from fastapi import Body, FastAPI, Form, HTTPException, Query
from typing import Annotated, List
from xml.etree import ElementTree as ET
#import server.zeep as zeep
#from server.zeep import xsd
from flask import jsonify, request
import zeep
import json
from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import base64
from datetime import datetime , timedelta, date
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import zeep.exceptions
from zeep.exceptions import Fault
from sql.models import CRUD
import mysql.connector
import numpy as np
import pandas as pd

from datetime import datetime

from ConnectOdooFramework import createOdoo
from createOdoo import createOdoo
from createAdherentOdoo import createAdherentOdoo
from createOdooGesica import createOdooGesica
from sql.connexion import recupere_connexion_db


# Chargement des variables d'environnement
load_dotenv()

#Récupération des variables d'environnement
WSDL_URL = os.getenv('MY_URCOOPA_URL')
API_KEY_URCOOPA = os.getenv('API_KEY_URCOOPA')
API_KEY_JOUR_FACTURES = os.getenv('API_KEY_JOUR_FACTURES')
#API_KEY_DATE_REFERENCE = os.getenv('API_KEY_DATE_REFERENCE')

# Vérification des variables requises
if not all([WSDL_URL, API_KEY_URCOOPA]):
    raise ValueError("Toutes les variables d'environnement (WSDL_URL et API_KEY_URCOOPA) doivent être définies.")

client = zeep.Client(wsdl=WSDL_URL)  # on crée le client

app = FastAPI()

# Monter les fichiers statiques à l'URL /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dossier templates
templates = Jinja2Templates(directory="templates")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplacez par l'URL de votre front-end
    allow_credentials=True,
    allow_methods=["*"],  # Méthodes HTTP autorisées
    allow_headers=["*"],  # En-têtes autorisés
)

# ---------------------
# 0. 📦 Connexion à mysql
# ---------------------
print('📤[INFO] Début connexion MYSQL')

connexion_base_de_donnees = recupere_connexion_db()

print('🌐 connexion mysql => ', connexion_base_de_donnees.is_connected)

# ---------------------
# 0. 📦 Connexion à la commande Odoo
# ---------------------

print('📤[INFO] Début connexion odoo')
from collections import defaultdict
import xmlrpc.client
            
# Paramètres
url = os.getenv('URL_ODOO')
db = os.getenv('DB_ODOO')
username = os.getenv('USERNAME_ODOO')
password = os.getenv('PASSWORD_ODOO')

# Authentification
info = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')

uid = info.authenticate(db, username, password, {})
#uid = ''info.authenticate(db, username, password, {})
    
if not uid:
    print('*'*50)
    print("[ERREUR]❌ Échec de l'authentification.")
    print('*'*50)
    
if uid:   
    print(f"✅ Authentification réussie. UID: {uid} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} \n\n")
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

date_end = datetime.now() # on recupere la date maintenant (int)
#date_start = date_end - timedelta(days=5) # on soustrait 2jours (int)
date_start = date_end - timedelta(days=int(os.getenv('DATE_JOUR_FACTURES'))) # on soustrait 2jours (int)
#dateReferenceFacture = date_start.strftime('%Y-%m-%d')
dateReferenceFacture = date_end.strftime('%Y-%m-%d')

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

######## HOME / RACINE
@app.get('/', response_class=HTMLResponse)
def home(request : Request):
    try: 
        print('🌐 init home')
        
        crud = CRUD()
        
        factures = crud.readFiltreAdherent()
        avoirs = crud.readFiltreAdherentAvoir()
        
        # Récupération des données comptables pour le mois en cours
        donnees_comptables = crud.readDonneesComptables()
        
        # Convert date objects to strings
        def convert_dates(data_list):
            for item in data_list:
                for key, value in item.items():
                    if isinstance(value, (date, datetime)):
                        item[key] = value.isoformat()
            return data_list

        factures = convert_dates(factures)
        avoirs = convert_dates(avoirs)
        
        for row in factures:
            print(row.get('date_validation'))
        
        # si vide []
        if len(factures) == 0:
            return templates.TemplateResponse( 
                                        'index.html', 
                                        { 
                                            'request' : request,
                                            'tous_factures_adherent_regroupe' : '' ,
                                            "total_ht": '0',
                                            "total_ttc": '0',
                                            #'adherent_null' : regroupe_non_adherent,
                                            "year": datetime.now().year,
                                            'donnees_comptables': donnees_comptables
                                        })
        
        else: 
            return templates.TemplateResponse( 
                                        'index.html', 
                                        { 
                                            'request' : request,
                                            'FACTURES' : factures ,
                                            'AVOIRS' : avoirs ,
                                            "total_ht": '0',
                                            "total_ttc": '0',
                                            #'adherent_null' : regroupe_non_adherent,
                                            "year": datetime.now().year,
                                            'donnees_comptables': donnees_comptables
                                        })
        
    except mysql.connector.Error as erreur:
        print(f'Erreur lors de la connexion à la base de données : {erreur}')
        return {"Erreur connexion Base de données : {erreur}"}
    '''
    return templates.TemplateResponse(
        'index.html', 
        {
            "request" : request, 
            'title' : 'Accueil',
            'year' : datetime.now().year
        })
    '''


######## API pour données comptables par mois
@app.get('/api/donnees-comptables/{annee}/{mois}')
def get_donnees_comptables_mois(annee: int, mois: int):
    try:
        crud = CRUD()
        
        # Construire les dates de début et fin du mois
        date_debut = f"{annee}-{mois:02d}-01"
        
        # Calculer le dernier jour du mois
        if mois == 12:
            date_fin = f"{annee + 1}-01-01"
        else:
            date_fin = f"{annee}-{mois + 1:02d}-01"
        
        donnees = crud.readDonneesComptables(date_debut, date_fin)
        print('CHOIX MOIS => ', donnees)
        
        return {
            "success": True,
            "data": donnees,
            "periode": f"{annee}-{mois:02d}"
        }
        
    except Exception as e:
        print(f"Erreur lors de la récupération des données comptables : {e}")
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

