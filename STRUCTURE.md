# Structure du Projet NexTraction

## 📁 Organisation des Fichiers

```
Nextraction/
├── README.md                    # Documentation principale (reste à la racine)
├── STRUCTURE.md                 # Ce fichier - Structure du projet
├── requirements.txt             # Dépendances Python
├── Dockerfile                   # Configuration Docker
├── docker-compose.yml           # Configuration Docker Compose
├── .env.example                 # Template de variables d'environnement
├── pytest.ini                   # Configuration pytest
├── run.py                       # Script de démarrage
│
├── app/                         # Code source principal
│   ├── __init__.py
│   ├── main.py                  # Point d'entrée FastAPI
│   ├── config.py                # Configuration centralisée
│   ├── models.py                # Modèles de données
│   ├── schemas.py               # Schémas Pydantic
│   │
│   ├── routers/                 # Endpoints API
│   │   ├── __init__.py
│   │   ├── ingest.py            # POST /ingest
│   │   ├── status.py            # GET /status/{job_id}
│   │   ├── ask.py               # POST /ask
│   │   ├── health.py            # GET /health
│   │   └── auth.py              # Authentification
│   │
│   ├── services/               # Logique métier
│   │   ├── __init__.py
│   │   ├── fetcher.py           # Récupération web
│   │   ├── cleaner.py           # Nettoyage HTML et chunking
│   │   ├── embedder.py          # Génération d'embeddings
│   │   ├── vector_store.py      # Stockage vectoriel FAISS
│   │   ├── generator.py         # Génération de réponses
│   │   └── job_manager.py       # Gestion des jobs
│   │
│   ├── auth/                    # Authentification
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── service.py
│   │   └── dependencies.py
│   │
│   ├── middleware/              # Middleware
│   │   ├── __init__.py
│   │   └── rate_limit.py        # Rate limiting
│   │
│   ├── utils/                   # Utilitaires
│   │   ├── __init__.py
│   │   └── logger.py            # Logging structuré
│   │
│   └── static/                  # Fichiers statiques
│       ├── index.html           # Interface web
│       └── presentation.html    # Page de présentation
│
├── tests/                       # Tests automatisés
│   ├── __init__.py
│   ├── conftest.py              # Configuration pytest
│   ├── README.md
│   │
│   ├── unit/                    # Tests unitaires
│   │   ├── __init__.py
│   │   └── test_cleaner.py
│   │
│   └── integration/             # Tests d'intégration
│       ├── __init__.py
│       ├── test_ingest.py
│       ├── test_workflow.py
│       └── test_auth.py
│
├── scripts/                     # Scripts utilitaires
│   ├── README.md
│   ├── evaluation.py            # Script d'évaluation
│   ├── test_ingestion_example.py
│   └── test_workflow_simple.py
│
├── docs/                        # Documentation
│   ├── README.md                # Index de la documentation
│   ├── DESIGN.md                # Document de design
│   │
│   ├── analysis/                # Analyses et audits
│   │   ├── COMPLETENESS_CHECK.md
│   │   ├── CORRECTIONS.md
│   │   ├── PROJECT_ANALYSIS.md
│   │   ├── PROJECT_STATUS.md
│   │   ├── PROJECT_SUMMARY.md
│   │   ├── WORKFLOW_TEST_RESULTS.md
│   │   └── REQUIREMENTS_AUDIT.md
│   │
│   ├── deployment/              # Guides de déploiement
│   │   ├── DEPLOYMENT.md
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   ├── DEPLOY_DOCKER.md
│   │   ├── DEPLOY_INFO.md
│   │   ├── DEPLOY_MAINTENANT.md
│   │   ├── DEPLOY_NOW.md
│   │   ├── DEPLOY_RAILWAY.md
│   │   ├── DEPLOY_RAPIDE.md
│   │   ├── DEPLOY_SANS_DOCKER.md
│   │   ├── FIX_FLY_TIMEOUT.md
│   │   ├── FLY_DEPLOY_FIX.md
│   │   ├── FLY_INSTANCE_GUIDE.md
│   │   ├── INSTALL_DOCKER_WINDOWS.md
│   │   └── RENDER_SETUP.md
│   │
│   ├── guides/                  # Guides d'utilisation
│   │   ├── AUTH_GUIDE.md
│   │   ├── ENDPOINTS_EXPLANATION.md
│   │   ├── FIX_OPENAI_QUOTA.md
│   │   ├── INGESTION_EXAMPLES.md
│   │   ├── NEXT_STEPS.md
│   │   ├── PRESENTATION_GUIDE.md
│   │   ├── QUICK_START.md
│   │   ├── QUICK_TEST.md
│   │   ├── QUICKSTART.md
│   │   ├── SWAGGER_LOGIN_GUIDE.md
│   │   ├── TEST_AUTH.md
│   │   ├── TEST_WORKFLOW_GUIDE.md
│   │   └── VERIFICATION.md
│   │
│   └── misc/                    # Documentation diverse
│       ├── ACTION_PLAN.md
│       ├── OPTIMIZE_BUILD.md
│       └── SOLUTIONS_GRATUITES.md
│
├── deployment/                  # Configurations de déploiement
│   ├── README.md
│   ├── Procfile                 # Heroku/Railway
│   ├── render.yaml              # Render.com
│   ├── railway.json             # Railway
│   └── runtime.txt              # Version Python
│
├── data/                        # Données générées (non versionnées)
│   ├── chunks/                  # Chunks de texte
│   ├── indices/                 # Index FAISS
│   ├── users.json               # Base de données utilisateurs
│   ├── .salt                    # Salt pour mots de passe
│   └── .jwt_secret              # Clé secrète JWT
│
├── venv/                        # Environnement virtuel (non versionné)
├── .gitignore                   # Fichiers ignorés par Git
├── .dockerignore                # Fichiers ignorés par Docker
├── deploy.sh                    # Script de déploiement (Linux/Mac)
└── deploy.bat                   # Script de déploiement (Windows)
```

