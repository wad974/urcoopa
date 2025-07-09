from .connexion import recupere_connexion_db
import mysql.connector
from mysql.connector import errorcode

# Classe pour le CRUD
class CRUD:
    
    def __init__(self):
        # Initialiser la connexion à la base de données
        self.connexion = recupere_connexion_db()
        
    #METHODE PROCEDURE 
    async def procedureUrcoopa(self):
        
        cnx = self.connexion
        cursor = cnx.cursor(dictionary=True)

        # Appel de la procédure stockée
        cursor.callproc("URCOOPA_PREPA_FACTURES")

        # Récupérer les résultats de la procédure
        for result in cursor.stored_results():
            data = result.fetchall()

        cursor.close()
        cnx.close()
        return data
    
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
            cnx.close()
            
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
                    SELECT * FROM exportodoo.sic_urcoopa_facture
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
    async def create_facture_ancien_api(self, row: dict):
        
        cnx = self.connexion
        cursor = cnx.cursor()
        
        try:
            
            nameChamps = '''
            SELECT distinct COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'sic_urcoopa_facture_ancien_api' and COLUMN_KEY<>'PRI';
            '''

            cursor.execute(nameChamps)
            dataName = cursor.fetchall()
            
            columnChamp = []
            for colonne in dataName:
                columnChamp.append(colonne[0])
            

            # Filtrer les données de 'row' pour ne garder que les colonnes existantes
            valeurs_filtrees = []
            colonnes_utilisees = []
            
            for colonne in columnChamp:
                if colonne in row:
                    valeurs_filtrees.append(row[colonne])
                    colonnes_utilisees.append(colonne)
                else:
                    # Optionnel: ajouter une valeur par défaut (NULL)
                    valeurs_filtrees.append(None)
                    colonnes_utilisees.append(colonne)
            
            # Construire la requête d'insertion
            colonnes_str = ', '.join(colonnes_utilisees)
            placeholders = ', '.join(['%s'] * len(valeurs_filtrees))
            
            insert_query = f'''
                INSERT INTO exportodoo.sic_urcoopa_facture ({colonnes_str})
                VALUES ({placeholders})
            '''
            
            #print('Requête SQL:', insert_query)
            #print('Valeurs:', valeurs_filtrees)
            
            # Exécuter l'insertion
            cursor.execute(insert_query, tuple(valeurs_filtrees))
            cnx.commit()
            
            cursor.close()
            return print(f'✅ Insertion réussie - Facture {row.get("Numero_Facture")} ligne {row.get("Numero_Ligne_Facture")}')
            
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
    async def create(self, datas: dict):
        
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
            
            datas = cursor.fetchall()
            
            cursor.close()
            
            print('il y quoi dans datas : ' , datas)
            return datas
            return print(f'✅ Insertion réussie - Facture {datas.get("Numero_Facture")} ligne {datas.get("Numero_Ligne_Facture")}')
            
        except mysql.connector.Error as err:
            print(f'❌ Erreur MySQL : {err}')
            cnx.rollback()  # Annuler la transaction en cas d'erreur
            
        except Exception as e:
            print(f'❌ Erreur générale : {e}')
            cnx.rollback()
        '''  
        finally:
            if cursor:
                try:
                    cursor.fetchall()  # au cas où il reste un SELECT en attente
                except:
                    pass  # ignore si ce n’est pas un SELECT
                cursor.close()
            if cnx:
                cnx.close()
        ''' 
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
        #print(numero_facture)
        cnx = self.connexion
        if not cnx:
            raise Exception("❌ Connexion MySQL non disponible")
        
        cursor = cnx.cursor(dictionary=True)  # pour récupérer un dict et comparer facilement
        
        try:
            query = '''
                SELECT Numero_Facture, Numero_Ligne_Facture
                FROM exportodoo.sic_urcoopa_facture 
                WHERE Numero_Facture = %s AND Numero_Ligne_Facture = %s
            '''
            value = (numero_facture, ligne,)
            
            cursor.execute(query, value)
            resultat = cursor.fetchone()
            
            # IMPORTANT: Consommer tous les résultats restants
            # Ceci évite l'erreur "Unread result found"
            while cursor.nextset():
                pass
            
            return resultat  # soit None soit un dict complet
        
        except mysql.connector.Error as e:
            print(f"[ERROR] Erreur MYSQL lors de la lecture de la facture {numero_facture}, ligne {ligne}: {e}")
            raise e
        except Exception as e:
            print(f"[ERROR] Erreur lors de la lecture de la facture {numero_facture}, ligne {ligne}: {e}")
            raise e
            
        finally:
            # Fermer proprement le curseur
            cursor.close()
            # Note: Ne pas fermer la connexion ici si elle est réutilisée ailleurs
            # cnx.disconnect()  # Décommentez si vous voulez fermer la connexion
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
        
