from fastapi import HTTPException
import requests
import json
import os
from sql.connexion import recupere_connexion_db
from sql.models import CRUD
import time
import datetime
import xmlrpc.client
from fastapi.responses import JSONResponse





async def createAdherentOdoo(rows: list, models, db, uid, password, status):
    
    #efface la console
    #clear = lambda: os.system('clear')
    #clear()

    # 3 tentative 
    #for attempt in range(3):
    try :
        
        print('🔍[INFO] Recherche dans res.partner')
        print('🔍[INFO] Nom adherent à matcher: ',rows[0]['Nom_Client'])
        # Récupération du fournisseur URCOOPA
        ids_fournisseur = models.execute_kw(
            db, uid, password,
            'res.partner', 'search',
            [[['name', '=', rows[0]['Nom_Client'] ]]],
            {'limit': 1}
        )
        print(f"✅ Ids fournisseur qui match -> Odoo  : {ids_fournisseur}")
        
        if not ids_fournisseur or len(ids_fournisseur) == 0:
            #ICI ON PEUT INSERER LES CLIENTS QUI NE MATCH OU EXISTE PAS DANS LA BASE DE DONNEES
            crud = CRUD()
            
            print(f"❌ Adherent {rows[0]['Nom_Client']} non trouvé dans supplierinfo. \n\n")
            crud.insertAdherentCorrespondance(rows[0]['Nom_Client'])
            crud.updateSicUrcoopaFacture(rows[0]['Numero_Facture'])
            
            if status : 
                return(JSONResponse(content={"message": "Client adherent non trouvé."}, status_code=511))
            else :
                return
            
        # recherche id fournisseur sicalait pour urcoopa->sicalait
        # Récupération du fournisseur URCOOPA
        ids_fournisseur_Sicalait = models.execute_kw(
            db, uid, password,
            'res.partner', 'search',
            [[['name', '=', 'SICALAIT' ]]],
            {'limit': 1}
        )
        
        #urcoopa
        ids_fournisseur_Urcoopa = models.execute_kw(
            db, uid, password,
            'res.partner', 'search',
            [[['name', '=', 'URCOOPA' ]]],
            {'limit': 1}
        )
        
        name_fournisseur_sicalait = models.execute_kw(
            db, uid, password,
            'res.partner', 'read',
            [ids_fournisseur_Sicalait],
            {'fields': ['name']}
        )[0]['name']
        
        name_fournisseur_urcoopa = models.execute_kw(
            db, uid, password,
            'res.partner', 'read',
            [ids_fournisseur_Urcoopa],
            {'fields': ['name']}
        )[0]['name']
        
        partner_id_sicalait = ids_fournisseur_Sicalait[0]
        partner_id_urcoopa = ids_fournisseur_Urcoopa[0]
            
        # Id fournisseur pour sicalait->adherent
        partner_id = ids_fournisseur[0]
        
        name_fournisseur = models.execute_kw(
            db, uid, password,
            'res.partner', 'read',
            [ids_fournisseur],
            {'fields': ['name']}
        )[0]['name']
        # Id fournisseur 
        print(f"✅ Name fournisseur qui match -> Odoo : {name_fournisseur}")
        
        
        # Infos communes à toute la facture
        #Contenu de row avant traitement pour Odoo
        
        #print(f"✅ Contenu de Rows avant injection. Rows: {json.dumps(rows, indent=2)}")
        #numero_facture = f"URCOOPA/{str(datetime.datetime.now().strftime('%Y/%m'))}/{str(rows[0]['Numero_Facture'])}"
        ref_facture = rows[0]['Numero_Facture']
        invoice_date = rows[0]['Date_Facture']
        invoice_date_due = rows[0]['Date_Echeance']

        invoice_lines = []

        # Récupération des lignes produits
        for row in rows:
            
            #code produit
            #print(json.dumps(row, indent=2))
            print(f"🔍 [INFO] Recherche produit à {datetime.datetime.now().strftime('%H:%M:%S')} : {row.get('Code_Produit')}")
            code_produit = row.get('Code_Produit')
            tmpl_id = int()
            
            if code_produit is None:
                tmpl_id = int(row.get('ID_Produit_tmpl_ODOO'))
                print('[INFO] Code produit is None tmpl_id = ', tmpl_id)
            
            if code_produit is not None:
                #time.sleep(1)  # ralentis de 1000ms
                supplier_ids = models.execute_kw(
                    db, uid, password,
                    'product.supplierinfo', 'search',
                    [[
                        ['product_code', '=', code_produit],
                        #['partner_id', '=', partner_id]
                    ]],
                    {'limit': 1}
                )
                #supplier_ids récupérer
                print(f'✅ [SUCCESS] Supplier_ids récupérer dans Odoo : {supplier_ids}')

                if not supplier_ids:
                    
                    crud = CRUD()
                    print(f"❌ Produit {code_produit} non trouvé dans supplierinfo. \n\n")
                    crud.insertArticleCorrespondance(code_produit)
                    crud.updateSicUrcoopaFacture(ref_facture)
                    
                    if status : 
                        return(JSONResponse(content={"message": f"Produit {code_produit} non trouvé dans supplierinfo."}, status_code=500))
                    else :
                        continue
                
                #time.sleep(1)  # ralentis de 1000ms
                #supplier_data
                supplier_data = models.execute_kw(
                    db, uid, password,
                    'product.supplierinfo', 'read',
                    [supplier_ids],
                    {'fields': ['product_tmpl_id']}
                )[0]

                #supplier _data récuperer
                print(f'✅ [SUCCESS] Supplier_data récupéré -> Odoo : {supplier_data}')

                #product tmpl id recupéré uniquement
                product_tmpl = supplier_data.get('product_tmpl_id')

                #Si product tmpl est False on arrete la boucle et on continue sur l'autre produit
                if not product_tmpl or product_tmpl[0] is False:
                    return(JSONResponse(content={"message": f"Produit code dans Facture -> Rows {code_produit} non trouvé dans supplierinfo."}, status_code=500))
                    
                    print(f"❌ Produit code dans Facture -> Rows {code_produit} non trouvé dans supplierinfo.")
                    continue
                
                tmpl_id = supplier_data['product_tmpl_id'][0]

            #time.sleep(1)  # ralentis de 1000ms
            print(f'✅ tmpl_id récupérer  : {tmpl_id}')
            product_ids = models.execute_kw(
                db, uid, password,
                'product.product', 'search',
                [[['product_tmpl_id', '=', tmpl_id]]],
                {'limit': 1}
            )
            #supplier_ids récupérer
            print(f'✅ Product_ids récupérer -> Odoo  : {product_ids}')

            if not product_ids:
                return(JSONResponse(content={"message": f"❌ Aucun produit trouvé pour le template {tmpl_id}"}))
                
                print(f"❌ Aucun produit trouvé pour le template {tmpl_id}")
                continue

            product_id = product_ids[0]
            print(f"✅ Produit trouvé pour {code_produit} ➔ ID {product_id}")

            #unité facture
            udm_code = row.get('Unite_Facturee')
            if udm_code == 'UN':
                udm_id = 1
            elif udm_code == 'TO':
                udm_id = 14
            else:
                print(f"⚠️ Unité {udm_code} non reconnue, unité par défaut forcée (UN)")
                udm_id = 1  # fallback safe
                
            udm = models.execute_kw(
                db, 
                uid, 
                password, 
                'uom.uom', 
                'read', 
                [udm_id],
                {
                    #'fields' : ['product_uom_id']
                    'fields' : ['name']
                }
                )[0]
            print(f"✅ Unités de mesure récupéré -> {row.get('Unite_Facturee')} - {udm_id} : {udm.get('name')}")
            
            invoice_lines.append([0, 0, {
                'product_id': product_id,
                'quantity': row['Quantite_Facturee'],
                #'product_uom_id': udm.get('name'),
                'price_unit': row['Prix_Unitaire']
            }])

        if not invoice_lines:
            return(JSONResponse(content={"message": "❌ Aucune ligne de produit valide à créer. Annulation."}, status_code=500))
                
            print("❌ Aucune ligne de produit valide à créer. Annulation.")
            return

        #Debug JSON
        #import json
        #print(f"📦 Facture creer pour Odoo : {rows[0]['Numero_Facture']} - {sendAccountMove}")
        #print(json.dumps(sendAccountMove, indent=2))
        
        # Envoi
        try:
            if status:
                
                # Construction de la facture pour l'urcoopa en premier
                sendAccountMoveFournisseur = {
                    "move_type": "in_invoice",
                    "partner_id": partner_id_urcoopa,
                    "invoice_partner_display_name": name_fournisseur_urcoopa,
                    "ref": ref_facture,
                    "invoice_date": invoice_date,
                    "invoice_date_due": invoice_date_due,
                    "invoice_line_ids": invoice_lines
                }
                
                print(f"📦 Facture Urcoopa creer pour Odoo_Sicalait : {rows[0]['Numero_Facture']} - {sendAccountMoveFournisseur}")
                
                
                # on creer dans account.move la facture fournisseur
                move_id = models.execute_kw(
                    db, uid, password,
                    'account.move', 'create',
                    [sendAccountMoveFournisseur]
                )
                
                # Un write vide peut déclencher les compute fields
                models.execute_kw(
                    db, uid, password,
                    'account.move', 'write',
                    [move_id, {}]  
                )
                
                print(f"✅📤 [SUCCESS] Facture Urcoopa envoyer à Odoo_Sicalait : {rows[0]['Numero_Facture']} \n")
                
                #puis on injecte la facture adherent 
                # COEFFICIENT SUR FACTURE ADHERENT
                # augementation pour ajouter 5%
                POURCENTAGE_COEF = float(os.getenv('COEFFICIENT'))
                #PORCENTAGE_COEF = 1.05 #coefficient de 5% (100% + 5% = 105% - 1.0 + 0.05)
                invoice_lines_avec_coef = []
                
                for row in invoice_lines:
                    
                    # row = [0, 0, {'product_id': 102562, 'quantity': 2.04, 'price_unit': 486.23}]
                    ligne = row[2]  # Récupère le dictionnaire en position 2
                    
                    invoice_lines_avec_coef.append([0, 0, {
                        'product_id': ligne.get('product_id'),
                        'quantity': ligne.get('quantity'),
                        'price_unit': ligne.get('price_unit') * POURCENTAGE_COEF  # Application du coef
                    }])
                        
                #DEBUG INVOICE    
                print(invoice_lines)
                print(invoice_lines_avec_coef)
                
                # Construction de la facture pour l'adherent en deuxiement
                sendAccountMove = {
                    "move_type": "out_invoice",
                    #"invoice_user_id": partner_id_sicalait, # A rajouter dans res.users le partner_id de sicalait
                    "partner_id": partner_id,
                    "invoice_partner_display_name": name_fournisseur,
                    "ref": ref_facture,
                    "invoice_date": invoice_date,
                    "invoice_date_due": invoice_date_due,
                    "invoice_line_ids": invoice_lines_avec_coef # injection facture avec coef
                }
                
                print(f"📦 Facture Sicalait creer pour Adherent : {rows[0]['Numero_Facture']} - {sendAccountMove}")
                
                move_id = models.execute_kw(
                    db, uid, password,
                    'account.move', 'create',
                    [sendAccountMove]
                )
                
                models.execute_kw(
                    db, uid, password,
                    'account.move', 'write',
                    [move_id, {}]  # Un write vide peut déclencher les compute fields
                )
                
                print(f"✅📤 [SUCCESS] Facture Sicalait creer pour Adherent: {rows[0]['Numero_Facture']} \n\n")
                
                
                return(JSONResponse(content={"message": "Votre facture a bien été transférée dans Odoo."}, status_code=200))
            else : 
                
                crud = CRUD()
                crud.updateSicUrcoopaFacture(ref_facture)
                
                print(f"✅📤 [SUCCESS] Facture Mise à jour réussie \n\n")
                    
            #print(f"✅📤 [SUCCESS] Facture Odoo créée avec ID {move_id} \n\n")
        except xmlrpc.client.Fault as e:
            #Retourne tous les erreur odoo
            #Erreur odoo si facture existe sera retrouné
            print(f"❌ Erreur Envoi XML-RPC Odoo : {e.faultString} \n\n")
            return(JSONResponse(content={"message": f"{e.faultString}"}, status_code=200))
        
    except xmlrpc.client.Fault as e:
        print(f"❌ Erreur XML-RPC Odoo : {e.faultString}")
    except Exception as e:
        print(f"🔥 Erreur récupération facture : {str(e)}")