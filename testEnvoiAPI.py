import json
import zeep
from zeep import Client, Settings
import os
import datetime
from xml.etree import ElementTree as ET

##DEBUT FUNCTION SEND SOAP

print('[INFO] : Démarrage envoie soap')

def send_soap(WSDL_URL, API_KEY_URCOOPA, commande_data):
    
    # Récupération des variables d'environnement
    #WSDL_URL = 'https://www.urcoopa.fr/ws_sicalait/WS_Sicalait.awws?wsdl'
    #print('URL: ', WSDL_URL)
    #API_KEY_URCOOPA = 'f1f3b6d5-113e-4cd1-943d-0f07d28000df'
    #print('KEY: ', API_KEY_URCOOPA)

    # Configuration Zeep optimisée
    parametre = Settings(strict=False, xml_huge_tree=False)

    try:
        print('='*50)
        client = zeep.Client(wsdl=WSDL_URL, settings=parametre)
        print('Client créé avec succès')
    except Exception as e:
        print(f'[ERREUR] Impossible de créer le client: {e}')
        exit(1)
    
    '''
    def generer_numero_commande_unique():
        """Génère un numéro de commande unique basé sur timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return f"TEST{timestamp[-8:]}"  # Utilise les 8 derniers chiffres

    # Structure de données pour la commande avec numéro unique
    numero_commande_unique = generer_numero_commande_unique()
    print(f'[INFO] Numéro de commande généré: {numero_commande_unique}')

    
    commande_data = {
        'commande': [
            {
                "Societe": "UR",
                "Code_Client": "5950",
                "Numero_Commande": numero_commande_unique,  # Numéro unique
                "Nom_Client": "16 - LA CHALOUPE: Réceptions",
                "Code_Adresse_Livraison": "01",
                "Commentaire": "TEST RETOUR RESPONSE SOAP AVEC ZEEP CLIENT ",
                "Date_Livraison_Souhaitee": "20250616",
                "Num_Telephone": '0123456789',
                "Email": "test@sicalait.fr",
                "Ligne_Commande": [
                    {
                        "Numero_ligne": 1,
                        "Code_Produit": "31040N25AA",
                        "Libelle_Produit": "[0715205] MAIS GRAIN NETTOYE 25KG",
                        "Poids_Commande": 160.0
                    }
                ]
            }
        ]
    }
    '''
    
    #print('[INFO] Commande structure:', json.dumps(commande_data, indent=2))

    def envoyer_commande_soap(client, api_key, commande_data, debug=False):
        """
        Fonction optimisée pour envoyer une commande SOAP avec gestion d'erreurs
        
        Args:
            client: Client Zeep
            api_key: Clé API
            commande_data: Données de la commande (dict)
            debug: Active le mode debug pour voir les détails XML
        
        Returns:
            dict: Résultat avec succès/erreur et message
        """
        try:
            # Conversion en JSON string (format attendu par l'API)
            commande_json_str = json.dumps(commande_data, ensure_ascii=False, separators=(',', ':'))
            
            if debug:
                #print(f'[DEBUG] JSON envoyé: {commande_json_str}')
                print('[DEBUG] JSON envoyé')
            
            # Envoi avec raw_response pour capturer les erreurs métier
            with client.settings(raw_response=True):
                #response = client.service.Push_Commandes_Sicalait(
                response = client.service.Push_Commandes(
                    xCleAPI=api_key,
                    jCommande=commande_json_str
                )
                
                if debug:
                    print(f'[DEBUG] Status code: {response.status_code}')
                    print(f'[DEBUG] Raw content: {response.content.decode("utf-8")}')
                
                # Parse de la réponse XML pour extraire le résultat
                if response.status_code == 200:
                    return parser_reponse_soap(response.content.decode('utf-8'))
                else:
                    return {
                        'success': False,
                        'error': f'Erreur HTTP: {response.status_code}',
                        'raw_response': response.content.decode('utf-8')
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'type': type(e).__name__
            }

    def parser_reponse_soap(xml_content):
        """
        Parse la réponse SOAP XML pour extraire le résultat
        
        Args:
            xml_content: Contenu XML de la réponse
            
        Returns:
            dict: Résultat parsé
        """
        try:
            root = ET.fromstring(xml_content)
            
            # Recherche du résultat dans la réponse SOAP
            #result_element = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body/Push_Commandes_SicalaitResult')
            result_element = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body/Push_CommandesResult')
            
            if result_element is not None:
                result_text = result_element.text or ""
                
                # Détection des erreurs métier
                if "ERREUR" in result_text.upper():
                    return {
                        'success': False,
                        'error': result_text,
                        'type': 'BusinessError'
                    }
                else:
                    return {
                        'success': True,
                        'message': result_text,
                        'data': result_text
                    }
            else:
                return {
                    'success': False,
                    'error': 'Impossible de parser la réponse SOAP',
                    'raw_xml': xml_content
                }
                
        except ET.ParseError as e:
            return {
                'success': False,
                'error': f'Erreur de parsing XML: {str(e)}',
                'raw_xml': xml_content
            }

    # ENVOI DE LA COMMANDE
    print('\n' + '='*50)
    print('[INFO] ENVOI DE LA COMMANDE')
    print('='*50)

    resultat = envoyer_commande_soap(
        client=client,
        api_key=API_KEY_URCOOPA,
        commande_data=commande_data,
        debug=True  # Mettre False pour moins de verbosité
    )

    # AFFICHAGE DU RÉSULTAT
    print('\n[RÉSULTAT FINAL]')
    if resultat['success']:
        print('✅ SUCCÈS !')
        print(f'Message: {resultat["message"]}')
        
        #CREER ENVOI CMD BASE DE DONNEES
        from sql.models import CRUD
        crud = CRUD()
        crud.insertCommandeUrcoopaOdoo(commande_data.Code_Client, 
                                    commande_data.Nom_Client, 
                                    commande_data.Email, 
                                    datetime.datetime.now().strftime('%Y/%m/%d'), 
                                    commande_data.Numero_Commande, 
                                    len(commande_data.Ligne_Commande))
        
    else:
        print('❌ ÉCHEC')
        print(f'Type d\'erreur: {resultat.get("type", "Unknown")}')
        print(f'Erreur: {resultat["error"]}')
        
        # Suggestions selon le type d'erreur
        if resultat.get('type') == 'BusinessError':
            if 'déjà enregistrée' in resultat['error']:
                print('\n💡 SOLUTION: Changez le numéro de commande (il existe déjà)')
            elif 'Client N°' in resultat['error']:
                print('\n💡 SOLUTION: Vérifiez le code client dans votre système')
        
    print('\n' + '='*50)