######## API pour données adherent par mois
@app.get('/api/donnees-adherent')
def get_donnees_adherent(annee: int, mois: int):
    try:
        crud = CRUD()
        
        # Construire la data base pour recuperer les infos sur tous les adherents 
        db  = recupere_connexion_db()
        cursor  = db.cursor(dictionary=True)
        
        requete  = '''
                SELECT DISTINCT Type_Client
                from exportodoo.sic_urcoopa_facture
            '''     
        
        # Execute la requête
        cursor.execute(requete,)
        datas = cursor.fetchall()
        
        # datas matcher avec odoo
        '''
        SELECT DISTINCT name
        FROM exportodoo.res_partner;
        '''
        
        return {
            "success": True,
            "data": datas,
            "periode": f"{annee}-{mois:02d}"
        }
        
    except Exception as e:
        print(f"Erreur lors de la récupération des données comptables : {e}")
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

'''
#GET COMMANDES DEPUIS GESICA
@app.get('/Commandes_Gesica')
async def get_commandes_gesica():
    
    try:
        crud = CRUD()
        resultat = await crud.readAll()
        purchase = defaultdict(list)

        for index, row in enumerate(resultat):
            #print(f'\n Boucle => {index + 1} \n')
            purchase[row["ENOCOM"]].append(row)

        max_factures = 2
        for i, (numero_facture, lignes) in enumerate(purchase.items()):
            print(f'📦 Traitement de la facture {numero_facture} contenant {len(lignes)} lignes')

            if i >= max_factures:
                print(f"🔔 Limite atteinte ({max_factures} factures). Arrêt du traitement.")
                break
            
            # Appel à createOdooGesica pour construire la commande
            commande_odoo = await createOdooGesica(
                lignes, models, db, uid, password
            )

            print('commande odoo', commande_odoo)
            if commande_odoo:
                
                try:
                    move_id = models.execute_kw(
                        db, uid, password,
                        'purchase.order', 'create',
                        [commande_odoo]
                    )
                    print(f"✅📤 Commande Odoo créée avec ID {move_id} pour facture {numero_facture}")
                except xmlrpc.client.Fault as e:
                    print(f"❌ Erreur XML-RPC Odoo : {e.faultString}")
                    
        #print('RETOUR PURCHASE ', purchase)
        return JSONResponse(content={"message": "Import terminé avec succès."}, status_code=200)

    except Exception as e:
        print(f'ERREUR: {e}')
        raise HTTPException(status_code=500, detail=str(e))
'''

### GET FACTURES ANCIEN API
@app.get('/ancien_api_recupere_factures')
async def get_Factures_Sicalait(xCleAPI=API_KEY_URCOOPA,nb_jours=API_KEY_JOUR_FACTURES):
    
    print("🌐 INIT : Démarrage du service get_factures...")
    
    link_wsdl = os.getenv('MY_URCOOPA_URL_ANCIEN')
    client = zeep.Client(wsdl=link_wsdl)  # on crée le client
    
    response = client.service.Get_Factures_Sicalait(xCleAPI=xCleAPI, NbJours=nb_jours)
    
    #print(response) 
    factures= json.loads(response)
    
    # boucles sur factures pour recuperer les datas json
    crud = CRUD()
    
    #boucle 
    for facture in factures:
        #filtre adherent
        #if facture.get('Type_Client') == 'ADHERENT':
            # verification dans sql
            numero_facture = facture.get('Numero_Facture')
            numero_ligne_facture = facture.get('Numero_Ligne_Facture')
            resultat = await crud.read_factures_ancien_api(numero_facture, numero_ligne_facture)
            
            # si vide on creer
            if resultat == None:
                await crud.create_facture_ancien_api(facture)
                print(f'[SUCESS] FACTURE N°{numero_facture} AJOUTER')
                
            else:
                print(f'[INFO] N°:{numero_facture} FACTURE DEJA EXISTANT')
        #else:
        #    print('❌[INFO] NON ADHERENT')
    return JSONResponse(content='[SUCCESS] FACTURE AJOUTER BASE DE DONNEES', status_code=200)

