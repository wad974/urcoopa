class METHODE:
    
    #on passe au préalable les cnx pour odoo
    #function (models, db, uid, password)
    def __init__(self, models, db, uid, password):
        #on recupere tous les cnx
        self.models = models
        self.db = db
        self.uid = uid
        self.password = password
        
    """
    on creer les functions besoins pour stats
    """
    
    def CommandeOdooPourEnvoiUrcoopa(self, dateDepart, DateFin):
        models = self.models
        commandes = models.execute_kw(
            self.db, self.uid, self.password,
            'purchase.order',
            #'search',
            'search_read',
            #'search_count',
            [[
                ['date_order', '>=', dateDepart], #depart Jours
                ['date_order', '<=', DateFin] # fin jours present
            ]],
            {
                #'limit' : 10,
                'order': 'id asc'
            }
        )
        
        data_commande = []
        
        for commande in commandes:
            if (commande['partner_id'][1] == "URCOOPA" 
                and commande['state'] == 'purchase'):
                
                data_commande.append(commande)
                
        print(f'CONTENU DANS {len(data_commande)}')
        return len(data_commande)