import requests
import json
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
import xml.sax.saxutils as saxutils

import requests
import json
from xml.etree import ElementTree as ET
import xml.sax.saxutils as saxutils

def envoyer_commande_soap(commande_json, api_key):
    """
    Version avec debug complet pour identifier le problème
    """
    url = "https://www.urcoopa.fr/ws_sicalait/awws/WS_Sicalait.awws"
    
    # Headers multiples à tester
    headers_options = [
        # Option 1 : Headers basiques
        {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '""'  # SOAPAction vide
        },
        # Option 2 : Headers avec SOAPAction spécifique
        {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'urn:WS_Sicalait#Push_Commandes_Sicalait'
        },
        # Option 3 : Headers sans SOAPAction
        {
            'Content-Type': 'text/xml; charset=utf-8'
        },
        # Option 4 : Headers avec SOAPAction
        
        {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'urn:WS_Sicalait/Push_Commandes_Sicalait'
        }
    ]
    
    # Convertir la commande en JSON string
    jCommande_str = json.dumps(commande_json, ensure_ascii=False)
    
    print(f"[DEBUG] 🔍 API Key utilisée: {api_key}")
    print(f"[DEBUG] 🔍 Longueur API Key: {len(api_key)}")
    print(f"[DEBUG] 🔍 JSON à envoyer: {jCommande_str}")
    
    # Échapper pour XML
    jCommande_escaped = saxutils.escape(jCommande_str)
    
    # Tester différents formats de requête SOAP
    soap_templates = [
        # Template 1 : Format standard
        f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
                xmlns:urn="urn:WS_Sicalait">
    <soap:Body>
        <urn:Push_Commandes_Sicalait>
            <urn:xCleAPI>{api_key}</urn:xCleAPI>
            <urn:jCommande>{jCommande_escaped}</urn:jCommande>
        </urn:Push_Commandes_Sicalait>
    </soap:Body>
</soap:Envelope>""",
        
        # Template 2 : Sans namespace prefix
        f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <Push_Commandes_Sicalait xmlns="urn:WS_Sicalait">
            <xCleAPI>{api_key}</xCleAPI>
            <jCommande>{jCommande_escaped}</jCommande>
        </Push_Commandes_Sicalait>
    </soap:Body>
</soap:Envelope>""",
        
        # Template 3 : Format simple
        f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <Push_Commandes_Sicalait>
            <xCleAPI>{api_key}</xCleAPI>
            <jCommande>{jCommande_escaped}</jCommande>
        </Push_Commandes_Sicalait>
    </soap:Body>
</soap:Envelope>""",

        # Template 4 : Format attendu
        f"""<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <Push_Commandes_Sicalait xmlns="urn:WS_Sicalait">
            <xCleAPI>{api_key}</xCleAPI>
            <jCommande>{jCommande_escaped}</jCommande>
        </Push_Commandes_Sicalait>
    </soap:Body>
</soap:Envelope>"""
    ]
    
    # Tester chaque combinaison
    for i, soap_body in enumerate(soap_templates):
        for j, headers in enumerate(headers_options):
            print(f"\n[TEST] 🧪 Test {i+1}.{j+1} - Template {i+1}, Headers {j+1}")
            print(f"[DEBUG] Headers: {headers}")
            
            try:
                response = requests.post(url, data=soap_body, headers=headers, timeout=30)
                
                print(f"[INFO] Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        root = ET.fromstring(response.text)
                        
                        # Chercher le résultat
                        result_node = None
                        for elem in root.iter():
                            if 'Result' in elem.tag:
                                result_node = elem
                                break
                        
                        if result_node is not None:
                            result_text = result_node.text
                            print(f"[RESULT] 📋 Réponse: {result_text}")
                            
                            if result_text != "Token API incorrect":
                                print(f"[SUCCESS] ✅ Combinaison gagnante trouvée!")
                                print(f"[SUCCESS] Template: {i+1}, Headers: {j+1}")
                                return {"status": "success", "message": result_text, "template": i+1, "headers": j+1}
                        else:
                            print("[WARNING] ⚠️ Pas de résultat dans la réponse")
                            print(f"Response: {response.text}")
                            
                    except ET.ParseError as e:
                        print(f"[ERROR] ❌ Erreur parsing XML: {e}")
                        print(f"Response: {response.text}")
                else:
                    print(f"[ERROR] ❌ Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    
            except Exception as e:
                print(f"[ERROR] ❌ Erreur requête: {e}")
    
    return {"status": "all_failed", "message": "Toutes les combinaisons ont échoué"}


def tester_api_directement(api_key):
    """
    Test simple avec une commande minimale pour vérifier l'API
    """
    commande_minimale = {
        "commande": [
            {
                "Societe": "UR",
                "Code_Client": "5010",
                "Numero_Commande": "TEST001",
                "Nom_Client": "Test",
                "Code_Adresse_Livraison": "01",
                "Commentaire": "",
                "Date_Livraison_Souhaitee": "20241215",
                "Num_Telephone": "",
                "Email": "",
                "Ligne_Commande": [
                    {
                        "Numero_ligne": 1,
                        "Code_Produit": "TEST",
                        "Libelle_Produit": "Test",
                        "Poids_Commande": 1
                    }
                ]
            }
        ]
    }
    
    print(f"[TEST] 🧪 Test API avec commande minimale")
    return envoyer_commande_soap(commande_minimale, api_key)


def verifier_wsdl():
    """
    Vérifier si le WSDL est accessible et récupérer les informations
    """
    wsdl_url = "https://www.urcoopa.fr/ws_sicalait/awws/WS_Sicalait.awws?wsdl"
    
    try:
        response = requests.get(wsdl_url, timeout=10)
        if response.status_code == 200:
            print("[SUCCESS] ✅ WSDL accessible")
            
            # Analyser le WSDL pour trouver les noms des méthodes et paramètres
            try:
                root = ET.fromstring(response.text)
                print("[INFO] 📋 Structure WSDL:")
                
                # Chercher les opérations
                for elem in root.iter():
                    if 'operation' in elem.tag.lower():
                        if 'name' in elem.attrib:
                            print(f"  - Opération: {elem.attrib['name']}")
                    elif 'element' in elem.tag.lower():
                        if 'name' in elem.attrib:
                            print(f"  - Élément: {elem.attrib['name']}")
                            
            except ET.ParseError as e:
                print(f"[ERROR] ❌ Erreur parsing WSDL: {e}")
                
        else:
            print(f"[ERROR] ❌ WSDL non accessible: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] ❌ Erreur accès WSDL: {e}")


# Fonction principale de test
def diagnostiquer_probleme_api(api_key):
    """
    Lance tous les tests de diagnostic
    """
    print("=" * 50)
    print("🔍 DIAGNOSTIC COMPLET API URCOOPA")
    print("=" * 50)
    
    # 1. Vérifier le WSDL
    print("\n1. 📡 Vérification WSDL")
    verifier_wsdl()
    
    # 2. Test API
    print("\n2. 🧪 Test API")
    result = tester_api_directement(api_key)
    
    print(f"\n📊 RÉSULTAT FINAL: {result}")
    
    return result


# Utilisation dans votre code principal:
# result = diagnostiquer_probleme_api("f1f3b6d5-113e-4cd1-943d-0f07d28000df")

'''
def envoyer_commande_soap(commande_json, api_key):
    """
    Envoie une commande via SOAP en utilisant requests
    """
    url = "https://www.urcoopa.fr/ws_sicalait/awws/WS_Sicalait.awws"
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'urn:WS_Sicalait#Push_Commandes_Sicalait'  # Parfois nécessaire
    }
    
    # Convertir la commande en JSON string et échapper les caractères XML
    jCommande_str = json.dumps(commande_json, ensure_ascii=False)
    jCommande_escaped = saxutils.escape(jCommande_str)
    
    # Construire le body SOAP
    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
                xmlns:urn="urn:WS_Sicalait">
    <soap:Body>
        <urn:Push_Commandes_Sicalait>
            <urn:xCleAPI>{api_key}</urn:xCleAPI>
            <urn:jCommande>{jCommande_escaped}</urn:jCommande>
        </urn:Push_Commandes_Sicalait>
    </soap:Body>
</soap:Envelope>"""
    
    try:
        print(f"[INFO] 📤 Envoi de la commande via SOAP...")
        
        response = requests.post(url, data=soap_body, headers=headers, timeout=30)
        
        print(f"[INFO] Status Code: {response.status_code}")
        print(f"[INFO] Response Headers: {response.headers}")
        
        if response.status_code == 200:
            # Parser la réponse XML
            try:
                root = ET.fromstring(response.text)
                
                # Chercher le résultat dans différents namespaces possibles
                result_node = root.find('.//Push_Commandes_SicalaitResult')
                if result_node is None:
                    result_node = root.find('.//{urn:WS_Sicalait}Push_Commandes_SicalaitResult')
                if result_node is None:
                    # Fallback - chercher n'importe quel élément contenant "Result"
                    for elem in root.iter():
                        if 'Result' in elem.tag:
                            result_node = elem
                            break
                
                if result_node is not None:
                    result_text = result_node.text
                    print(f"[SUCCESS] ✅ Réponse serveur Urcoopa: {result_text}")
                    
                    # Analyser le résultat
                    if result_text and result_text.startswith('ERREUR'):
                        print(f"[ERROR] ❌ Erreur retournée par Urcoopa: {result_text}")
                        return {"status": "error", "message": result_text}
                    else:
                        print("[SUCCESS] ✅ Commande envoyée avec succès")
                        return {"status": "success", "message": result_text}
                else:
                    print("[WARNING] ⚠️ Pas de résultat clair dans la réponse")
                    print("Réponse brute:", response.text)
                    return {"status": "unknown", "message": "Pas de résultat clair", "raw_response": response.text}
                    
            except ET.ParseError as e:
                print(f"[ERROR] ❌ Erreur de parsing XML: {e}")
                print("Réponse brute:", response.text)
                return {"status": "parse_error", "message": str(e), "raw_response": response.text}
        else:
            print(f"[ERROR] ❌ Erreur HTTP {response.status_code}")
            print("Response:", response.text)
            return {"status": "http_error", "code": response.status_code, "message": response.text}
            
    except requests.exceptions.Timeout:
        print("[ERROR] ❌ Timeout de la requête")
        return {"status": "timeout", "message": "Timeout de la requête"}
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] ❌ Erreur de requête: {e}")
        return {"status": "request_error", "message": str(e)}
    
    except Exception as e:
        print(f"[ERROR] ❌ Erreur générale: {e}")
        return {"status": "general_error", "message": str(e)}
        
'''