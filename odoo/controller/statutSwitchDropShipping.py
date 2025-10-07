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


def switchStatutFacturationUrcoopa(commande, models, db, uid, password):
    """Confirme une commande si elle est en brouillon"""
    if commande['state'] == 'purchase': # etat de la commande = demande de prix
        models.execute_kw(
            db, uid, password,
            'purchase.order', 'action_create_invoice',
            [[commande['id']]]
        )
        print(f"✅ Commande {commande['name']} creer facture confirmée.")
    else:
        print(f"⚠️ Commande {commande['name']} ignorée (state={commande['state']}).")
