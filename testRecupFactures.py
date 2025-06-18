from dotenv import load_dotenv
from zeep import Client
import os
from fastapi import FastAPI, Form, HTTPException
import json

from sql.models import CRUD

# Chargement des variables d'environnement
load_dotenv()

#Récupération des variables d'environnement
WSDL_URL = os.getenv('MY_URCOOPA_URL')
API_KEY_URCOOPA = os.getenv('API_KEY_URCOOPA')
API_KEY_JOUR = os.getenv('API_KEY_JOUR')

# Vérification des variables requises
if not all([WSDL_URL, API_KEY_URCOOPA]):
    raise ValueError("Toutes les variables d'environnement (WSDL_URL et API_KEY_URCOOPA) doivent être définies.")

client = Client(wsdl=WSDL_URL)  # on crée le client

print("🌐 INIT : Démarrage du service get_factures...")
        
response = client.service.Get_Factures_Sicalait(xCleAPI=API_KEY_URCOOPA, NbJours=30)

if not response:
    raise HTTPException(status_code=404, detail="Aucune facture trouvée.")

factures = json.loads(response)

# boucles sur factures pour recuperer les datas json
crud = CRUD()

Adherent = []
Urcoopa = []

#on utilise un dictionnaire au lieu d'une liste[]
numeros_facture_enregistrer = {}

for row in factures:
    numero_facture = row.get('Numero_Facture')
    
    # si numeros facture est dans numeros facture enregistrer
    if numero_facture in numeros_facture_enregistrer:
        print('-' * 50)
        print(f'[INFO] NUMERO DETECTE - : {numero_facture}')
        numeros_facture_enregistrer[numero_facture].append(row)
        print(f"Maintenant {len(numeros_facture_enregistrer[numero_facture])} occurrences pour ce numéro")
        print(row)
        print('-' * 50,'\n')
    
    else : 
        numeros_facture_enregistrer[numero_facture] = [row]
        
# CORRECTION ICI : Boucler sur chaque ligne de chaque facture
for numero_facture, lignes_factures in numeros_facture_enregistrer.items():
    print(f'📄 Traitement facture {numero_facture} - {len(lignes_factures)} lignes')
    
    # Insérer chaque ligne individuellement
    for ligne in lignes_factures:
        try:
            result = crud.create(ligne)  # Passer UNE ligne à la fois
            print(f'✅ Ligne {ligne.get("Numero_Ligne_Facture")} insérée')
        except Exception as e:
            print(f'❌ Erreur insertion ligne {ligne.get("Numero_Ligne_Facture")} : {e}')
    
    print('*' * 50)