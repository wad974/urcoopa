import mysql.connector
import os
from dotenv import load_dotenv

#on init les variables d'environnement pour connexion base de données
load_dotenv()

'''
def recupere_connexion_db() :
    #connexion au serveur
    login  = mysql.connector.connect(
        host= os.getenv('DB_URL_HOST'), 
        port= os.getenv('DB_URL_PORT'),
        user= os.getenv('DB_URL_USER'),
        password= os.getenv('DB_URL_PASSWORD'),
        database= os.getenv('DB_URL_DATABASE')
    )
    
    return login
'''

import logging
import time

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Also log to a file
file_handler = logging.FileHandler("cpy-errors.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) 

def recupere_connexion_db(attempts=3, delay=2):
    attempt = 1
    #connexion au serveur
    config  = mysql.connector.connect(
        host= os.getenv('DB_URL_HOST'), 
        port= os.getenv('DB_URL_PORT'),
        user= os.getenv('DB_URL_USER'),
        password= os.getenv('DB_URL_PASSWORD'),
        database= os.getenv('DB_URL_DATABASE')
    )
    
    
    # Implement a reconnection routine
    while attempt < attempts + 1:
        try:
            return config
        except (mysql.connector.Error, IOError) as err:
            if (attempts is attempt):
                # Attempts to reconnect failed; returning None
                logger.info("Failed to connect, exiting without a connection: %s", err)
                return None
            logger.info(
                "Connection failed: %s. Retrying (%d/%d)...",
                err,
                attempt,
                attempts-1,
            )
            # progressive reconnect delay
            time.sleep(delay ** attempt)
            attempt += 1
    return None