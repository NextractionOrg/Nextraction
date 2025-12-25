# Guide de Déploiement - NexTraction Web RAG

Ce guide couvre plusieurs options de déploiement pour le projet NexTraction.

## 🚀 Option 1: Railway (Recommandé - Le plus simple)

Railway est gratuit pour commencer et très simple à utiliser.

### Étapes:

1. **Créer un compte sur Railway**
   - Allez sur https://railway.app
   - Connectez-vous avec GitHub

2. **Créer un nouveau projet**
   - Cliquez sur "New Project"
   - Sélectionnez "Deploy from GitHub repo"
   - Choisissez votre repo `Nextraction`

3. **Configurer les variables d'environnement**
   - Dans les settings du projet, ajoutez:
     ```
     OPENAI_API_KEY=votre_clé_api
     EMBEDDING_PROVIDER=openai
     LLM_PROVIDER=openai
     ```

4. **Déploiement automatique**
   - Railway détecte automatiquement le Dockerfile
   - Le déploiement se fait automatiquement à chaque push

**Avantages:** Gratuit au début, déploiement automatique, très simple

---

## 🌐 Option 2: Render

Render offre un plan gratuit avec quelques limitations.

### Étapes:

1. **Créer un compte sur Render**
   - Allez sur https://render.com
   - Connectez-vous avec GitHub

2. **Créer un nouveau Web Service**
   - Cliquez sur "New +" → "Web Service"
   - Connectez votre repo GitHub
   - Sélectionnez le repo `Nextraction`

3. **Configuration**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3

4. **Variables d'environnement**
   - Ajoutez dans "Environment":
     ```
     OPENAI_API_KEY=votre_clé_api
     EMBEDDING_PROVIDER=openai
     LLM_PROVIDER=openai
     PORT=10000
     ```

5. **Déployer**
   - Cliquez sur "Create Web Service"
   - Le déploiement démarre automatiquement

**Avantages:** Plan gratuit disponible, simple à configurer

---

## 🐳 Option 3: Docker sur VPS (DigitalOcean, Linode, etc.)

Pour un contrôle total et des performances optimales.

### Prérequis:
- Un VPS avec Docker et Docker Compose installés
- Un nom de domaine (optionnel mais recommandé)

### Étapes:

1. **Se connecter au VPS**
   ```bash
   ssh user@votre-serveur
   ```

2. **Cloner le repo**
   ```bash
   git clone https://github.com/omarelkhaoudi/Nextraction.git
   cd Nextraction
   ```

3. **Créer le fichier .env**
   ```bash
   cp env.example.txt .env
   nano .env  # Ajoutez vos clés API
   ```

4. **Démarrer avec Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Configurer Nginx (optionnel mais recommandé)**
   ```nginx
   server {
       listen 80;
       server_name votre-domaine.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

**Avantages:** Contrôle total, performances, scalable

---

## ☁️ Option 4: Heroku

Heroku est populaire mais nécessite une carte bancaire pour le plan gratuit.

### Étapes:

1. **Installer Heroku CLI**
   - Téléchargez depuis https://devcenter.heroku.com/articles/heroku-cli

2. **Se connecter**
   ```bash
   heroku login
   ```

3. **Créer l'application**
   ```bash
   heroku create nextraction-rag
   ```

4. **Configurer les variables d'environnement**
   ```bash
   heroku config:set OPENAI_API_KEY=votre_clé_api
   heroku config:set EMBEDDING_PROVIDER=openai
   heroku config:set LLM_PROVIDER=openai
   ```

5. **Déployer**
   ```bash
   git push heroku main
   ```

**Note:** Heroku nécessite un `Procfile` (déjà créé)

---

## 🔧 Option 5: Google Cloud Run (Serverless)

Déploiement serverless avec facturation à l'usage.

### Étapes:

1. **Installer Google Cloud SDK**
   ```bash
   # Suivez les instructions sur https://cloud.google.com/sdk/docs/install
   ```

2. **Créer un projet**
   ```bash
   gcloud projects create nextraction-rag
   gcloud config set project nextraction-rag
   ```

3. **Activer Cloud Run API**
   ```bash
   gcloud services enable run.googleapis.com
   ```

4. **Déployer**
   ```bash
   gcloud run deploy nextraction \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=votre_clé_api
   ```

**Avantages:** Serverless, facturation à l'usage, scalable automatiquement

---

## 📋 Checklist de Déploiement

Avant de déployer, assurez-vous que:

- [ ] Les variables d'environnement sont configurées (OPENAI_API_KEY)
- [ ] Le fichier `.env` n'est pas commité (déjà dans .gitignore)
- [ ] Le Dockerfile fonctionne localement
- [ ] Les tests passent
- [ ] Le port est configuré dynamiquement (utilise `$PORT` ou `0.0.0.0`)

---

## 🔒 Sécurité en Production

1. **Ne jamais commiter les secrets**
   - ✅ Déjà dans .gitignore

2. **Utiliser HTTPS**
   - Configurez un reverse proxy (Nginx) avec SSL

3. **Limiter les CORS**
   - Modifiez `app/main.py` pour restreindre les origines:
   ```python
   allow_origins=["https://votre-domaine.com"]  # Au lieu de ["*"]
   ```

4. **Rate Limiting**
   - ✅ Déjà implémenté

5. **Monitoring**
   - Ajoutez des logs structurés (déjà fait)
   - Configurez des alertes

---

## 🆘 Dépannage

### Le serveur ne démarre pas
- Vérifiez les logs: `docker-compose logs` ou dans l'interface de votre plateforme
- Vérifiez que le port est correctement configuré
- Vérifiez les variables d'environnement

### Erreurs d'import
- Assurez-vous que toutes les dépendances sont dans `requirements.txt`
- Vérifiez la version de Python (3.11+)

### Problèmes de mémoire
- Augmentez la limite de mémoire sur votre plateforme
- Réduisez `max_pages` et `chunk_size` dans la config

---

## 💡 Recommandation

Pour commencer rapidement: **Railway** ou **Render**
Pour production: **VPS avec Docker** ou **Google Cloud Run**

