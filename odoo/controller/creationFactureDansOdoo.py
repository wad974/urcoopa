from fastapi import HTTPException
import requests
import json
import os
from sql.connexion import recupere_connexion_db
import time
import datetime
import xmlrpc.client




def function_creation_facture_dans_odoo(continue_integration_facture, purchase, rows: list, models, db, uid, password):
    
    #efface la console
    #clear = lambda: os.system('clear')
    #clear()

    # 3 tentative 
    #for attempt in range(3):
    try :
        
        # 1. Rechercher numero commande existant
        # on boucle sur la commande existant
        continue_integration_facture = continue_integration_facture
        name_purchase_order = ''
        id_purchase_order = int()
        
        # condition si vrai execute create odoo
        #print('[INFO] ETAT CONDITIONS INTEGRATION FACTURE : ', continue_integration_facture)
        if continue_integration_facture == True : 
            
            name_purchase_order = purchase.get('name')
            #name_purchase_order = rows[0].get('Numero_Commande_ODOO')
            id_purchase_order = purchase.get('id')
            
            #conditions pour origin document si origine trouver dans achat sinon Numero facture
            if purchase.get('origin') == '' or purchase.get('origin') is None or purchase.get('origin') == False:
                ref_facture = rows[0]['Numero_Facture']
                
            else:
                ref_facture = purchase.get('origin')
                #ref_facture = rows[0]['Numero_Facture']
                
            invoice_date = rows[0]['Date_Facture']
            invoice_date_due = rows[0]['Date_Echeance']
            
            # Récupération du fournisseur URCOOPA
            ids_fournisseur = models.execute_kw(
                db, uid, password,
                'res.partner', 'search',
                [[['name', '=', 'URCOOPA']]],
                {'limit': 1}
            )
            
            if not ids_fournisseur:
                print("❌ Fournisseur 'URCOOPA' non trouvé.\n\n")
                return
            # Id fournisseur 
            print(f"✅ Ids fournisseur -> Odoo  : {ids_fournisseur}")
            partner_id = ids_fournisseur[0]
            
            name_fournisseur = models.execute_kw(
                db, uid, password,
                'res.partner', 'read',
                [ids_fournisseur],
                {'fields': ['name']}
            )[0]['name']
            # Id fournisseur 
            print(f"✅ Name fournisseur -> Odoo : {name_fournisseur}")
            
            
            # Infos communes à toute la facture
            #Contenu de row avant traitement pour Odoo
            import json
            #print(f"✅ Contenu de Rows avant injection. Rows: {json.dumps(rows, indent=2)}")
            #numero_facture = f"URCOOPA/{str(datetime.datetime.now().strftime('%Y/%m'))}/{str(rows[0]['Numero_Facture'])}"
            
            invoice_lines = []
            
            # Récupération des lignes produits
            for row in rows:
                
                #code produit
                #print(f"🔍 [INFO] Recherche produit à {datetime.datetime.now().strftime('%H:%M:%S')} : {row.get('Code_Produit')}")
                code_produit = row.get('Code_Produit')
                
                #time.sleep(1)  # ralentis de 1000ms
                supplier_ids = models.execute_kw(
                    db, uid, password,
                    'product.supplierinfo', 'search',
                    [[
                        ['product_code', '=', code_produit],
                        ['partner_id', '=', partner_id]
                    ]],
                    {'limit': 1}
                )
                #supplier_ids récupérer
                #print(f'✅ [SUCCESS] Supplier_ids récupérer dans Odoo : {supplier_ids}')
                
                if not supplier_ids:
                    print(f"❌ Produit {code_produit} non trouvé dans supplierinfo.")
                    from sql.models import CRUD
                    crud = CRUD()
                    crud.insertArticleCorrespondance(code_produit)
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
                #print(f'✅ [SUCCESS] Supplier_data récupéré -> Odoo : {supplier_data}')
                
                #product tmpl id recupéré uniquement
                product_tmpl = supplier_data.get('product_tmpl_id')
                
                #Si product tmpl est False on arrete la boucle et on continue sur l'autre produit
                if not product_tmpl or product_tmpl[0] is False:
                    print(f"❌ Produit code dans Facture -> Rows {code_produit} non trouvé dans supplierinfo.")
                    from sql.models import CRUD
                    CRUD.insertArticleCorrespondance(code_produit)
                    continue
                
                tmpl_id = supplier_data['product_tmpl_id'][0]
                
                #time.sleep(1)  # ralentis de 1000ms
                product_ids = models.execute_kw(
                    db, uid, password,
                    'product.product', 'search',
                    [[['product_tmpl_id', '=', tmpl_id]]],
                    {'limit': 1}
                )
                #supplier_ids récupérer
                #print(f'✅ Product_ids récupérer -> Odoo  : {product_ids}')
                
                if not product_ids:
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
                #print(f"✅ Unités de mesure récupéré -> {row.get('Unite_Facturee')} - {udm_id} : {udm.get('name')}")
                
                # Recherche de la ligne de commande achat (purchase.order.line)
                purchase_line_ids = models.execute_kw(
                    db, uid, password,
                    'purchase.order.line', 'search',
                    [[
                        ['order_id', '=', id_purchase_order],
                        ['product_id', '=', product_id]
                    ]],
                    {'limit': 1}
                )
                #print(f'[INFO] Il y a quoi dans purchase_line_ids => {purchase_line_ids}')
                if not purchase_line_ids:
                    #print(f"❌ Pas de ligne de commande trouvée pour produit ID {product_id} dans commande {id_purchase_order}")
                    purchase_line_id = False  # Pas de lien avec bon de commande
                else:
                    purchase_line_id = purchase_line_ids[0]
                    print(f"✅ purchase_line_id récupéré : {purchase_line_id}")
                    
                invoice_lines.append([0, 0, {
                    'product_id': product_id,
                    'quantity': row['Quantite_Facturee'],
                    #'product_uom_id': udm.get('name'),
                    'price_unit': row['Prix_Unitaire'],
                    'purchase_line_id' : purchase_line_id
                }])
                
            if not invoice_lines:
                print("❌ Aucune ligne de produit valide à créer. Annulation.")
                return
            
            #type de facture
            moveType = ''
            if rows[0]['Type_Facture'] == 'F':
                moveType = 'in_invoice'
            elif rows[0]['Type_Facture'] == 'A':
                moveType = 'in_refund'
            
            #filtre facture mag-sicalait uniquement
            
            from sql.connexion import recupere_connexion_db
            connexion = recupere_connexion_db()
            cursor = connexion.cursor(dictionary=True)
            cursor.execute('select distinct Code_Client,  Societe_Facture_ODOO from exportodoo.sic_urcoopa_facture suf where Societe_Facture_ODOO  IS NOT NULL ')
            magasin = cursor.fetchall()
            
            #print( 'ICI MAGASIN -> ',magasin )
            sendAccountMove = {}
            
            #print('ICI ROWS -> ',rows[0]['Type_Client'])
            #if rows[0]['Type_Client'] == 'MAG. SICALAIT' and rows[0]['Type_Client'] == 'MAG. SDPMA':
            
            for code_client in magasin: 
                    
                    #print('[INFO] Code_Client :', rows[0]['Code_Client'], '==', code_client['Code_Client'])
                    #print('[INFO] EN ATTENTE DU BON CODE CLIENT ... ')
                    if rows[0]['Code_Client'] == code_client['Code_Client'] :
                        #print('code client company id : ', code_client['Societe_Facture_ODOO'])
                        # Construction de la facture
                        sendAccountMove = {
                            "move_type": moveType,
                            "partner_id": partner_id,
                            "company_id" : int(code_client['Societe_Facture_ODOO']),
                            "invoice_partner_display_name": name_fournisseur,
                            "ref": ref_facture,
                            "invoice_date": invoice_date,
                            "invoice_date_due": invoice_date_due,
                            'invoice_origin': name_purchase_order,
                            "invoice_line_ids": invoice_lines
                        }
                        
                        # Debug JSON
                        #import json
                        print(f"\n📦 Facture creer pour Odoo : {rows[0]['Numero_Facture']}")
                        #print(json.dumps(sendAccountMove, indent=2))
                        
                        # Envoi
                        try:
                            
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
                            
                            print(f"✅📤 [SUCCESS] Facture envoyer à Odoo : {rows[0]['Numero_Facture']} \n")
                            from sql.models import CRUD
                            crud = CRUD()
                            crud.UpdateStatutIntegrationFactureOdoo(rows[0]['Numero_Facture'])
                            #print(f"✅📤 [SUCCESS] Facture Odoo créée avec ID {move_id} \n\n")
                            continue
                            
                        except xmlrpc.client.Fault as e:
                            #Retourne tous les erreur odoo
                            #Erreur odoo si facture existe sera retrouné
                            print(f"❌ Erreur Envoi XML-RPC Odoo : {e.faultString} \n\n")
                        
                    else: 
                        #print('[INFO] Code_Client :', rows[0]['Code_Client'], '\n' )
                        continue
            #else : 
            #    print('[INFO] ERREUR TYPE CLIENT :', rows[0]['Type_Client'] )
        #else :
        #    print('❌ [INFO] Non continue_integration_facture')
        
        else:
            print(f'[INFO] PAS DE PURCHASE ORDER POUR LA FACTURE {rows[0].get('Numero_Commande_ODOO')}')
            
            
    except xmlrpc.client.Fault as e:
        print(f"Erreur XML-RPC Odoo : {e.faultString}")
    except Exception as e:
        print(f"🔥 Erreur récupération facture : {str(e)}")