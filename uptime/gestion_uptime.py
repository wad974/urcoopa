def traitement_uptime(datetime, os, HTTPException, push_url):
    
    start_time = datetime.now()
    
    try:
        print('[INFO] 🌐 INITIALISATION UPTIME MONITORING')
        
        # En cas de succès
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Notification Uptime Kuma - SUCCÈS  
        
        if push_url:
            from uptime.sonde import notify_uptime_kuma
            notify_uptime_kuma(
                push_url=push_url,
                status="up",
                message="OK", 
                ping_time=processing_time
            )
        
        return {
            'STATUS': 'SUCCESS',
            'MESSAGE': 'AUCUNE ERREUR DETECTER',
            'SUCCESS' : f"Envoi commandes réussi - {processing_time}ms"
        }
        
    except Exception as e:
        print(f"❌ Erreur envoi commandes: {e}")
        
        # Notification Uptime Kuma - ERREUR
        if push_url:
            notify_uptime_kuma(
                push_url=push_url,
                status="down",
                message=f"Erreur envoi commandes: {str(e)[:100]}"
            )
        
        raise HTTPException(status_code=500, detail=str(e))
