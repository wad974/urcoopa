# function uptime
import requests

def notify_uptime_kuma(push_url: str, status: str = "up", message: str = "OK", ping_time: int = None):
    """Notifie Uptime Kuma du statut du service"""
    try:
        params = {
            "status": status,  # "up", "down", "error"
            "msg": message
        }
        
        #if ping_time:
        #    params["ping"] = ping_time
            
        #response = requests.get(push_url, params=params, timeout=10)
        response = requests.get(push_url, params=params)
        print(f"[UPTIME] Notification envoyée: {status} - {message}")
        return response.status_code == 200
    except Exception as e:
        print(f"[UPTIME ERROR] Échec notification: {e}")
        return False