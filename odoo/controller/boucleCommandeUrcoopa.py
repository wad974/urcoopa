def boucleCommandeUrcoopa(commande, models, db, uid, password, WSDL_URL, API_KEY_URCOOPA):
    
        #print(commande.get('partner_id'), commande.get('state'))
        partner_urcoopa = commande.get('partner_id')
        
        #filtre par urcoopa
        if partner_urcoopa[1] != 'URCOOPA':
            print('[FAULT] ❌ FAUSSE ALERTE - NON URCOOPA ', partner_urcoopa , '\n')
            return
        
        print('[SUCCESS] ✅  BINGO URCOOPA')      
        # ---------------------
        # 1. 📦 Récupérer la commande Odoo
        # ---------------------
        print('[INFO] 1. 📦 Récupération de la commande Odoo : ', commande.get('name'))
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
            
            #print('[INFO] 2. 📦 Récupérer le partner Odoo')
            partner = models.execute_kw(
                db, uid, password,
                'res.partner', 'read',
                [[commande['partner_id'][0]]],
                {'fields': ['name']}
            )[0]
            #print('[SUCCESS] ✅ Partner Odoo récupéré : ', partner)
            
            #recuperation info : login mail societe
            #print('[INFO] COMMANDE USER: ', commande['company_id'])
            IdCommandeUser = commande['user_id']
            
            if not IdCommandeUser:
                IdCommandeUser = commande['company_id']
                
            info_user = models.execute_kw(
                db, uid, password,
                #'purchase.order.line', 'search_read',      
                'res.company', 'search_read',
                [[[ 'id', '=', IdCommandeUser[0] ]]],  # pas de filtre, on veut tout
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
            #print('[INFO] 📦 Produits récupéré')
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
                            
                #print('[INFO] Code fournisseur récupéré :', product_code)
                
                '''
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
                
                print('*'*50)
                print('[INFO] Ligne commande :')
                print('[INFO] Code_Produit : ', product_code)
                print('[INFO] Libelle_Produit : ', ligne['name'])
                print('[INFO] Quantite_Commande :', ligne['product_qty'])
                print('*'*50)
                '''
                
                #conditions si product_qty = 0
                if ligne['product_qty'] == 0:
                    continue
                else:
                    ligne_commande.append({
                        "Numero_ligne": i + 1,
                        "Code_Produit": product_code,
                        "Libelle_Produit": ligne['name'],
                        "Quantite_Commandee": ligne['product_qty'],
                        "Unite_Commande": "UN"
                        #Quantite_Commandee
                        #Unite_Commande (valeurs attendues : "UN", "KG" ou "TO")
                    })
            
            #print('[INFO] 📦 lignes produits Commandes final : ', json.dumps(ligne_commande, indent=2))
            print('[INFO] 📦 lignes produits Commandes final OK!')
            
            #on enleve gesica
            reference_partenaire = commande.get('partner_ref')
            
            if reference_partenaire == '' or reference_partenaire is None or reference_partenaire == False:
                reference = commande.get('name').strip()
                
            else : 
                reference = reference_partenaire.replace('GESICA', "").strip()
                
            '''
            if reference_partenaire:
                reference = reference_partenaire.replace('GESICA', "").strip()
            else :
                reference = commande.get('name').strip()
            '''
            
            #requete code client
            if not commande['company_id']:
                return
            else:
                #print( '\n📤 [INFO] REQUETE SQL CODE COMPANY_ID ODOO : ', json.dumps( commande['company_id'][0], indent=2 ))
                code = commande['company_id'][0] 
                #print(json.dumps( commande, indent=2 ))          
                
                #requete sic_depot
                print('🌐 init SQL POUR CODE CLIENT')
                
                from sql.connexion import recupere_connexion_db
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
                    #print('Code_Client :', code_client)
                
                else: 
                    #"Code_Client": "5024",
                    code_client = datas[0].get('code_urcoopa')
                    code_adresse_livraison = datas[0].get('code')
            
            import json
            from datetime import datetime , timedelta, date
            
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
            # 3. 📤 Envoi ACTION button valider commande
            # ---------------------
            
            # APPEL à Action 
            
            
            # ---------------------
            # 3. 📤 Envoi via SOAP
            # ---------------------
            
            from testEnvoiAPI import send_soap
            #print(commande_json)
            send_soap(WSDL_URL, API_KEY_URCOOPA, commande_json)
            print(f'[SUCCESS] ✅ Commande : {commande["name"]} traiter \n')
        else : 
            print(f'[FAULT] ❌ ZUT COMMANDE : {commande["name"]} TOUJOURS EN BROUILLON \n') 