### GET LIVRAISONS
@app.get("/recupere_livraison/")
async def get_livraison(
    xCleAPI: str = API_KEY_URCOOPA, 
    nb_jours: int = API_KEY_JOUR_FACTURES, 
    dateReference: date = dateReferenceFacture):
    
    try:
        print("🌐 INIT : Démarrage du service get_factures...")
        print('date : ', dateReference)
        
        response = client.service.Get_Livraisons(xCleAPI=xCleAPI, NbJours=nb_jours, DateReference=dateReference)
        
        if not response:
            raise HTTPException(status_code=404, detail="Aucune facture trouvée.")
        
        factures = json.loads(response)
        #print(factures)
        
        # boucles sur factures pour recuperer les datas json
        crud = CRUD()
        
        #on utilise un dictionnaire{} au lieu d'une liste[]
        Urcoopa = []
        
        #on modifie les données pour uploader
        for key, value in factures.items():
            #print('KEY -> ', json.dumps(key, indent=2))
            for row in value:
                #print('VALUE -> ', json.dumps(row['Numero_BL'], indent=2))
                if row.get('Detail') is not None:
                    # on fais un boucle dans Détail
                    for article in row.get('Detail') :
                        #print('ARTICLE -> ', json.dumps(article, indent=2))
                        Urcoopa.append(
                            {
                                "Numero_BL": row.get("Numero_BL"),
                                "Code_Client": row.get("Code_Client"),
                                "Nom_Client": row.get("Nom_Client"),
                                "Date_BL": row.get("Date_BL"),
                                "Code_Adresse": row.get("Code_Adresse"),
                                "Libelle_Adresse": row.get("Libelle_Adresse"),
                                "Rue": row.get("Rue"),
                                "Lieu": row.get("Lieu"),
                                "Code_Postal": row.get("Code_Postal"),
                                "Ville": row.get("Ville"),

                                "Numero_Ligne_BL": article.get("Numero_Ligne_BL"),
                                "Code_Produit": article.get("Code_Produit"),
                                "Libelle_Produit": article.get("Libelle_Produit"),
                                "Quantite_Livree": article.get("Quantite_Livree"),
                                "Silo": article.get("Silo"),
                                "Transporteur": article.get("Transporteur"),
                                "Depot_Commande": article.get("Depot_Commande"),
                                "Numero_Commande": article.get("Numero_Commande"),
                                "Numero_Ligne_Commande": article.get("Numero_Ligne_Commande"),
                                "Numero_Facture": article.get("Numero_Facture"),
                                "Numero_Bande": article.get("Numero_Bande")
                            }
                        )
                else :
                    print("[ERREUR] The list is None, cannot iterate.")
                    break
                    
        #print(json.dumps(Urcoopa, indent=2))

        #fin travaux des données pret a uploader sur SQL et ODOO
        #on fais une boucle sur urcoopa[]
        from collections import defaultdict

        # Grouper les lignes par numéro de facture
        factures_groupees = defaultdict(list)
        for row in Urcoopa:
            factures_groupees[row['Numero_BL']].append(row)

        # Traiter facture par facture
        for numero_facture, lignes_a_traiter in factures_groupees.items():
            print(f"[INFO] Traitement facture {numero_facture}")
            
            ligne = int()
            for ligne_premier in lignes_a_traiter:
                ligne = ligne_premier['Numero_Ligne_BL']
                
            try :
                # Verification numéro facture et ligne facture exist
                resultat = await crud.read_livraison(numero_facture, ligne)
                #print(resultat)
            except:
                print('ERREUR RESULTAT : ',resultat)
                        
            if resultat == None :
                # Facture n'existe pas, créer toutes les lignes
                for row in lignes_a_traiter:
                    #print('dans ',resultat)
                    #print('dans row ', row)
                    
                    cnx = recupere_connexion_db()
                    cursor = cnx.cursor()
                    
                    nameChamps = '''
                    SELECT distinct COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'sic_urcoopa_livraison' and COLUMN_KEY<>'PRI';
                    '''

                    cursor.execute(nameChamps)
                    dataName = cursor.fetchall()
                    
                    columnChamp = []
                    for colonne in dataName:
                        columnChamp.append(colonne[0])
                    

                    # Filtrer les données de 'row' pour ne garder que les colonnes existantes
                    valeurs_filtrees = []
                    colonnes_utilisees = []
                    
                    for colonne in columnChamp:
                        if colonne in row:
                            valeurs_filtrees.append(row[colonne])
                            colonnes_utilisees.append(colonne)
                        else:
                            # Optionnel: ajouter une valeur par défaut (NULL)
                            valeurs_filtrees.append(None)
                            colonnes_utilisees.append(colonne)
                    
                    # Construire la requête d'insertion
                    colonnes_str = ', '.join(colonnes_utilisees)
                    placeholders = ', '.join(['%s'] * len(valeurs_filtrees))
                    
                    insert_query = f'''
                        INSERT INTO exportodoo.sic_urcoopa_livraison ({colonnes_str})
                        VALUES ({placeholders})
                    '''
                    
                    #print('Requête SQL:', insert_query)
                    #print('Valeurs:', valeurs_filtrees)
                    
                    # Exécuter l'insertion
                    cursor.execute(insert_query, tuple(valeurs_filtrees))
                    cnx.commit()
                    
                    cursor.close()
                    
                    #resultat_create = await crud.create_facture_ancien_api(row)
                    #print(f'[INFO] Message : {resultat_create}')
                    #print(f'[INFO] Message ')
                    print(f'✅ Ligne {row.get("Numero_Ligne_BL")} créée pour nouvelle facture {numero_facture}')
                    
            else : 
                print(f'ℹ️ Ligne {ligne} existe déjà dans la facture {numero_facture}')
                
        
        return factures
    
    except Exception as e:
        print('ERREUR CONNEXION ', e)


