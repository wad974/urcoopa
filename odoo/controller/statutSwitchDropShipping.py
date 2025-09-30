def switchStatutUrcoopa(commande, models, db, uid, password):
    """Confirme une commande si elle est en brouillon"""
    if commande['state'] == 'draft': # etat de la commande = demande de prix
        models.execute_kw(
            db, uid, password,
            'purchase.order', 'button_confirm',
            [[commande['id']]]
        )
        print(f"✅ Commande {commande['name']} confirmée.")
    else:
        print(f"⚠️ Commande {commande['name']} ignorée (state={commande['state']}).")
