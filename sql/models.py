from .connexion import recupere_connexion_db
import mysql.connector
from mysql.connector import errorcode
import json
# Classe pour le CRUD
class CRUD:
    
    def __init__(self):
        
        # Initialiser la connexion à la base de données
        self.connexion = recupere_connexion_db()
        
        # Ajoutez cette méthode dans votre classe CRUD
    
    def save_non_correspondances(self, urcoopa_only, odoo_only, only_CodeProduct_in_urcoopa, only_ProductCode_in_odoo):
        """Sauvegarde les non-correspondances dans la table"""
        db = self.connexion
        cursor = db.cursor()
        
        # Vider la table avant insertion
        cursor.execute("TRUNCATE TABLE exportodoo.sic_urcoopa_non_correspondance")
        
        # Insérer ceux qui sont seulement dans Urcoopa
        for nom in urcoopa_only:
            cursor.execute("""
                INSERT INTO exportodoo.sic_urcoopa_non_correspondance 
                (Nom_Adherent_Urcoopa, Nom_Adherent_Odoo)
                VALUES (%s, NULL)
            """, (nom,))
        
        # Insérer ceux qui sont seulement dans Odoo
        for nom in odoo_only:
            cursor.execute("""
                INSERT INTO exportodoo.sic_urcoopa_non_correspondance 
                (Nom_Adherent_Urcoopa, Nom_Adherent_Odoo)
                VALUES (NULL, %s)
            """, (nom,))
            
        # Insérer Numéros Articles ceux qui sont seulement dans Urcoopa
        for numero in only_CodeProduct_in_urcoopa:
            cursor.execute("""
                INSERT INTO exportodoo.sic_urcoopa_non_correspondance 
                (Nom_Adherent_Urcoopa, Nom_Adherent_Odoo)
                VALUES (NULL, %s)
            """, (numero,))
            
        # Insérer Numéros Articles ceux qui sont seulement dans Urcoopa
        for numero in only_ProductCode_in_odoo:
            cursor.execute("""
                INSERT INTO exportodoo.sic_urcoopa_non_correspondance 
                (Nom_Adherent_Urcoopa, Nom_Adherent_Odoo)
                VALUES (NULL, %s)
            """, (numero,))
        
        db.commit()
        cursor.close()
        db.close()
        print(f"\n✅ {len(urcoopa_only) + len(odoo_only)} non-correspondances sauvegardées")

    def readDonneesComptables(self, date_debut: str = None, date_fin: str = None):
        """
        Récupère les données comptables pour l'écriture TVA
        Args:
            date_debut: Date de début au format 'YYYY-MM-DD' (ex: '2025-07-01')
            date_fin: Date de fin au format 'YYYY-MM-DD' (ex: '2025-07-31')
        """
        cnx = None
        cursor = None
        
        try:
            # Créer une nouvelle connexion pour éviter les conflits
            cnx = recupere_connexion_db()
            cursor = cnx.cursor(dictionary=True)
            
            # Si pas de dates fournies, utiliser le mois en cours
            if not date_debut or not date_fin:
                from datetime import datetime
                now = datetime.now()
                date_debut = f"{now.year}-{now.month:02d}-01"
                # Dernier jour du mois
                if now.month == 12:
                    date_fin = f"{now.year + 1}-01-01"
                else:
                    date_fin = f"{now.year}-{now.month + 1:02d}-01"
            
            '''
            REQUTE POUR TVA ET HT
            
            
            SELECT left(Date_Facture,7) mois_facture, Type_Facture ,
            (case when Code_Produit='INTR' then 'INTR' else '' end) est_intr,
            sum(Montant_HT_Ligne) total_HT
            #sum(Montant_HT_Ligne*Taux_TVA/100) total_TVA                
            FROM exportodoo.sic_urcoopa_facture
            where Societe_Facture ='VRAC'
            and left(Code_Client,1)='5'
            and Date_Facture>=%s
            and Date_Facture<=%s
            and Nom_Client not in (select Nom_Client from exportodoo.sic_urcoopa_Exclution_mois where mois_facture=left(sic_urcoopa_facture.Date_Facture,7))
            group by left(Date_Facture,7), Type_Facture, (case when Code_Produit='INTR' then 'INTR' else '' end)
        
            
            '''
            
            
            requete ='''
                SELECT left(Date_Facture,7) mois_facture, Type_Facture ,
                (case when Code_Produit='INTR' then 'INTR' else '' end) est_intr,
                sum(Montant_HT_Ligne) total_HT             
                FROM exportodoo.sic_urcoopa_facture
                where Societe_Facture ='VRAC'
                and left(Code_Client,1)='5'
                and Date_Facture>=%s
                and Date_Facture<=%s
                and Nom_Client not in (select Nom_Client from exportodoo.sic_urcoopa_Exclution_mois where mois_facture=left(sic_urcoopa_facture.Date_Facture,7))
                group by left(Date_Facture,7), Type_Facture, (case when Code_Produit='INTR' then 'INTR' else '' end)
                '''
            
            
            # Correction du paramètre pour le nom client
            cursor.execute(requete, (date_debut, date_fin,))
            resultatHT = cursor.fetchall()
            
            cursor.close()
            cnx.close()
            
            #print('VRAC => ', resultatHT)
            
            cnx = recupere_connexion_db()
            cursor = cnx.cursor(dictionary=True)
            
            requete2 ='''
                SELECT left(Date_Facture,7) mois_facture, sum(Montant_HT_Ligne*Taux_TVA/100) total_TVA
                FROM exportodoo.sic_urcoopa_facture
                where Societe_Facture ='VRAC'
                and left(Code_Client,1)='5'
                and Date_Facture>=%s
                and Date_Facture<=%s
                and Nom_Client not in (select Nom_Client from exportodoo.sic_urcoopa_Exclution_mois where mois_facture=left(sic_urcoopa_facture.Date_Facture,7))
                group by left(Date_Facture,7)
                '''
            
            
            # Correction du paramètre pour le nom client
            cursor.execute(requete2, (date_debut, date_fin,))
            resultatTVA = cursor.fetchall()
            
            cursor.close()
            cnx.close()
            
            print('VRAC => ', resultatTVA)
            
            # Créer un dictionnaire des TVA par mois pour faciliter la fusion
            tva_par_mois = {row['mois_facture']: row['total_TVA'] for row in resultatTVA}

            # Regrouper les résultats
            resultat = []
            for row in resultatHT:
                mois = row['mois_facture']
                resultat.append({
                    'mois_facture': mois,
                    'Type_Facture': row['Type_Facture'],
                    'est_intr': row['est_intr'],
                    'total_HT': row['total_HT'],
                    'total_TVA': tva_par_mois.get(mois, 0)  # TVA du mois complet
                })

            print('VRAC => ', resultat)
            
            #Consommer tous les résultats restants
            while cursor.nextset():
                pass
                
            return resultat
            
        except mysql.connector.Error as err:
            print(f'Erreur MySQL lors de la récupération des données comptables : {err}')
            return []
        except Exception as e:
            print(f'Erreur générale lors de la récupération des données comptables : {e}')
            return []
        finally:
            # Fermer proprement les ressources
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if cnx:
                try:
                    cnx.close()
                except:
                    pass
            
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
    async def read_livraison(self, numero_facture : str , ligne : int):
        cnx = self.connexion
        cursor = cnx.cursor(dictionary=True)  # pour récupérer un dict et comparer facilement
        
        #print(numero_facture)
        try:
            query = "SELECT * FROM exportodoo.sic_urcoopa_livraison WHERE Numero_BL = %s AND Numero_Ligne_BL = %s"
            value = ( numero_facture, ligne,)
            cursor.execute(query, value)
            resultat = cursor.fetchone()
            cursor.close()
            
            return resultat  # soit None soit un dict complet
            
        except mysql.connector.Error as err:
            print('Erreur :', err)
            
    
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
        
    #METHODE INSERT CORRESPONDANCE ARTICLES
    
    def insertArticleCorrespondance(self, code_produit):
        
        try:
            #code produit qui ne sont pas matcher avec Urcoopa<->Odoo envoyer dans Base de données
            cnx = self.connexion
            cursor = cnx.cursor()
            
            #on controle d'abord qu'il y a pas la meme donnees
            ctrl = '''
            SELECT Numero_Article_Urcoopa
            FROM exportodoo.sic_urcoopa_non_correspondance_article
            WHERE Numero_Article_Urcoopa = %s
            '''
            ctrl_code = (code_produit,)
            cursor.execute(ctrl, ctrl_code)
            response = cursor.fetchone()
            if response is None:
                
                print('[INFO] Aucun code produit trouvé')
                requete = '''
                    insert into exportodoo.sic_urcoopa_non_correspondance_article (Numero_Article_Urcoopa)
                    values (%s)
                '''
                valeurs = ( code_produit,)
                cursor.execute(requete, valeurs)
                cnx.commit()
                
                cursor.close()
                cnx.close()
                print(f'✅ [SUCCESS] code produit manquant dans database')
            
            else :
                print(f"❌ [ERREUR] {code_produit} DEJA DANS DATABASE")
        except :
            print(f"❌ [ERREUR] {code_produit} COMMIT DANS DATABASE")
            
            
    #METHODE INSERT CORRESPONDANCE ADHERENT
    def insertAdherentCorrespondance(self, nom_adherent):
        
        #code produit qui ne sont pas matcher avec Urcoopa<->Odoo envoyer dans Base de données
        cnx = self.connexion
        cursor = cnx.cursor()
        
        try:
            
            #on controle d'abord qu'il y a pas la meme donnees
            ctrl = '''
            SELECT Nom_Adherent_Urcoopa
            FROM exportodoo.sic_urcoopa_non_correspondance_adherent
            WHERE Nom_Adherent_Urcoopa = %s
            '''
            ctrl_code = (nom_adherent,)
            cursor.execute(ctrl, ctrl_code)
            response = cursor.fetchone()
            if response is None:
                
                print('[INFO] Aucun adherent trouvé')
                requete = '''
                    insert into exportodoo.sic_urcoopa_non_correspondance_adherent (Nom_Adherent_Urcoopa)
                    values (%s)
                '''
                valeurs = ( nom_adherent,)
                cursor.execute(requete, valeurs)
                cnx.commit()
                
                cursor.close()
                cnx.close()
                print(f'✅ [SUCCESS] Adherent manquant dans database')
            
            else :
                print(f"❌ [ERREUR] {nom_adherent} DEJA DANS DATABASE")
        except :
            print(f"❌ [ERREUR] {nom_adherent} COMMIT DANS DATABASE")
            
    #METHODE UPDATE SIC URCOOPA FACTURE
    def updateSicUrcoopaFacture(self, Numero_Facture):
        try:
            cnx = self.connexion
            cursor = cnx.cursor()
            
            Nouveau_status_bdd = 'déjà traiter'
            
            requete = '''
                update exportodoo.sic_urcoopa_facture 
                set Statut_Correspondance_Article = %s , Statut_Correspondance_Adherent = %s
                where Numero_Facture = %s
            '''
            
            valeursUpdate = ( Nouveau_status_bdd, Nouveau_status_bdd, Numero_Facture,)
            cursor.execute(requete,valeursUpdate)
            cnx.commit()
            
            return print(f"✅📤 [SUCCESS] Facture Mise à jour réussie dans la base de données \n\n")
        except:
            print(f"❌ [ERREUR] {Numero_Facture} UDAPTE DANS DATABASE")
            
    #METHODE UPDATE SIC URCOOPA FACTURE INTEGRATIOON ODOO
    def UpdateStatutIntegrationFactureOdoo(self, Numero_Facture):
        try:
            cnx = self.connexion
            cursor = cnx.cursor()
            
            Nouveau_status_bdd = 'intégré'
            
            requete = '''
                update exportodoo.sic_urcoopa_facture 
                set Statut_Integration_Fac_inOdoo = %s
                where Numero_Facture = %s
            '''
            
            valeursUpdate = ( Nouveau_status_bdd, Numero_Facture,)
            cursor.execute(requete,valeursUpdate)
            cnx.commit()
            
            return print(f"✅📤 [SUCCESS] Facture Mise à jour dans base de données \n\n")
        except:
            print(f"❌ [ERREUR] {Numero_Facture} UDAPTE DANS DATABASE")
            
            
    #METHODE INSERT COMMANDE URCOOPA PASSER PAR LES MAGASINS
    def insertCommandeUrcoopaOdoo(self, 
                                Code_Client, 
                                Nom_Client, 
                                Email, 
                                date_commande, 
                                Numero_Commande, 
                                Nombre_Commande):
        
        try:
            print('[INFO] DEBUT INSERTION')
            #code produit qui ne sont pas matcher avec Urcoopa<->Odoo envoyer dans Base de données
            cnx = self.connexion
            cursor = cnx.cursor()
            
            #on controle d'abord qu'il y a pas les memes donnees
            req_ctrl = '''
            SELECT Numero_Commande
            FROM exportodoo.sic_urcoopa_commande_odoo
            WHERE Numero_Commande = %s
            '''
            req_ctrl_commande = (Numero_Commande,)
            cursor.execute(req_ctrl, req_ctrl_commande)
            response = cursor.fetchone()
            print('[INFO] RESPONSE : ', response)
            
            if response is None:
                
                print('[INFO] Aucun Numero de commande trouvé')
                #print('[INFO] code client : ', Code_Client, ' Nom_client : ', Nom_Client, ' email : ', Email, ' date_commande : ', date_commande, ' Numero_commande : ', Numero_Commande , 'nombre de commande : ', Nombre_Commande)
                requete = '''
                    insert into exportodoo.sic_urcoopa_commande_odoo(Code_Client, Nom_Client, Email, date_envoi_commande, Numero_Commande, Nombre_Article)
                    values (%s,%s,%s,%s,%s,%s)
                '''
                valeurs = ( Code_Client, Nom_Client, Email, date_commande, Numero_Commande, Nombre_Commande, )
                cursor.execute(requete, valeurs)
                cnx.commit()
                
                cursor.close()
                cnx.close()
                
                print(f'✅ [SUCCESS] Commande inséré dans database')
            
            else :
                print(f"❌ [ERREUR] {Numero_Commande} DEJA DANS DATABASE")
        except :
            print(f"❌ [ERREUR] {Numero_Commande} COMMIT DANS DATABASE")
    
    #METHODE INSERT COMMANDE URCOOPA PASSER PAR LES MAGASINS
    def readInconnu(self, ):
        
        cnx = None
        cursor = None
        
        try:
            
            cnx = self.connexion
            cursor = cnx.cursor(dictionary=True)
            
            #print('ETAPE DEMARRAGE')
            #code produit qui ne sont pas matcher avec Urcoopa<->Odoo envoyer dans Base de données
            
            #print('ETAPE 1')
            #on controle d'abord qu'il y a pas les memes donnees
            
            requete_client = '''
                select Nom_Adherent_Urcoopa from  exportodoo.sic_urcoopa_non_correspondance_adherent
            '''
            
            requete = '''
                SELECT distinct Code_Produit ,Nom_Client, Type_Facture , Code_Client 
                FROM exportodoo.sic_urcoopa_facture
                where Nom_Client in (select Nom_Adherent_Urcoopa from  exportodoo.sic_urcoopa_non_correspondance_adherent )
                and Code_Produit in (select Numero_Article_Urcoopa  from exportodoo.sic_urcoopa_non_correspondance_article sunca )
            '''
            
            cursor.execute(requete)
            #print('ETAPE 2')
            
            datas  = cursor.fetchall()
            #print('DATAS READINCONNU : ', datas)
            
            cursor.close()
            
            print(f'✅ [SUCCESS] LISTE RECUPERER DANS DATABASE')
            
            if datas is None:
                return []
            else:
                return datas
        except :
            print(f"❌ [ERREUR] LORS DE LA RECUPERATION DES DATAS")
        
    #METHODE CLIENT NON RECONNU URCOOPA PASSER PAR LES MAGASINS
    def readClientNonReconnu(self, ):
        
        cnx = None
        cursor = None
        
        try:
            
            cnx = self.connexion
            cursor = cnx.cursor(dictionary=True)
            
            #print('ETAPE DEMARRAGE')
            #code produit qui ne sont pas matcher avec Urcoopa<->Odoo envoyer dans Base de données
            
            #print('ETAPE 1')
            #on controle d'abord qu'il y a pas les memes donnees
            
            requete_client = '''
                select Nom_Adherent_Urcoopa from  exportodoo.sic_urcoopa_non_correspondance_adherent
            '''
            
            
            cursor.execute(requete_client)
            #print('ETAPE 2')
            
            datas  = cursor.fetchall()
            #print('DATAS READINCONNU : ', datas)
            
            cursor.close()
            
            print(f'✅ [SUCCESS] LISTE RECUPERER DANS DATABASE')
            
            if datas is None:
                return []
            else:
                return datas
        except :
            print(f"❌ [ERREUR] LORS DE LA RECUPERATION DES DATAS")
            
    #METHODE INSERT COMMANDE URCOOPA PASSER PAR LES MAGASINS
    def readArticleNonReconnu(self, ):
        
        cnx = None
        cursor = None
        
        try:
            
            cnx = self.connexion
            cursor = cnx.cursor(dictionary=True)
            
            #print('ETAPE DEMARRAGE')
            #code produit qui ne sont pas matcher avec Urcoopa<->Odoo envoyer dans Base de données
            
            #print('ETAPE 1')
            #on controle d'abord qu'il y a pas les memes donnees
            
            requete_client = '''
                select Numero_Article_Urcoopa from  exportodoo.sic_urcoopa_non_correspondance_article
            '''
            
            
            cursor.execute(requete_client)
            #print('ETAPE 2')
            
            datas  = cursor.fetchall()
            #print('DATAS READINCONNU : ', datas)
            
            cursor.close()
            
            print(f'✅ [SUCCESS] LISTE RECUPERER DANS DATABASE')
            
            if datas is None:
                return []
            else:
                return datas
        except :
            print(f"❌ [ERREUR] LORS DE LA RECUPERATION DES DATAS")
    
    ######################################################
    ######################################################
    #STATISTIQUE - PARTIE
    #METHODE COUNT COMMANDE URCOOPA PASSER PAR LES MAGASINS
    def countCommandesEnvoyees(self, ):
        
        cnx = None
        cursor = None
        
        try:
            
            cnx = self.connexion
            cursor = cnx.cursor(dictionary=True)
            
            requete_client = '''
                SELECT count(id) as commande
                FROM exportodoo.sic_urcoopa_commande_odoo;
            '''
            
            cursor.execute(requete_client)
            
            datas  = cursor.fetchall()
            
            cursor.close()
            
            print(f'✅ [SUCCESS] LISTE RECUPERER countCommandesEnvoyees DANS DATABASE')
            
            if datas is None:
                return []
            else:
                return datas[0]
        except :
            print(f"❌ [ERREUR] LORS DE LA RECUPERATION DES DATAS")
            
    #METHODE COUNT COMMANDE URCOOPA PASSER PAR LES MAGASINS
    def countFacturesRecuperees(self, ):
        
        cnx = None
        cursor = None
        
        try:
            
            cnx = self.connexion
            cursor = cnx.cursor()
            
            requete_client = '''
                SELECT COUNT(DISTINCT Numero_Facture) as numero_facture
                FROM exportodoo.sic_urcoopa_facture
                WHERE Type_Facture = 'F';
            '''
            
            cursor.execute(requete_client)
            
            datas  = cursor.fetchall()
            
            cursor.close()
            
            print(f'✅ [SUCCESS] LISTE RECUPERER countFacturesRecuperees DANS DATABASE')
            
            if datas is None:
                return []
            else:
                return datas[0]
        except :
            print(f"❌ [ERREUR] LORS DE LA RECUPERATION DES DATAS")
            
    #METHODE COUNT COMMANDE URCOOPA PASSER PAR LES MAGASINS
    def countAvoirsRecuperees(self, ):
        
        cnx = None
        cursor = None
        
        try:
            
            cnx = self.connexion
            cursor = cnx.cursor(dictionary=True)
            
            requete_client = '''
                SELECT COUNT(DISTINCT Numero_Facture) AS total_avoirs
                FROM exportodoo.sic_urcoopa_facture
                WHERE Type_Facture = 'A';
            '''
            
            cursor.execute(requete_client)
            
            datas  = cursor.fetchall()
            
            cursor.close()
            
            print(f'✅ [SUCCESS] LISTE RECUPERER countAvoirsRecuperees DANS DATABASE')
            
            if datas is None:
                return []
            else:
                return datas[0]
        except :
            print(f"❌ [ERREUR] LORS DE LA RECUPERATION DES DATAS")
            
    #METHODE COUNT COMMANDE URCOOPA PASSER PAR LES MAGASINS
    def countAdherentsOdoo(self, ):
        
        cnx = None
        cursor = None
        
        try:
            
            cnx = self.connexion
            cursor = cnx.cursor(dictionary=True)
            
            requete_client = '''
                SELECT count(distinct Code_Client ) as code_client
                FROM exportodoo.sic_urcoopa_facture
                where Societe_Facture = 'VRAC'
                and left(Code_Client, 1) <> '5'
            '''
            
            cursor.execute(requete_client)
            
            datas  = cursor.fetchall()
            
            cursor.close()
            
            print(f'✅ [SUCCESS] LISTE RECUPERER countAdherentsOdoo DANS DATABASE')
            
            if datas is None:
                return []
            else:
                return datas[0]
        except :
            print(f"❌ [ERREUR] LORS DE LA RECUPERATION DES DATAS")
            
    #METHODE COUNT COMMANDE URCOOPA PASSER PAR LES MAGASINS
    def countClientsVrac(self, ):
        
        cnx = None
        cursor = None
        
        try:
            
            cnx = self.connexion
            cursor = cnx.cursor(dictionary=True)
            
            requete_client = '''
                SELECT count(distinct Code_Client ) as code_client
                FROM exportodoo.sic_urcoopa_facture
                where Societe_Facture = 'VRAC'
                and left(Code_Client, 1) = '5'
            '''
            
            cursor.execute(requete_client)
            
            datas  = cursor.fetchall()
            
            cursor.close()
            
            print(f'✅ [SUCCESS] LISTE RECUPERER countClientsVrac DANS DATABASE')
            
            if datas is None:
                return []
            else:
                return datas[0]
        except :
            print(f"❌ [ERREUR] LORS DE LA RECUPERATION DES DATAS")
            
    #METHODE COUNT COMMANDE URCOOPA PASSER PAR LES MAGASINS
    def countLivraisons(self, ):
        
        cnx = None
        cursor = None
        
        try:
            
            cnx = self.connexion
            cursor = cnx.cursor(dictionary=True)
            
            requete_client = '''
                select count(distinct Numero_BL) as numero_bl
                FROM exportodoo.sic_urcoopa_livraison;
            '''
            
            cursor.execute(requete_client)
            
            datas  = cursor.fetchall()
            
            cursor.close()
            
            print(f'✅ [SUCCESS] LISTE RECUPERER countLivraisons DANS DATABASE')
            
            if datas is None:
                return []
            else:
                return datas[0]
        except :
            print(f"❌ [ERREUR] LORS DE LA RECUPERATION DES DATAS")