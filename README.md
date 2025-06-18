# 🚀 API Sicalait Urcoopa

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-5.7+-orange.svg)](https://mysql.com)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

> **Interface de synchronisation entre Urcoopa, Gesica et Odoo pour la gestion automatisée des factures et commandes.**

## 🎯 Vue d'ensemble

Cette API FastAPI automatise la synchronisation des données entre trois systèmes critiques :

- **🏢 Urcoopa** - Système de facturation externe (SOAP)
- **📦 Gesica** - Gestion des commandes  
- **⚙️ Odoo** - ERP principal (XML-RPC)

### ✨ Fonctionnalités clés

- 🔄 **Synchronisation automatique** des factures Urcoopa → Odoo
- 📋 **Import des commandes** Gesica → Odoo  
- 📤 **Envoi des commandes** Odoo → Urcoopa
- 🌐 **Interface web** pour la gestion des factures adhérents
- ⏰ **Automatisation CRON** programmable
- 👥 **Gestion différenciée** Adhérents vs Magasins

## 🏗️ Architecture

```mermaid
graph LR
    A[Urcoopa SOAP] --> B[FastAPI]
    C[Gesica DB] --> B
    B --> D[MySQL]
    B --> E[Odoo XML-RPC]
    B --> F[Interface Web]
    
    style B fill:#e1f5fe
    style E fill:#c8e6c9
    style D fill:#fff3e0
```

## ⚡ Quick Start

### 1. **Installation**

```bash
# Cloner le repository
git clone <repository-url>
cd sicalait-urcoopa-api

# Installer les dépendances
pip install -r requirements.txt
```

### 2. **Configuration**

Créer le fichier `.env` :

```env
# Urcoopa API
MY_URCOOPA_URL=https://your-urcoopa-api.com/service.asmx?wsdl
API_KEY_URCOOPA=your_api_key
API_KEY_JOUR=30

# Base de données
MYSQL_HOST=172.17.240.18
MYSQL_DATABASE=exportodoo
MYSQL_USER=root
MYSQL_PASSWORD=your_password

# CRON Planning
CRONTAB_APP_FACTURES=30 14 * * *
CRONTAB_APP_COMMANDES=0 16 * * *
DATE_JOUR=5
```

### 3. **Démarrage**

```bash
# Lancement direct
python main.py

# Ou avec Uvicorn
uvicorn main:app --host 0.0.0.0 --port 9898
```

🌐 **Interface disponible sur :** `http://localhost:9898`

## 📊 Flux de données

### Synchronisation des factures (14h30 quotidien)

```mermaid
sequenceDiagram
    participant C as CRON
    participant A as API
    participant U as Urcoopa
    participant M as MySQL
    participant O as Odoo
    
    C->>A: Déclenchement automatique
    A->>U: Récupération factures (SOAP)
    U-->>A: JSON factures
    A->>M: Sauvegarde/Vérification
    A->>O: Création factures (XML-RPC)
    O-->>A: Confirmation
    A-->>C: Succès
```

### Envoi des commandes (16h00 quotidien)

```mermaid
sequenceDiagram
    participant C as CRON
    participant A as API
    participant O as Odoo
    participant U as Urcoopa
    
    C->>A: Déclenchement automatique
    A->>O: Récupération commandes
    O-->>A: Commandes validées
    A->>A: Construction JSON
    A->>U: Envoi commandes (SOAP)
    U-->>A: Accusé réception
    A-->>C: Succès
```

## 🛠️ API Endpoints

### 🌐 Interface Web

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | `GET` | 🏠 Dashboard principal |
| `/factureAdherentUrcoopa` | `GET` | 📋 Gestion factures adhérents |
| `/valider-facture` | `POST` | ✅ Validation facture |

### 🔄 API Synchronisation

| Route | Méthode | Description |
|-------|---------|-------------|
| `/factures/` | `GET` | 📥 Import factures Urcoopa |
| `/Commandes_Gesica` | `GET` | 📦 Import commandes Gesica |
| `/envoyer-commande/` | `POST` | 📤 Envoi commandes vers Urcoopa |

### 📝 Exemples d'utilisation

```bash
# Récupération manuelle des factures
curl "http://localhost:9898/factures/?xCleAPI=YOUR_KEY&nb_jours=30"

# Envoi des commandes
curl -X POST "http://localhost:9898/envoyer-commande/"

# Import des commandes Gesica
curl "http://localhost:9898/Commandes_Gesica"
```

## 📁 Structure du projet

```
📂 sicalait-urcoopa-api/
├── 📄 main.py                 # 🚀 Application principale
├── 📂 sql/
│   └── 📄 models.py          # 🗃️ Modèles CRUD
├── 📄 createOdoo.py          # 🔧 Création factures Odoo
├── 📄 createOdooGesica.py    # 🔧 Création commandes Gesica
├── 📄 testEnvoiAPI.py        # 📡 Client SOAP
├── 📂 templates/
│   ├── 📄 index.html         # 🏠 Page d'accueil
│   ├── 📄 factures.html      # 📋 Interface factures
│   └── 📄 confirmation.html  # ✅ Page confirmation
├── 📂 static/                # 🎨 Assets statiques
├── 📄 .env                   # ⚙️ Configuration
└── 📄 requirements.txt       # 📦 Dépendances
```

## ⏰ Automatisation CRON

L'application configure automatiquement les tâches CRON :

```bash
# 📥 Récupération factures - 14h30 quotidien
30 14 * * * curl http://localhost:9898/factures/

# 📤 Envoi commandes - 16h00 quotidien  
0 16 * * * curl -X POST http://localhost:9898/envoyer-commande/
```

**Configuration personnalisée :**
```env
CRONTAB_APP_FACTURES=30 14 * * *  # Format cron standard
CRONTAB_APP_COMMANDES=0 16 * * *   # Format cron standard
```

## 🗄️ Base de données

### Tables principales

```mermaid
erDiagram
    sic_urcoopa_facture {
        string Numero_Facture PK
        string Type_Client
        string Code_Client
        string Nom_Client
        decimal Montant_HT
        decimal Montant_TTC
        datetime Date_Facture
        int ID_Facture_ODOO
    }
    
    res_partner {
        int id PK
        string name
        string email
    }
    
    sic_depot {
        int company_id PK
        string code_urcoopa
    }
```

## 🔧 Technologies utilisées

| Technologie | Usage | Version |
|-------------|-------|---------|
| **FastAPI** | Framework web | 0.68+ |
| **Zeep** | Client SOAP | 4.0+ |
| **MySQL Connector** | Base de données | 8.0+ |
| **Pandas** | Traitement données | 1.3+ |
| **Jinja2** | Templates web | 3.0+ |
| **Python-crontab** | Automatisation | 2.5+ |

## 🚀 Déploiement

### 🐳 Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 9898

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9898"]
```

```bash
# Build et run
docker build -t sicalait-api .
docker run -p 9898:9898 sicalait-api
```

### 🔄 Production

```bash
# Avec SSL
uvicorn main:app \
  --host 0.0.0.0 \
  --port 9898 \
  --ssl-certfile server.crt \
  --ssl-keyfile server.key
```

## 📊 Monitoring

### 📝 Logs système

L'application génère des logs détaillés :

```python
📤[INFO] Début connexion odoo
✅ Authentification réussie. UID: 123
📦 Traitement facture F2024001 (15 lignes)
✅📤 Commande Odoo créée ID: 456
❌ Erreur SOAP : Timeout connexion
```

### 🔍 Vérifications de santé

```bash
# Status API
curl http://localhost:9898/

# Vérification base de données
curl http://localhost:9898/factureAdherentUrcoopa
```

## 🛡️ Sécurité

- 🔐 **Authentification API** par clé
- 🔒 **Variables d'environnement** pour credentials
- 🚫 **Validation des entrées** utilisateur
- 📝 **Audit trail** complet
- 🔄 **Retry automatique** en cas d'échec

## 🐛 Dépannage

### Problèmes courants

| Problème | Solution |
|----------|----------|
| ❌ Connexion Odoo | Vérifier URL/credentials dans `.env` |
| ❌ Erreur SOAP Urcoopa | Contrôler `API_KEY_URCOOPA` |
| ❌ Base données MySQL | Vérifier connexion réseau `172.17.240.18:3306` |
| ❌ CRON non exécuté | Redémarrer service cron : `service cron restart` |

### 📞 Debug mode

```bash
# Lancement avec logs détaillés
python main.py --log-level debug

# Test connexions
python -c "from main import *; print('✅ Connexions OK')"
```

## 🤝 Contribution

1. 🍴 **Fork** le repository
2. 🌿 **Créer** une branche feature : `git checkout -b feature/ma-fonctionnalite`
3. ✅ **Commiter** : `git commit -am 'Ajout fonctionnalité'`
4. 📤 **Push** : `git push origin feature/ma-fonctionnalite`
5. 🔄 **Pull Request**

### 📋 Checklist contribution

- [ ] Code testé et fonctionnel
- [ ] Documentation mise à jour
- [ ] Variables d'environnement documentées
- [ ] Logs ajoutés pour traçabilité

## 📜 Changelog

### Version 1.0.0 (Current)
- ✅ Synchronisation factures Urcoopa → Odoo
- ✅ Import commandes Gesica → Odoo
- ✅ Envoi commandes Odoo → Urcoopa
- ✅ Interface web gestion adhérents
- ✅ Automatisation CRON

## 📞 Support

- 📧 **Email :** info.sdpma@sicalait.fr
- 📱 **Téléphone :** +262 XXX XXX XXX
- 🐛 **Issues :** [GitHub Issues](issues)
- 📖 **Wiki :** [Documentation complète](wiki)

## 📄 Licence

**Propriétaire Sicalait** - Tous droits réservés

---

<div align="center">

**🚀 Développé avec ❤️ par l'équipe Sicalait**

*Automatisation • Performance • Fiabilité*

</div>