## 📂 Description des Dossiers

### `/app` - Code Source Principal
Contient tout le code de l'application FastAPI, organisé en modules :
- **routers/** : Définition des endpoints API
- **services/** : Logique métier (fetch, clean, embed, generate)
- **auth/** : Système d'authentification JWT
- **middleware/** : Middleware (rate limiting)
- **utils/** : Utilitaires (logger)

### `/tests` - Tests Automatisés
- **unit/** : Tests unitaires des composants individuels
- **integration/** : Tests d'intégration du workflow complet

### `/scripts` - Scripts Utilitaires
Scripts pour tester et évaluer le système :
- `evaluation.py` : Script d'évaluation avec exemples de questions
- `test_*.py` : Scripts de test

### `/docs` - Documentation
Documentation organisée par catégorie :
- **analysis/** : Analyses, audits, rapports
- **deployment/** : Guides de déploiement pour différentes plateformes
- **guides/** : Guides d'utilisation et tutoriels
- **misc/** : Documentation diverse

### `/deployment` - Configurations de Déploiement
Fichiers de configuration pour différentes plateformes (Render, Railway, Heroku)

### `/data` - Données Générées
Stockage des données générées par l'application (non versionnées) :
- Chunks de texte indexés
- Index FAISS
- Base de données utilisateurs

## 🎯 Fichiers Importants

### À la Racine
- **README.md** : Documentation principale (convention GitHub)
- **STRUCTURE.md** : Ce fichier - Structure du projet
- **requirements.txt** : Dépendances Python
- **Dockerfile** : Configuration Docker
- **docker-compose.yml** : Configuration Docker Compose
- **.env.example** : Template de variables d'environnement

### Documentation Essentielle
- **docs/DESIGN.md** : Architecture et décisions de design
- **docs/analysis/REQUIREMENTS_AUDIT.md** : Audit de conformité
- **docs/guides/QUICK_START.md** : Guide de démarrage rapide

## 📝 Conventions

1. **README.md reste à la racine** : Convention GitHub
2. **Tous les autres .md dans docs/** : Organisation claire
3. **Structure modulaire** : Code organisé par fonctionnalité
4. **Tests séparés** : Tests unitaires et d'intégration séparés
5. **Documentation organisée** : Par catégorie (guides, deployment, analysis)

## 🔍 Navigation

- **Pour commencer** : Lisez `README.md` à la racine
- **Pour comprendre l'architecture** : Lisez `docs/DESIGN.md`
- **Pour déployer** : Consultez `docs/deployment/`
- **Pour utiliser** : Consultez `docs/guides/`
- **Pour vérifier les exigences** : Consultez `docs/analysis/REQUIREMENTS_AUDIT.md`

