from .connexion import recupere_connexion_db
import mysql.connector
from mysql.connector import errorcode

# Classe pour le CRUD
class CRUD:
    
    def __init__(self):
        # Initialiser la connexion à la base de données
        self.connexion = recupere_connexion_db()
    
    # METHODE READ FILTRE ADHRENT
    def readFiltreAdherentAvoir(self,):
        cnx = self.connexion
        cursor = cnx.cursor(dictionary=True)  # pour récupérer un dict et comparer facilement
        
        #print(numero_facture)
        try:
            # on execute la requete sur la table sic urcoopa facture where champs adherent
            requete = '''
                    SELECT *
                    FROM exportodoo.sic_urcoopa_facture
                    WHERE Type_Facture = 'A'
                    ORDER BY Date_Echeance DESC
            '''          
            cursor.execute(requete,)
            resultat = cursor.fetchall()
            cursor.close()
            
            return resultat  # soit [] soit un dict complet
        
        except mysql.connector.Error as err:
            print('Erreur :', err)
        
    # METHODE READ FILTRE ADHRENT
    def readFiltreAdherent(self,):
        cnx = self.connexion
        cursor = cnx.cursor(dictionary=True)  # pour récupérer un dict et comparer facilement
        
        #print(numero_facture)
        try:
            # on execute la requete sur la table sic urcoopa facture where champs adherent
            requete = '''
                    SELECT * FROM sic_urcoopa_facture
                    WHERE Type_Client = 'ADHERENT'
                    ORDER BY Date_Echeance ASC
            '''          
            cursor.execute(requete,)
            resultat = cursor.fetchall()
            cursor.close()
            
            return resultat  # soit [] soit un dict complet
        
        except mysql.connector.Error as err:
            print('Erreur :', err)
            
    # Méthode CREATE FACTURE ancien API URCOOPA
    async def create_facture_ancien_api(self, datas: dict):
        
        cnx = self.connexion
        cursor = cnx.cursor()
        
        try:
            colonnes = [
                "Numero_Facture", "Type_Facture", "Date_Facture", "Date_Echeance", 
                "Societe_Facture", "Code_Client", "Nom_Client", "Type_Client", "Montant_HT", 
                "Montant_TTC", "Numero_Ligne_Facture", "Code_Produit", "Libelle_Produit", 
                "Prix_Unitaire", "Quantite_Facturee", "Unite_Facturee", "Numero_Silo", 
                "Montant_HT_Ligne", "Taux_TVA", "Depot_BL", "Numero_BL", "Numero_Ligne_BL", 
                "Commentaires", "Numero_Commande_Client", "Date_Commande_Client", 
                "Numero_Commande_ODOO", "Code_Produit_ODOO", "ID_Produit_ODOO", 
                "Code_Client_ODOO", "ID_Client_ODOO", "Societe_Facture_ODOO", "ID_Facture_ODOO"
            ]

            placeholders = ', '.join(['%s'] * len(colonnes))
            colonnes_str = ', '.join(colonnes)

            insert_query = f'''
                INSERT INTO exportodoo.sic_urcoopa_facture_ancien_api ({colonnes_str})
                VALUES ({placeholders})
            '''

            # Mettre les valeurs dans l'ordre des colonnes
            # Utiliser None pour les valeurs manquantes au lieu de None implicite
            valeurs = tuple(datas.get(colonne, None) for colonne in colonnes)

            cursor.execute(insert_query, valeurs)
            cnx.commit()
            
            return print(f'✅ Insertion réussie - Facture {datas.get("Numero_Facture")} ligne {datas.get("Numero_Ligne_Facture")}')
            
        except mysql.connector.Error as err:
            print(f'❌ Erreur MySQL : {err}')
            cnx.rollback()  # Annuler la transaction en cas d'erreur
            
        except Exception as e:
            print(f'❌ Erreur générale : {e}')
            cnx.rollback()
            
        finally:
            if cursor:
                cursor.close()
    
    # Méthode CREATE
    def create(self, datas: dict):
        
        cnx = self.connexion
        cursor = cnx.cursor()
        
        try:
            colonnes = [
                "Numero_Facture", "Type_Facture", "Date_Facture", "Date_Echeance", 
                "Societe_Facture", "Code_Client", "Nom_Client", "Type_Client", "Montant_HT", 
                "Montant_TTC", "Numero_Ligne_Facture", "Code_Produit", "Libelle_Produit", 
                "Prix_Unitaire", "Quantite_Facturee", "Unite_Facturee", "Numero_Silo", 
                "Montant_HT_Ligne", "Taux_TVA", "Depot_BL", "Numero_BL", "Numero_Ligne_BL", 
                "Commentaires", "Numero_Commande_Client", "Date_Commande_Client", 
                "Numero_Commande_ODOO", "Code_Produit_ODOO", "ID_Produit_ODOO", 
                "Code_Client_ODOO", "ID_Client_ODOO", "Societe_Facture_ODOO", "ID_Facture_ODOO"
            ]

            placeholders = ', '.join(['%s'] * len(colonnes))
            colonnes_str = ', '.join(colonnes)

            insert_query = f'''
                INSERT INTO exportodoo.sic_urcoopa_facture ({colonnes_str})
                VALUES ({placeholders})
            '''

            # Mettre les valeurs dans l'ordre des colonnes
            # Utiliser None pour les valeurs manquantes au lieu de None implicite
            valeurs = tuple(datas.get(colonne, None) for colonne in colonnes)

            cursor.execute(insert_query, valeurs)
            cnx.commit()
            
            return print(f'✅ Insertion réussie - Facture {datas.get("Numero_Facture")} ligne {datas.get("Numero_Ligne_Facture")}')
            
        except mysql.connector.Error as err:
            print(f'❌ Erreur MySQL : {err}')
            cnx.rollback()  # Annuler la transaction en cas d'erreur
            
        except Exception as e:
            print(f'❌ Erreur générale : {e}')
            cnx.rollback()
            
        finally:
            if cursor:
                cursor.close()
    
    # Méthode READ ancien api
    async def read_factures_ancien_api(self, numero_facture : str , ligne : int):
        cnx = self.connexion
        cursor = cnx.cursor(dictionary=True)  # pour récupérer un dict et comparer facilement
        
        #print(numero_facture)
        try:
            query = "SELECT * FROM exportodoo.sic_urcoopa_facture_ancien_api WHERE Numero_Facture = %s AND Numero_Ligne_Facture = %s"
            value = ( numero_facture, ligne,)
            cursor.execute(query, value)
            resultat = cursor.fetchone()
            cursor.close()
            
            return resultat  # soit None soit un dict complet
            
        except mysql.connector.Error as err:
            print('Erreur :', err)
            
    
    # Méthode READ
    async def read(self, numero_facture : str , ligne : int):
        cnx = self.connexion
        cursor = cnx.cursor(dictionary=True)  # pour récupérer un dict et comparer facilement
        
        #print(numero_facture)
        try:
            query = "SELECT * FROM exportodoo.sic_urcoopa_facture WHERE Numero_Facture = %s AND Numero_Ligne_Facture = %s"
            value = ( numero_facture, ligne,)
            cursor.execute(query, value)
            resultat = cursor.fetchone()
            cursor.close()
            
            return resultat  # soit None soit un dict complet
            
        except mysql.connector.Error as err:
            print('Erreur :', err)
            
    
    #Méthode READ ALL
    async def readAll(self,):
        cnx = self.connexion
        cursor = cnx.cursor(dictionary=True)  # pour récupérer un dict et comparer facilement
        
        #print(numero_facture)
        try:
            query = "SELECT * FROM exportgesica.CMD400"
            cursor.execute(query,)
            resultat = cursor.fetchall()
            cursor.close()
            
            return resultat  # soit None soit un dict complet
            
        except mysql.connector.Error as err:
            print('Erreur :', err)
    
    # Méthode UPDATE
    async def updateFacture(self, numero_facture):
        cnx = self.connexion
        cursor = cnx.cursor()
        try:
            vrai = 1
            # Exemple de requête de mise à jour
            update_query = '''
            UPDATE sic_urcoopa_facture 
            SET facture_valider = %s 
            WHERE Numero_Facture = %s
            '''
            valeurs = (vrai,numero_facture,)
            cursor.execute(update_query, valeurs)
            cnx.commit()
            print('Mise à jour réussie')
        except mysql.connector.Error as err:
            print('Erreur :', err)
        finally:
            cursor.close()
    
    # Méthode DELETE
    def delete(self, datas: dict):
        cnx = self.connexion
        cursor = cnx.cursor()
        try:
            # Exemple de requête de suppression
            delete_query = "DELETE FROM ta_table WHERE id = %s"
            valeurs = (datas['id'],)
            cursor.execute(delete_query, valeurs)
            cnx.commit()
            print('Suppression réussie')
        except mysql.connector.Error as err:
            print('Erreur :', err)
        finally:
            cursor.close()
            
    # Méthode comparer champs
    '''
        à faire si besoin pour la partie UPDATE
    '''
    def est_meme_facture(self, db_facture: dict, new_facture: dict) -> bool:
        # Comparer les champs importants
        # ce que qu'on veut vérifier
        champs_a_verifier = [
                    "ID", "Numero_Facture", "Type_Facture", "Date_Facture", "Date_Echeance", 
                    "Societe_Facture", "Code_Client", "Nom_Client", "Type_Client", "Montant_HT", 
                    "Montant_TTC", "Numero_Ligne_Facture", "Code_Produit", "Libelle_Produit", 
                    "Prix_Unitaire", "Quantite_Facturee", "Unite_Facturee", "Numero_Silo", 
                    "Montant_HT_Ligne", "Taux_TVA", "Depot_BL", "Numero_BL", "Numero_Ligne_BL", 
                    "Commentaires", "Numero_Commande_Client", "Date_Commande_Client", 
                    "Numero_Commande_ODOO", "Code_Produit_ODOO", "ID_Produit_ODOO", 
                    "Code_Client_ODOO", "ID_Client_ODOO", "Societe_Facture_ODOO", "ID_Facture_ODOO"
                ]
        
        #print('db _ facture :',db_facture)
        print(type(db_facture))
        print(type(new_facture))
        
        
        for champ in champs_a_verifier:
            print( 'champ : ',champ)
            '''
            if db_facture[champ] != new_facture.get(champ):
                return False  # si un champ est différent
            '''
        return True  # sinon tout est pareil
        