### FACTURES
@app.get("/Recupere_Factures/")
async def get_factures(
    xCleAPI: str = API_KEY_URCOOPA, 
    nb_jours: int = API_KEY_JOUR_FACTURES, 
    dateReference: date = dateReferenceFacture): # format YYYY-MM-DD
    
    try:
        print("🌐 INIT : Démarrage du service get_factures...")
        print('date : ', dateReference)
        
        response = client.service.Get_Factures(xCleAPI=xCleAPI, NbJours=nb_jours, DateReference=dateReference)
        
        if not response:
            raise HTTPException(status_code=404, detail="Aucune facture trouvée.")
        
        #Debug: Print the type and content of response
        #print(f"Response type: {type(response)}")
        #print(f"Response content: {response}")
        
        factures = json.loads(response)
        #print(factures)
        
        # boucles sur factures pour recuperer les datas json
        crud = CRUD()
        
        Adherent = []
        #on utilise un dictionnaire{} au lieu d'une liste[]
        numeros_facture_enregistrer = {}
        Urcoopa = []
        facture_odoo = []
        
        #on modifie les données pour uploader
        for key, value in factures.items():
            
            for row in value:
                
                #print('*'*50)
                #print(json.dumps(row, indent=2))
                #print('*'*50)
                facture_odoo.append(row)

                # on fais un boucle dans Détail
                for article in row.get('Detail') :
                    
                    Urcoopa.append(
                        {
                            'Numero_Facture' : row.get('Numero_Facture'),
                            'Type_Facture' : row.get('Type_Facture'),
                            'Date_Facture' : row.get('Date_Facture'),
                            'Date_Echeance' : row.get('Date_Echeance'),
                            'Societe_Facture' : row.get('Societe_Facture'),
                            'Code_Client' : row.get('Code_Client'),
                            'Nom_Client' : row.get('Nom_Client'),
                            'Type_Client': row.get('Type_Client'),
                            'Montant_HT': row.get('Montant_HT'),
                            'Montant_TTC': row.get('Montant_TTC'),
                            "Numero_Ligne_Facture": article.get('Numero_Ligne_Facture'),
                            "Code_Produit": article.get('Code_Produit'),
                            "Libelle_Produit": article.get('Libelle_Produit'),
                            "Prix_Unitaire": article.get('Prix_Unitaire'),
                            "Quantite_Facturee": article.get('Quantite_Facturee'),
                            "Unite_Facturee": article.get('Unite_Facturee'),
                            "Numero_Silo": article.get('Numero_Silo'),
                            "Montant_HT_Ligne": article.get('Montant_HT_Ligne'),
                            "Taux_TVA": article.get('Taux_TVA'),
                            "Depot_BL": article.get('Depot_BL'),
                            "Numero_BL": article.get('Numero_BL'),
                            "Numero_Ligne_BL": article.get('Numero_Ligne_BL'),
                            "Numero_Commande_Client": article.get('Numero_Commande_Client'),
                            "Date_Commande_Client": article.get('Date_Commande_Client'),
                            "Commentaires": article.get('Commentaires'),
                            "Date_Livraison": article.get('Date_Livraison'),
                        }
                    )
        
        #fin travaux des données pret a uploader sur SQL et ODOO
        #on fais une boucle sur urcoopa[]
        from collections import defaultdict

        # Grouper les lignes par numéro de facture
        factures_groupees = defaultdict(list)
        for row in Urcoopa:
            factures_groupees[row['Numero_Facture']].append(row)

        # Traiter facture par facture
        for numero_facture, lignes_a_traiter in factures_groupees.items():
            print(f"[INFO] Traitement facture {numero_facture}")
            
            ligne = int()
            for ligne_premier in lignes_a_traiter:
                ligne = ligne_premier['Numero_Ligne_Facture']
                
            try :
                # Verification numéro facture et ligne facture exist
                resultat = await crud.read(numero_facture, ligne)
                #print(resultat)
            except:
                print('ERREUR RESULTAT : ',resultat)
                        
            if resultat == None :
                # Facture n'existe pas, créer toutes les lignes
                for row in lignes_a_traiter:
                    #print('dans ',resultat)
                    #print('dans row ', row)
                    
                    cnx = recupere_connexion_db()
                    cursor = cnx.cursor()
                    
                    nameChamps = '''
                    SELECT distinct COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'sic_urcoopa_facture_ancien_api' and COLUMN_KEY<>'PRI';
                    '''

                    cursor.execute(nameChamps)
                    dataName = cursor.fetchall()
                    
                    columnChamp = []
                    for colonne in dataName:
                        columnChamp.append(colonne[0])
                    

                    # Filtrer les données de 'row' pour ne garder que les colonnes existantes
                    valeurs_filtrees = []
                    colonnes_utilisees = []
                    
                    for colonne in columnChamp:
                        if colonne in row:
                            valeurs_filtrees.append(row[colonne])
                            colonnes_utilisees.append(colonne)
                        else:
                            # Optionnel: ajouter une valeur par défaut (NULL)
                            valeurs_filtrees.append(None)
                            colonnes_utilisees.append(colonne)
                    
                    # Construire la requête d'insertion
                    colonnes_str = ', '.join(colonnes_utilisees)
                    placeholders = ', '.join(['%s'] * len(valeurs_filtrees))
                    
                    insert_query = f'''
                        INSERT INTO exportodoo.sic_urcoopa_facture ({colonnes_str})
                        VALUES ({placeholders})
                    '''
                    
                    #print('Requête SQL:', insert_query)
                    #print('Valeurs:', valeurs_filtrees)
                    
                    # Exécuter l'insertion
                    cursor.execute(insert_query, tuple(valeurs_filtrees))
                    cnx.commit()
                    
                    cursor.close()
                    
                    #resultat_create = await crud.create_facture_ancien_api(row)
                    #print(f'[INFO] Message : {resultat_create}')
                    #print(f'[INFO] Message ')
                    print(f'✅ Ligne {row.get("Numero_Ligne_Facture")} créée pour nouvelle facture {numero_facture}')
                    
            else : 
                print(f'ℹ️ Ligne {ligne} existe déjà dans la facture {numero_facture}')
                
        # PROCEDURE URCOOPA PREPA FACTURES
        # LANCER PROCEDURE
        try :
            print('Procédure lancer MAJ SQL lancé!')
            cnx = recupere_connexion_db()
            cursor = cnx.cursor()

            # Appel de la procédure stockée
            cursor.callproc("exportodoo.URCOOPA_PREPA_FACTURES")
            cnx.commit()
            #cursor.execute('{ CALL exportodoo.URCOOPA_PREPA_FACTURES() }')
            
            # Récupérer les résultats de la procédure
            for result in cursor.stored_results():
                data = result.fetchall()

            cursor.close()
            cnx.close()
            print ('✅ Message mise à jour procédure SQL: ', data[0])
        except Exception as e: 
            print('[ERREUR] PROCEDURE :', e)
        # QUAND TOUS DATAS EST DANS SQL ON TRAITE DE SUITE POUR ODOO
        # en creant un JSON
        #return JSONResponse(content={'message' : 'SUCCESS'})
        # Ajout ODOO debut
        '''
        try :
            print('✅ [SUCCESS] Fin ajout facture bdd')
            print('📤[INFO] Début ajout facture Odoo')
            
            # Construction JSONs
            factures_json = []
            
            for numero_facture, lignes in factures_groupees.items():
                # On filtre : ne traiter que les lignes NON ADHERENT
                lignes_filtrées = [row for row in lignes if row.get("Type_Client") != "ADHERENT"]

                if lignes_filtrées:
                    # Appel unique à createOdoo avec toutes les lignes de cette facture
                    #await createOdoo(lignes_filtrées,models, db, uid, password)
                    from testcreateOdoo import testcreateOdoo
                    await testcreateOdoo(lignes_filtrées,models, db, uid, password)
                    
                    
                    ligne0 = lignes_filtrées[0]

                    invoice_lines = []
                    for ligne in lignes_filtrées:
                        product_id = ligne.get('Code_Produit_ODOO')
                        qty = ligne.get('Quantite_Facturee', 0)
                        price = ligne.get('Prix_Unitaire', 0)

                        # Ajout ligne produit
                        invoice_lines.append([0, 0, {
                            'product_id': product_id,
                            'quantity': qty,
                            'price_unit': price
                        }])

                    # Construction du dictionnaire de facture
                    facture = {
                        "move_type": "in_invoice",
                        "partner_id": ligne0.get('Code_Client'),
                        "invoice_partner_display_name": ligne0.get('Nom_Client'),
                        "ref": ligne0.get('Numero_Facture'),
                        "invoice_date": ligne0.get('Date_Facture'),
                        "invoice_date_due": ligne0.get('Date_Echeance'),
                        "invoice_line_ids": invoice_lines
                    }

                    #factures_json.append(facture)    
                        
                    #import json
                    print(f"📦 Facture creer pour Odoo : {ligne0['Numero_Facture']}")
                    print(json.dumps(facture, indent=2))
                    
                    # Envoi
                    try:
                        
                        move_id = models.execute_kw(
                            db, uid, password,
                            'account.move', 'create',
                            [facture]
                        )
                        
                        
                        models.execute_kw(
                            db, uid, password,
                            'account.move', 'write',
                            [move_id, {}]  # Un write vide peut déclencher les compute fields
                        )
                        
                        print(f"✅📤 [SUCCESS] Facture envoyer à Odoo ")
                        #print(f"✅📤 [SUCCESS] Facture Odoo créée avec ID {move_id} \n\n")
                    except xmlrpc.client.Fault as e:
                        #Retourne tous les erreur odoo
                        #Erreur odoo si facture existe sera retrouné
                        print(f"❌ Erreur Envoi XML-RPC Odoo : {e.faultString} \n\n")               
                
        except Exception as e:
            print(f'❌ Erreur insertion ligne : {e}')
        
        print('✅📤 [SUCCESS] IMPORT FACTURE URCOOPA EFFECTUE !')
        return JSONResponse(content=facture_odoo, status_code=200 )
        ''' '''
        return facture_odoo
        if numeros_facture_enregistrer:
            
            try:
                #print('URCOOPA', numeros_facture_enregistrer)
                print('✅ [SUCCESS] Fin ajout facture bdd')
                print('📤[INFO] Début ajout facture Odoo')
                
                
                factures_groupées = defaultdict(list)

                #for row in numeros_facture_enregistrer:
                #    factures_groupées[row["Numero_Facture"]].append(row)

                for numero_facture, lignes in numeros_facture_enregistrer.items():
                    # On filtre : ne traiter que les lignes NON ADHERENT
                    lignes_filtrées = [row for row in lignes if row.get("Type_Client") != "ADHERENT"]
                    #print('-'*50)
                    #print('-'*50)
                    #print(json.dumps(lignes_filtrées, indent=2))
                    #for numero, articles in enumerate(lignes_filtrées):
                        
                        

                    if lignes_filtrées:
                        # Appel unique à createOdoo avec toutes les lignes de cette facture
                        await createOdoo(lignes_filtrées,models, db, uid, password )
                        
                        #print('[INFO] TEST REUSSI')
                        
            except Exception as e:
                print(f'❌ Erreur insertion ligne : {e}')

        
        print('✅📤 [SUCCESS] IMPORT FACTURE URCOOPA EFFECTUE !')
        return JSONResponse(content=Urcoopa, status_code=200 )       
        #return {"Messages": 'Récuperation factures urcoopa Ok !'}
        '''
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de décodage JSON.")
    except zeep.exceptions.Fault as fault:
        raise HTTPException(status_code=500, detail=f"Erreur SOAP : {fault}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

###############################
# AJOUT FACTURE ODOO
###############################

@app.get('/ajout-facture-odoo')
async def ajout_facture_odoo():
    print('[INFO] 🌐 init ajout facture odoo')
    
    cnx = recupere_connexion_db()
    cursor  = cnx.cursor(dictionary=True)
    
    requete = 'SELECT * FROM exportodoo.sic_urcoopa_facture'
    cursor.execute(requete)
    datas = cursor.fetchall()
    
    factures_groupees = defaultdict(list)
    
    for row in datas:
        factures_groupees[row.get('Numero_Facture')].append(row)
    
    for numero_facture, lignes in factures_groupees.items():
        # On filtre : ne traiter que les lignes NON ADHERENT
        lignes_filtrées = [row for row in lignes if row.get("Type_Client") != "ADHERENT"]

        if lignes_filtrées:
            # Appel unique à createOdoo avec toutes les lignes de cette facture
            #await createOdoo(lignes_filtrées,models, db, uid, password)
            from testcreateOdoo import testcreateOdoo
            await testcreateOdoo(lignes_filtrées,models, db, uid, password)
    
    return JSONResponse(content='AJOUT FACTURE ODOO OK')

#PUSH FACTURES
@app.post("/envoyer-commande/")
async def post_commande():

    #try:
    print('[INFO] 🌐 init commande envoyer urcoopa')
    
    #filtre par date
    
    date_end = datetime.now() # on recupere la date maintenant (int)
    #date_start = date_end - timedelta(days=5) # on soustrait 2jours (int)
    date_start = date_end - timedelta(days=int(os.getenv('DATE_JOUR'))) # on soustrait 2jours (int)

    date_start_new = date_start.strftime('%Y-%m-%d 00:00:00') # date de départ strftime
    date_end_new = date_end.strftime('%Y-%m-%d 23:59:59') # date fin str

    commandes = models.execute_kw(
        db, uid, password,
        'purchase.order',
        #'search',
        'search_read',
        #'search_count',
        [[
            ['date_order', '>=', date_start_new], #depart Jours - 2
            ['date_order', '<=', date_end_new] # fin jours present
        ]],
        {
            #'limit' : 10,
            'order': 'id asc'
        }
    )
    
    #filtres 
    for commande in commandes:
        #print(commande.get('partner_id'), commande.get('state'))
        partner_urcoopa = commande.get('partner_id')
        
        #filtre par urcoopa
        if partner_urcoopa[1] != 'URCOOPA':
            print('[FAULT] ❌ FAUSSE ALERTE - NON URCOOPA ', partner_urcoopa , '\n')
            continue
            
        print('[SUCCESS] ✅  BINGO URCOOPA')      
        # ---------------------
        # 1. 📦 Récupérer la commande Odoo
        # ---------------------
        print('[INFO] 1. 📦 Récupération de la commande Odoo')
        commande_id = models.execute_kw(
            db, uid, password,
            'purchase.order', 'read',
            [[commande.get('id')]],  # filtre, sur le id de la commande
            {
                'fields' : ['name', 'partner_id', 'company_id', 'date_order', 'order_line', 'state']
                #'limit': 1,
                #'order': 'id desc'  # trie du plus grand ID au plus petit
            }
        )[0]
        #print("[INFO] 🆔 Dernier ID créé dans purchase.order :", commande_id)
        
        #FILTRES : commandes urcoopa uniquement
        #FILTRES : status : draft 
        if commande['partner_id'][1] == 'URCOOPA' and commande.get('state') == 'purchase':
            
            print('[INFO] 2. 📦 Récupérer le partner Odoo')
            partner = models.execute_kw(
                db, uid, password,
                'res.partner', 'read',
                [[commande['partner_id'][0]]],
                {'fields': ['name']}
            )[0]
            #print('[SUCCESS] ✅ Partner Odoo récupéré : ', partner)
            
            #recuperation info : login mail societe
            #print('COMMANDE : ', commande['user_id'])
            info_user = models.execute_kw(
                db, uid, password,
                #'purchase.order.line', 'search_read',      
                'res.company', 'search_read',
                [[[ 'id', '=', commande['user_id'][0] ]]],  # pas de filtre, on veut tout
                {
                    #'limit': 10,
                    #'order': 'id asc' , # trie du plus grand ID au plus petit
                    'fields' : ['name', 'email']
                }
            )[0]
            #print('[SUCCESS] ✅ info_user Odoo récupéré : ', info_user)
            
            shipping = models.execute_kw(db, uid, password,
                'res.partner', 'read', [[commande['partner_id'][0]]],
                {'fields': ['name']}
            )[0]
            
            #print('[SUCCESS] ✅ shipping Odoo récupéré', shipping )

            # Récupérer les lignes de la commande
            products = models.execute_kw(
                db, uid, password,
                'purchase.order.line', 'read',
                [commande['order_line']],
                {'fields': ['product_id', 'name', 'product_qty']}
            )
            print('[INFO] 📦 Produits récupéré')
            #print('[INFO] 📦 Voici les produits  : ', json.dumps(products, indent=2))

            commentaire = ''
            # ---------------------
            # 2. 🏗️ Construire le JSON à envoyer
            # ---------------------
            ligne_commande = []
            for i, ligne in enumerate(products):
                
                #conditions pour recupéré products s'il y a commentaire
                if not ligne['product_id']:
                    commentaire += f" - {ligne['name']} ;"
                    print('-> commentaire : ', commentaire)
                    continue
                
                product_id = ligne['product_id'][0]
                #print('-> product_id récupéré: ', product_id)
                
                # Récupérer le product_tmpl_id
                product_product = models.execute_kw(
                    db, uid, password,
                    'product.product', 'read',
                    [[product_id]],
                    {'fields': ['product_tmpl_id']}
                )[0]
                product_tmpl_id = product_product['product_tmpl_id'][0]
                #print('-> product_tmpl_id récupéré: ', product_tmpl_id)
                
                # Chercher les ids supplierinfo
                supplierinfo_ids = models.execute_kw(
                    db, uid, password,
                    'product.supplierinfo', 'search',
                    [[['product_tmpl_id', '=', product_tmpl_id]]]
                )
                #print('-> supplierinfo_ids récupéré: ', supplierinfo_ids)
                
                # Lire les infos product code à enlever si besoin
                product_code = 'N/A'
                if supplierinfo_ids:
                    
                    supplierinfo_data = models.execute_kw(
                        db, uid, password,
                        'product.supplierinfo', 'read',
                        [supplierinfo_ids],
                        {'fields': ['product_code']}
                    )
                    #if supplierinfo_data and supplierinfo_data[0].get('product_code'):
                    for row in supplierinfo_data:
                        if row['product_code']:
                            product_code = row['product_code']
                            #print('[INFO] Code supplierinfo_product_code récupéré :', product_code)
                            
                print('[INFO] Code fournisseur récupéré :', product_code)
                
                udm = models.execute_kw(db, uid, password, 
                'uom.uom', 
                'read', 
                [product_id],
                {
                    #'fields' : ['product_uom_id']
                    'fields' : ['name']
                }
                )[0]
                
                # Extrait code interne si besoin ( code dans crochets)
                code_interne = ligne['name'].split("]")[0].replace("[", "")
                
                ligne_commande.append({
                    "Numero_ligne": i + 1,
                    "Code_Produit": product_code,
                    "Libelle_Produit": ligne['name'],
                    "Quantite_Commandee": ligne['product_qty'],
                    "Unite_Commande": "UN",
                    #Quantite_Commandee
                    #Unite_Commande (valeurs attendues : "UN", "KG" ou "TO")
                })
            
            
            #print('[INFO] 📦 lignes produits Commandes final : ', json.dumps(ligne_commande, indent=2))
            print('[INFO] 📦 lignes produits Commandes final OK!')
            
            #on enleve gesica
            reference_partenaire = commande.get('partner_ref')
            
            if reference_partenaire:
                reference = reference_partenaire.replace('GESICA', "").strip()
            else :
                reference = commande.get('name').strip()
                
            #requete code client
            if not commande['company_id']:
                continue
            else:
                #print( '\n📤 [INFO] REQUETE SQL CODE COMPANY_ID ODOO : ', json.dumps( commande['company_id'][0], indent=2 ))
                code = commande['company_id'][0] 
                #print(json.dumps( commande, indent=2 ))          
                
                #requete sic_depot
                print('🌐 init SQL')
                connexion = recupere_connexion_db()
                # on recupere le cursor en dictionnaire
                cursorRequete = connexion.cursor(dictionary=True)
                
                # on execute la requete sur la table sic urcoopa facture where champs adherent
                requete = '''
                        SELECT * FROM sic_depot
                        WHERE company_id = %s
                '''
                
                code_urcoopa = ( code,)
                cursorRequete.execute(requete, code_urcoopa)
                
                # on recupere la requete
                datas = cursorRequete.fetchall()
                #print('✅ récupération datas ok !', datas)
                #print(json.dumps(datas, indent=2))
                
                if len(datas) == 0 or datas[0].get('code_urcoopa') is None:
                    code_client = "5010" #code par defaut
                    code_adresse_livraison = '01' #code par defaut
                    print('Code_Client :', code_client)
                
                else: 
                    #"Code_Client": "5024",
                    code_client = datas[0].get('code_urcoopa')
                    code_adresse_livraison = datas[0].get('code')
                
            commande_json ={ 
            'commande' :
                [
                    {
                        "Societe": "UR",
                        "Code_Client": code_client,
                        "Numero_Commande": reference,
                        "Nom_Client": json.loads(f'"{commande.get("picking_type_id")[1]}"'),
                        "Code_Adresse_Livraison": code_adresse_livraison,
                        "Commentaire": commentaire,
                        "Date_Livraison_Souhaitee": datetime.now().strftime('%Y%m%d'),
                        "Num_Telephone": info_user.get("phone", ""),
                        "Email": info_user.get("email", ""),
                        "Ligne_Commande": ligne_commande
                    }
                ]
            }
            
            
            # ---------------------
            # 3. 📤 Envoi via SOAP
            # ---------------------
            
            from testEnvoiAPI import send_soap
            print(commande_json)
            send_soap(WSDL_URL, API_KEY_URCOOPA, commande_json)
            
            
        else : 
            print(f'[FAULT] ❌ ZUT COMMANDE : {commande["name"]} TOUJOURS EN BROUILLON \n')    
    
    '''         
    except Fault as soap_err:
        print("❌ Erreur SOAP :", soap_err)
        #raise HTTPException(status_code=500, detail=str(soap_err))
    
    except Exception as e:
        print("❌ Erreur générale :", e)
        #raise HTTPException(status_code=500, detail=str(e))
    '''   
    ######################################################

#recuperation adherent dans base de données exportOdoo
@app.get('/factureAdherentUrcoopa', response_class=HTMLResponse)
async def getFactureAdherentUrcoopa( request : Request ):
    try: 
        print('🌐 init')
        #connexion base de données
        connexion = mysql.connector.connect(
            host = '172.17.240.18',#host,
            port='3306',
            database= 'exportodoo', #dbname 
            user='root', #user
            password='S1c@l@1t'
        )
        print('🌐 connexion', connexion)
        # on recupere le cursor en dictionnaire
        cursorRequete = connexion.cursor(dictionary=True)
        
        # on execute la requete sur la table sic urcoopa facture where champs adherent
        requete = '''
                SELECT * FROM sic_urcoopa_facture
                WHERE Type_Client = 'ADHERENT'
                ORDER BY Nom_Client ASC
        '''
        cursorRequete.execute(requete,)
        
        # on recupere la requete
        datas = cursorRequete.fetchall()
        print('✅ récupération datas ok !')
        
        query  = '''
                SELECT
                f.Numero_Facture,
                f.Type_Facture,
                f.Date_Facture,
                f.Date_Echeance,
                f.Societe_Facture,
                f.Code_Client,
                f.Nom_Client,
                f.Type_Client,
                f.Montant_HT,
                f.Montant_TTC,
                f.Numero_Ligne_Facture,
                f.Code_Produit,
                f.Libelle_Produit,
                f.Prix_Unitaire,
                f.Quantite_Facturee,
                f.Unite_Facturee,
                f.Numero_Silo,
                f.Montant_HT_Ligne,
                f.Taux_TVA,
                f.Depot_BL,
                f.Numero_BL,
                f.Numero_Ligne_BL,
                f.Commentaires,
                f.Numero_Commande_Client,
                f.Date_Commande_Client,
                f.Numero_Commande_ODOO,
                f.Code_Produit_ODOO,
                f.ID_Produit_ODOO,
                f.Code_Client_ODOO,
                f.ID_Client_ODOO,
                f.Societe_Facture_ODOO,
                f.ID_Facture_ODOO,
                p.id
                FROM exportodoo.sic_urcoopa_facture f
                left join exportodoo.res_partner p
                on f.Nom_Client = p.name
                where Type_Client ='ADHERENT'
                ORDER BY Nom_Client ASC
        '''
        cursorRequete.execute(query,)
        
        # on recupere la requete
        adherent_null = cursorRequete.fetchall()
        print('✅ récupération adherent_null ok !')
        
        #on ferme la connexion
        cursorRequete.close()
        connexion.close()
        
        # ✅ Calcul des totaux côté serveur
        total_ht = sum(f["Montant_HT"] for f in datas)
        total_ttc = sum(f["Montant_TTC"] for f in datas)
        
        #filtre somme client
        df = pd.DataFrame(datas)
        regroupe = df.groupby(['Code_Client', 'Nom_Client' ])[['Montant_HT', 'Montant_TTC']].sum().reset_index()
        regroupé_dicts = regroupe.to_dict(orient='records')
        
        #print(regroupé_dicts)
        
        
        
        # affiche uniquement les adherent_nul
        facture_adherent_null = []
        for row in adherent_null:
            
            if row.get('id') == None:
                facture_adherent_null.append(row)
        
        df = pd.DataFrame(facture_adherent_null)
        regroupe_non_adherent = df.groupby(['Code_Client', 'Nom_Client' ])[['Montant_HT', 'Montant_TTC']].sum().reset_index()
        regroupe_non_adherent = regroupe_non_adherent.to_dict(orient='records')
        
        #print(regroupe_non_adherent)
        #return JSONResponse(content=regroupé_dicts)
        
        
        return templates.TemplateResponse( 
                                        'factures.html', 
                                        { 
                                            'request' : request,
                                            'factures' : regroupé_dicts ,
                                            "total_ht": total_ht,
                                            "total_ttc": total_ttc,
                                            'adherent_null' : regroupe_non_adherent,
                                            "year": datetime.now().year
                                        })
        
        
    except mysql.connector.Error as erreur:
        print(f'Erreur lors de la connexion à la base de données : {erreur}')
        return {"Erreur connexion Base de données : {erreur}"}
    
    
# POST HOME SITE RACINE BOUTON VALID
@app.post("/valider-facture/{numero_facture}", response_class=HTMLResponse)
async def valider_facture(
    request: Request,
    numero_facture: int,
):
    
    #connexion sql
    print(' 🌐 init connexion sql valider-facture')
    print('Numeros => ',numero_facture)
    
    crud = CRUD()
    response = await crud.updateFacture(numero_facture)
    
    print('RESPONSE UPDATE -> ',response)
    if response != None:
        print('[ERREUR] => update')
    # rediriger, stocker, ou afficher une page de confirmation
    return templates.TemplateResponse("confirmation.html", 
    {
        "request": request,
        "numero_facture": numero_facture,
        "code_client": '0.00',
        "montant_ht": '0.00'
    })
    
    #connexion base de données
    connexion = mysql.connector.connect(
            host = '172.17.240.18',#host,
            port='3306',
            database= 'exportodoo', #dbname 
            user='root', #user
            password='S1c@l@1t'
        )
    print('🌐 connexion', connexion)
    # on recupere le cursor en dictionnaire
    cursorRequete = connexion.cursor(dictionary=True)
    
    requete = '''
                update sic_urcoopa_facture
                set Numero_Facture = '%s'
                where Numero_Facture = '%s'
        '''
    new_numero_facture = 'val'+numero_facture
    datas = (new_numero_facture, numero_facture)
    cursorRequete.execute(requete,datas,)
    connexion.commit()
    # utiliser les données ici
    print(f"Facture {numero_facture} validée pour le client {code_client} - ht : {montant_ht}€ - ttc : ")

    # rediriger, stocker, ou afficher une page de confirmation
    return templates.TemplateResponse("confirmation.html", {
        "request": request,
        "numero_facture": numero_facture,
        "code_client": code_client,
        "montant_ht": montant_ht
    })

#POST HOME SITE RACINE VERS ODOO
@app.post('/create_facture_adherent_odoo', response_class=JSONResponse)
async def create_facture_adherent_odoo(request: Request):
    facture_adherent = await request.json()  # <-- lit le JSON envoyé dans le body
    #print("📦 JSON reçu :", json.dumps(facture_adherent, indent=2))
    print("📦 JSON reçu ")
    
    #on groupe les lignes par numéros facture
    facture_groupé = defaultdict(list)

    for ligne in facture_adherent:
        numero = ligne.get("Numero_Facture")
        facture_groupé[numero].append(ligne)
        
    print('📤[INFO] Début ajout facture Odoo')
    for numero_facture, lignes in facture_groupé.items():
        # On filtre : ne traiter que les lignes NON ADHERENT
        lignes_filtrées = [row for row in lignes]

        if lignes_filtrées:
                    # Appel unique à createOdoo avec toutes les lignes de cette facture
                    return await createAdherentOdoo(lignes_filtrées,models, db, uid, password )

                    if result :
                        return result

    # Affichage propre
    #print("📦 JSON REGROUPE :", json.dumps(facture_groupé, indent=2, ensure_ascii=False))


    # tu peux ensuite utiliser facture_adherent['Numero_Facture'], etc.
    return JSONResponse(content={"message": "Facture adhérent créée dans Odoo"})



# Modèle Pydantic pour la validation des données
class ValidationRequest(BaseModel):
    factures: List[str]
    totalHT: float
    totalTTC: float
#POST VALIDER TOUTES LES FACTURES
@app.post('/valider-toutes-factures', response_class=JSONResponse)
async def valider_toutes_factures(request: Request):
    try:
        # Récupérer les données JSON du body
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        
        db = recupere_connexion_db()
        cursor = db.cursor()
        
        factures = data.get('factures', [])
        total_ht = data.get('totalHT', 0)
        total_ttc = data.get('totalTTC', 0)
        
        if not factures:
            return JSONResponse(
                status_code=400,
                content={
                    'success': False,
                    'message': 'Aucune facture à valider'
                }
            )
        
        factures_validees = 0
        
        # Valider toutes les factures
        for numero_facture in factures:
            cursor.execute("""
                UPDATE sic_urcoopa_facture 
                SET facture_valider = 1, 
                    date_validation = NOW()
                WHERE Numero_Facture = %s AND (facture_valider IS NULL OR facture_valider = 0)
            """, (numero_facture,))
            
            if cursor.rowcount > 0:
                factures_validees += 1
        
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                'success': True,
                'message': f'{factures_validees} factures validées avec succès',
                'total_ht': round(total_ht, 2),
                'total_ttc': round(total_ttc, 2),
                'factures_validees': factures_validees
            }
        )
        
    except Exception as e:
        if 'db' in locals():
            db.rollback()
            
        return JSONResponse(
            status_code=500,
            content={
                'success': False,
                'message': f'Erreur: {str(e)}'
            }
        )
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()


