# 🚀 Guide de Démarrage Rapide - NexTraction

## ✅ Projet Réorganisé et Prêt !

Votre projet a été réorganisé avec une structure claire. Voici les étapes pour démarrer.

---

## 📋 Checklist de Démarrage

### 1. Vérifier l'Environnement

```bash
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
venv\Scripts\activate.bat     # Windows CMD

# Vérifier Python
python --version  # Doit être 3.11+

# Vérifier les dépendances
pip list | Select-String "fastapi|uvicorn|httpx"
```

### 2. Configurer les Variables d'Environnement

```bash
# Si .env n'existe pas, créer depuis le template
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host ".env créé depuis .env.example"
    Write-Host "⚠️  N'oubliez pas d'éditer .env et d'ajouter vos clés API !"
}

# Éditer .env avec vos clés
notepad .env
```

**Variables importantes à configurer :**
- `OPENAI_API_KEY` : Votre clé API OpenAI (ou utilisez `EMBEDDING_PROVIDER=local`)
- `JWT_SECRET_KEY` : Générer avec `openssl rand -hex 32`
- `PASSWORD_SALT` : Générer avec `openssl rand -hex 16`

### 3. Installer les Dépendances Manquantes (si nécessaire)

```bash
# Installer toutes les dépendances
pip install -r requirements.txt

# Si vous voulez utiliser des embeddings locaux (sans clé API)
pip install sentence-transformers
```

### 4. Démarrer le Serveur

```bash
# Méthode 1 : Script de démarrage
python run.py

# Méthode 2 : Directement avec uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur démarre sur : **http://localhost:8000**

---

## 🧪 Tester l'Application

### Option 1 : Interface Web (Recommandé)

1. Ouvrir dans le navigateur : **http://localhost:8000/**
2. S'inscrire avec un nouveau compte
3. Se connecter
4. Tester l'ingestion :
   - URLs : `https://example.com`
   - Domaines : `example.com`
   - Max pages : `3`
   - Profondeur : `0`
5. Vérifier le statut
6. Poser une question

### Option 2 : API Documentation (Swagger)

1. Ouvrir : **http://localhost:8000/docs**
2. Tester les endpoints directement depuis l'interface Swagger
3. Utiliser le bouton "Authorize" pour ajouter votre token JWT

### Option 3 : Script de Test Automatique

```bash
# Démarrer le serveur dans un terminal
python run.py

# Dans un autre terminal, exécuter le test
python scripts/test_workflow_simple.py
```

---

## 🔍 Vérification Rapide

### Test de Santé

```bash
# Test rapide avec curl (ou dans PowerShell)
Invoke-WebRequest -Uri http://localhost:8000/health -Method GET
```

Devrait retourner : `{"status": "healthy"}`

### Test d'Authentification

```bash
# 1. Inscription
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/auth/register -Method POST -Body $body -ContentType "application/json"

# 2. Connexion
$loginBody = "username=testuser&password=testpass123"
Invoke-WebRequest -Uri http://localhost:8000/auth/login -Method POST -Body $loginBody -ContentType "application/x-www-form-urlencoded"
```

---

## 📁 Structure du Projet

```
Nextraction/
├── app/              # Code source principal
├── tests/            # Tests automatisés
├── docs/             # Documentation complète
├── scripts/          # Scripts utilitaires
├── deployment/       # Configs de déploiement
├── data/             # Données (générées)
└── venv/             # Environnement virtuel
```

**Voir `STRUCTURE.md` pour plus de détails.**

---

## 🐛 Résolution de Problèmes

### Erreur : "Module not found"
```bash
pip install -r requirements.txt
```

### Erreur : "Port 8000 already in use"
```bash
# Changer le port dans run.py ou utiliser :
uvicorn app.main:app --reload --port 8001
```

### Erreur : "OPENAI_API_KEY not found"
```bash
# Option 1 : Ajouter la clé dans .env
# Option 2 : Utiliser des embeddings locaux
pip install sentence-transformers
# Puis dans .env : EMBEDDING_PROVIDER=local
```

### Erreur : "JWT_SECRET_KEY not found"
```bash
# Générer une clé sécurisée
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
# Copier le résultat dans .env
```

---

## 📚 Documentation Disponible

- **README.md** : Documentation principale
- **STRUCTURE.md** : Structure détaillée du projet
- **docs/guides/** : Guides d'utilisation
- **docs/deployment/** : Guides de déploiement
- **docs/analysis/** : Analyses et rapports

---

## 🎯 Prochaines Étapes

Une fois que tout fonctionne localement :

1. **Exécuter les tests** :
   ```bash
   pytest tests/ -v
   ```

2. **Tester avec Docker** :
   ```bash
   docker-compose up --build
   ```

3. **Déployer en production** :
   - Voir `docs/deployment/DEPLOYMENT.md`
   - Configurations disponibles pour Render, Railway, Heroku

4. **Améliorer le projet** :
   - Voir `docs/guides/NEXT_STEPS.md` pour des idées

---

## ✅ Checklist de Vérification

- [ ] Environnement virtuel activé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Fichier `.env` créé et configuré
- [ ] Serveur démarre sans erreur (`python run.py`)
- [ ] Interface web accessible (`http://localhost:8000/`)
- [ ] API docs accessible (`http://localhost:8000/docs`)
- [ ] Test d'inscription/connexion réussi
- [ ] Test d'ingestion réussi
- [ ] Test de question/réponse réussi

---

## 🎉 C'est Parti !

Votre projet est prêt. Commencez par :

```bash
python run.py
```

Puis ouvrez **http://localhost:8000/** dans votre navigateur.

**Bonne chance ! 🚀**

