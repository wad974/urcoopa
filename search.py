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
    
    ids = models.execute_kw(
        db, 
        uid, 
        password, 
        'res.company', 
        'search_read',
        # on match tous les product_code qui sont égale Code_Produit
        [], 
        {'fields': ['id', 'name', 'email']}
        )
    products = models.execute_kw(
                db, uid, password,
                'purchase.order.line', 'search_read',
                [],
                {   'limit' : 20,
                    #'fields': ['product_id', 'name', 'product_qty']
                }
            )
    
    
    #test que chaque produits match
    print('Res.Partner: \n\n\n')
    print(json.dumps(products, indent=4, ensure_ascii=False))

    # Méthodes import json
    with open('res_partner.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    
    #print('models read. RESULTAT: ', partner)
    print("Enregistrement effectué ")
    
    
else:
    print("Authentication failed.")
    
