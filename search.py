# Paramètre
# URL ODOO JCWAD
import xmlrpc.client
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('URL_ODOO')
#url = 'https://odoo.jcwad.re'
db = os.getenv('DB_ODOO')
#db = 'test_odoo_17'
#username = 'woodartdeco974@gmail.com'
#apiKey=788c811c79c24889b2214559c386e6fa2c0eebb9
username = 'info.sdpma@sicalait.fr'
password = 'nathalia974'

# XML-RPC endpoints
# authentification
info = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common'.format(url))
uid = info.authenticate(db, username, password, {})

# Check if authentication is successful
if uid:
    print("Authentification réussi. UID:", uid)

    # Get server version
    version = info.version()
    print("Odoo version:", version)
    
    #on match les produis 
    # 1. on recherche les produits dans odoo qui match avec Code_Produit urcoopa
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # 1. Rechercher le partenaire URCOOPA
    #partner = partner[0].get('purchase_order_id')[1]
    from sql.connexion import recupere_connexion_db
    
    # Requete depuis exportOdoo Analytique
    database = recupere_connexion_db()
    cursor_analytique = database.cursor(dictionary = True)
    
    requete_analytique = '''
        SELECT id 
        FROM exportodoo.account_analytic_account aaa 
        WHERE aaa.code  = '92165'
    '''
    cursor_analytique.execute(requete_analytique)
    data_analytique = cursor_analytique.fetchall()
    
    analytic_id = data_analytique[0]['id']
    print("📈 ID analytique :", analytic_id)
    
    #env pourcentage analytique
    pourcentage_analytique = float(os.getenv('POURCENTAGE_ANALYTIQUE'))
    analytic_distribution = {str(analytic_id): pourcentage_analytique}
    
    print(analytic_distribution)
else:
    print('SINON')
''' 
    analytic_accounts = models.execute_kw(
        db, uid, password,
        'account.analytic.account', 'search_read',
        [],
        {'fields': ['id', 'name']}
    )

    print(analytic_accounts)
    
    
    if not partner_ids:
        print("❌ Partenaire introuvable.")
        exit()

    partner_id = partner_ids[0]
    print(f"[INFO] Partenaire trouvé : ID={partner_id}")

    # 2. Rechercher les bons de commande liés à ce partenaire
    purchase_orders = models.execute_kw(
        db, uid, password,
        'purchase.order', 'search_read',
        [[['partner_id', '=', partner_id]]],
        {'fields': ['id', 'name', 'state']}
    )

    if not purchase_orders:
        print("❌ Aucun bon de commande trouvé pour ce partenaire.")
        exit()

    print(f"[INFO] {len(purchase_orders)} commandes trouvées.")

    # 3. Parcourir et agir selon l'état
    for order in purchase_orders:
        if order['state'] == 'draft':   # 👉 pour confirmer les brouillons
            models.execute_kw(
                db, uid, password,
                'purchase.order', 'button_confirm',
                [[order['id']]]
            )
            print(f"✅ Commande {order['name']} confirmée.")
        elif order['state'] == 'purchase':  # 👉 si déjà confirmée, on peut annuler
            models.execute_kw(
                db, uid, password,
                'purchase.order', 'button_cancel',
                [[order['id']]]
            )
            print(f"⛔ Commande {order['name']} annulée.")
        else:
            print(f"⚠️ Commande {order['name']} ignorée (state={order['state']}).")
    
    
    product_ids = models.execute_kw(
                db, uid, password,
                'product.product', 'search',
                [[['product_tmpl_id', '=', '110822']]],
                {'limit': 1}
            )

    print('✅ Champs account.move.line disponibles :', product_ids)

    partner = models.execute_kw(
        db, uid, password,
        'purchase.order', 'search_read',
        [
            #[['parent_state', '=', 'posted']],
            #[['partner_id', '=', '5081' ]]
        ],
        {
            #'limit': 1000,
            #'fields': ['purchase_order_id','partner_id', 'name', 'partner_ref', 'invoice_status']
        }
    #)[0].get('purchase_order_id')[1]
    )
    
    nbCommande = []
    
    for ligne in partner:
        
        if ligne.get('partner_id')[0] == 5081 and ligne.get('invoice_status') == 'no': 
            
            if ligne.get('partner_ref'):
                numero_reference_gesica = ligne.get('partner_ref').replace('GESICA', '').strip()
            else :
                numero_reference_gesica= ''
            nbCommande.append(ligne
                
            )
            
                {
                'name' : ligne.get('name'),
                'partner_ref' : numero_reference_gesica,
                'invoice_status' : ligne.get('invoice_status')
                
                
    
    partner = models.execute_kw(
        db, uid, password,
        'account.move.line', 'search_read',
        [
            #[['parent_state', '=', 'posted']],
            [['purchase_order_id', '=', '']]
        ],
        {
            'limit': 1000,
            'fields': ['purchase_order_id']
        }
    #)[0].get('purchase_order_id')[1]
    )
        partner = models.execute_kw(
        db, uid, password,
        'account.move.line', 'search_read',
        [],
        {
            'limit': 200
            #'fields': ['id', 'name', 'parent_ids']
        }
    )
    
    for value in partner: 
        
        if value.get('parent_ids')[0] == 19 :
            print('sicalait => ', value)
    
    
    partner = models.execute_kw(
        db, uid, password,
        'res.company', 'search_read',
        #[[['name', '=', 'URCOOPA']]],
        #[[['name', '=', 'LEPA ST JOSEPH']]],
        [[[ 'parent_ids', '=', [19] ]]],
        {
            #'limit' : 1000,
            'fields': ['id', 'name', 'parent_ids']
        }
        #{'fields': ['id', 'name']}
    )
    
    # 2. Trouver les produits liés à ce fournisseur
    company = models.execute_kw(
        db, uid, password,
        'product.supplierinfo', 'read',
        [[['partner_id', '=', partner['id']]]],
        {'fields': ['product_tmpl_id', 'product_code']}
    )
    
    
    # 3. Extraire les IDs de templates produits
    #if info.get('product_tmpl_id')
    product_ids = [info['product_tmpl_id'][0] for info in supplier_infos ]

    # 4. Lire les produits
    products = models.execute_kw(
        db, uid, password,
        'product.template', 'search_read',
        [[['id', 'in', product_ids]]],
        {
            
            'fields': ['name', 'weight', 'weight_uom_name', 'default_code']
        }
    )
    # Map {product_tmpl_id: product_code}
    code_map = {
        info['product_tmpl_id'][0]: info['product_code']
        for info in supplier_infos if info.get('product_code')
    }

    # Ajouter le product_code à chaque produit
    for p in products:
        tmpl_id = p['id']
        p['product_code'] = code_map.get(tmpl_id)
    
    
    #test que chaque produits match
    #print('Res.Partner: \n\n\n')
    #print(json.dumps(ids.get('id'), indent=4, ensure_ascii=False))
    print(json.dumps(product_ids, indent=4, ensure_ascii=False))

    # Méthodes import json
    with open('res_partner.json', 'w', encoding='utf-8') as f:
        json.dump(product_ids, f, ensure_ascii=False, indent=4)
    
    #print('models read. RESULTAT: ', partner)
    print("Enregistrement effectué ")
    '''
    