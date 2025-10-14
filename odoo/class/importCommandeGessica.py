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