from crontab import CronTab
def init_cron():
    # Récupération de la planification via variable d'environnement
    #cron_schedule = os.getenv('CRONTAB_APP', '30 14 * * *')
    cron_schedule = os.getenv('CRONTAB_APP_FACTURES')
    cron_schedule2 = os.getenv('CRONTAB_APP_COMMANDES')

    # Initialisation du cron pour l'utilisateur root
    #cron = CronTab(user='root')
    cron = CronTab(user='jimmy')
    cron.remove_all()
    cron.write()

    # Définition de la commande
    job = cron.new(command=f'curl http://0.0.0.0:9898/recupere_Factures/?xCleAPI={API_KEY_URCOOPA}&nb_jours={API_KEY_JOUR_FACTURES}&dateReference={dateReferenceFacture}')
    job2 = cron.new(command=f'curl -X POST http://0.0.0.0:9898/envoyer-commande/')
    job.setall(cron_schedule)
    job2.setall(cron_schedule2)
    cron.write()

    # Lancement du service cron
    #print(f"✅ CRON configuré avec la planification : {cron_schedule1} et {cron_schedule2}")
    print(f"✅ CRON configuré avec la planification factures: {cron_schedule} ")
    print(f"✅ CRON configuré avec la planification commandes: {cron_schedule2} ")
    print("✅ Démarrage du service CRON...")
    os.system('service cron start')
    print("✅ Service CRON lancé avec succès.")

#init_cron()

if __name__ == "__main__":
    
    
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=9898,
        #ssl_certfile="server.crt",
        #ssl_keyfile="server.key"
        )
