# Structure du Projet NexTraction

## Vue d'ensemble

```
Nextraction/
├── app/                    # Code source de l'application
│   ├── auth/               # Authentification JWT
│   │   ├── __init__.py
│   │   ├── dependencies.py # Dépendances FastAPI pour l'auth
│   │   ├── models.py       # Modèles Pydantic (User, Token, etc.)
│   │   └── service.py      # Service d'authentification (hash, JWT)
│   │
│   ├── middleware/         # Middleware FastAPI
│   │   ├── __init__.py
│   │   └── rate_limit.py   # Rate limiting middleware
│   │
│   ├── routers/            # Endpoints API FastAPI
│   │   ├── __init__.py
│   │   ├── auth.py         # Routes d'authentification (/auth/*)
│   │   ├── ingest.py        # Route POST /ingest
│   │   ├── status.py        # Route GET /status/{job_id}
│   │   ├── ask.py           # Route POST /ask
│   │   └── health.py        # Route GET /health
│   │
│   ├── services/           # Services métier (RAG pipeline)
│   │   ├── __init__.py
│   │   ├── fetcher.py      # Web crawling
│   │   ├── cleaner.py      # HTML cleaning et chunking
│   │   ├── embedder.py     # Génération d'embeddings
│   │   ├── vector_store.py # Stockage vectoriel FAISS
│   │   ├── generator.py    # Génération de réponses avec citations
│   │   └── job_manager.py  # Gestion des jobs d'ingestion
│   │
│   ├── static/             # Interface web (HTML/CSS/JS)
│   │   └── index.html      # Interface utilisateur complète
│   │
│   ├── utils/              # Utilitaires
│   │   ├── __init__.py
│   │   └── logger.py       # Configuration du logging structuré
│   │
│   ├── config.py           # Configuration (Pydantic Settings)
│   ├── main.py             # Point d'entrée FastAPI
│   ├── models.py           # Modèles de données (JobState, etc.)
│   └── schemas.py          # Schémas Pydantic pour les requêtes/réponses
│
├── tests/                  # Tests automatisés
│   ├── unit/               # Tests unitaires
│   │   ├── __init__.py
│   │   └── test_cleaner.py # Tests du service de nettoyage
│   │
│   ├── integration/        # Tests d'intégration
│   │   ├── __init__.py
│   │   ├── test_auth.py    # Tests d'authentification
│   │   ├── test_ingest.py  # Tests d'ingestion
│   │   └── test_workflow.py # Tests du workflow complet
│   │
│   ├── conftest.py         # Configuration pytest et fixtures
│   ├── run_all_tests.py    # Script pour exécuter tous les tests
│   └── README.md           # Documentation des tests
│
├── docs/                   # Documentation
│   ├── guides/             # Guides d'utilisation
│   │   ├── AUTH_GUIDE.md
│   │   ├── ENDPOINTS_EXPLANATION.md
│   │   ├── NEXT_STEPS.md
│   │   ├── QUICKSTART.md
│   │   ├── QUICK_TEST.md
│   │   ├── SWAGGER_LOGIN_GUIDE.md
│   │   ├── TEST_AUTH.md
│   │   ├── TEST_WORKFLOW_GUIDE.md
│   │   └── VERIFICATION.md
│   │
│   ├── deployment/         # Documentation de déploiement
│   │   └── DEPLOYMENT.md
│   │
│   ├── analysis/           # Analyses et rapports
│   │   ├── COMPLETENESS_CHECK.md
│   │   ├── CORRECTIONS.md
│   │   ├── PROJECT_ANALYSIS.md
│   │   ├── PROJECT_STATUS.md
│   │   ├── PROJECT_SUMMARY.md
│   │   └── WORKFLOW_TEST_RESULTS.md
│   │
│   ├── DESIGN.md           # Notes de conception et architecture
│   └── README.md           # Index de la documentation
│
├── scripts/                # Scripts utilitaires
│   ├── cleanup_old_tests.py
│   ├── evaluation.py       # Script d'évaluation du pipeline
│   ├── test_workflow_simple.py # Script de test simple du workflow
│   └── README.md
│
├── deployment/             # Configurations de déploiement
│   ├── render.yaml         # Configuration Render.com
│   ├── railway.json        # Configuration Railway
│   ├── Procfile            # Configuration Heroku
│   ├── runtime.txt         # Version Python
│   └── README.md
│
├── data/                   # Données (générées à l'exécution, ignoré par git)
│   ├── chunks/             # Chunks de texte extraits
│   └── indices/            # Indices vectoriels FAISS
│
├── venv/                   # Environnement virtuel Python (ignoré par git)
│
├── .gitignore              # Fichiers ignorés par git
├── .env                    # Variables d'environnement (ignoré, créer depuis .env.example)
├── .env.example            # Template de configuration
├── README.md               # Documentation principale du projet
├── STRUCTURE.md            # Ce fichier - description de la structure
├── requirements.txt        # Dépendances Python
├── pytest.ini              # Configuration pytest
├── Dockerfile              # Image Docker pour containerisation
├── docker-compose.yml      # Configuration Docker Compose
└── run.py                  # Script de démarrage de l'application
```

## Description des dossiers

### `/app`
Code source principal de l'application FastAPI. Structure modulaire avec séparation claire des responsabilités :

- **auth/** : Système d'authentification JWT complet
  - `dependencies.py` : Dépendances FastAPI pour valider les tokens
  - `models.py` : Modèles Pydantic pour les utilisateurs et tokens
  - `service.py` : Logique d'authentification (hash de mots de passe, création/validation de tokens)

- **routers/** : Endpoints API REST
  - `auth.py` : Routes d'authentification (`/auth/register`, `/auth/login`, `/auth/me`)
  - `ingest.py` : Route d'ingestion (`POST /ingest`)
  - `status.py` : Route de statut (`GET /status/{job_id}`)
  - `ask.py` : Route de question (`POST /ask`)
  - `health.py` : Route de santé (`GET /health`)

- **services/** : Logique métier du pipeline RAG
  - `fetcher.py` : Web crawling avec contraintes (domain allowlist, max pages, depth)
  - `cleaner.py` : Nettoyage HTML et chunking avec métadonnées
  - `embedder.py` : Génération d'embeddings (OpenAI, Gemini, local)
  - `vector_store.py` : Stockage et recherche vectorielle FAISS
  - `generator.py` : Génération de réponses avec citations et anti-hallucination
  - `job_manager.py` : Orchestration des jobs d'ingestion en arrière-plan

- **static/** : Interface web utilisateur (HTML/CSS/JavaScript)
  - `index.html` : Interface complète avec authentification, ingestion, et questions

- **utils/** : Utilitaires partagés
  - `logger.py` : Configuration du logging structuré en JSON

- **Fichiers racine** :
  - `config.py` : Configuration via variables d'environnement (Pydantic Settings)
  - `main.py` : Application FastAPI principale
  - `models.py` : Modèles de données (enums, etc.)
  - `schemas.py` : Schémas Pydantic pour validation des requêtes/réponses

### `/tests`
Tests automatisés organisés par type :

- **unit/** : Tests unitaires pour les composants individuels
  - `test_cleaner.py` : Tests du service de nettoyage HTML

- **integration/** : Tests d'intégration pour le workflow complet
  - `test_auth.py` : Tests du système d'authentification
  - `test_ingest.py` : Tests du processus d'ingestion
  - `test_workflow.py` : Tests end-to-end du workflow RAG

- **Fichiers racine** :
  - `conftest.py` : Configuration pytest et fixtures partagées
  - `run_all_tests.py` : Script pour exécuter tous les tests
  - `README.md` : Documentation des tests

### `/docs`
Documentation organisée par catégorie :

- **guides/** : Guides d'utilisation et tutoriels
  - Guides d'authentification, endpoints, quickstart, etc.

- **deployment/** : Documentation de déploiement
  - Instructions pour déployer sur différentes plateformes

- **analysis/** : Analyses techniques et rapports
  - Analyses de complétude, corrections, statut du projet, etc.

- **Fichiers racine** :
  - `DESIGN.md` : Notes de conception et décisions architecturales
  - `README.md` : Index de la documentation

### `/scripts`
Scripts utilitaires pour :
- Nettoyage du projet
- Évaluation du pipeline RAG
- Tests simples du workflow
- Autres tâches d'automatisation

### `/deployment`
Fichiers de configuration pour différentes plateformes de déploiement :
- **Render.com** : `render.yaml`
- **Railway** : `railway.json`
- **Heroku** : `Procfile`, `runtime.txt`

### `/data`
Données générées à l'exécution (non versionnées) :
- **chunks/** : Chunks de texte extraits des pages web
- **indices/** : Indices vectoriels FAISS persistés

## Fichiers à la racine

### Configuration
- `requirements.txt` : Dépendances Python du projet
- `pytest.ini` : Configuration des tests pytest
- `.gitignore` : Fichiers et dossiers ignorés par git
- `.env.example` : Template de configuration (copier vers `.env`)
- `Dockerfile` : Image Docker pour containerisation
- `docker-compose.yml` : Configuration Docker Compose pour développement

### Documentation
- `README.md` : Documentation principale du projet (setup, usage, API)
- `DESIGN.md` : Notes de conception et décisions architecturales
- `STRUCTURE.md` : Ce fichier - description de la structure du projet

### Scripts
- `run.py` : Script de démarrage de l'application (uvicorn)

## Conventions

### Nommage
- **Fichiers Python** : `snake_case.py`
- **Dossiers** : `lowercase` ou `snake_case`
- **Classes** : `PascalCase`
- **Fonctions/variables** : `snake_case`
- **Constantes** : `UPPER_SNAKE_CASE`

### Organisation
- **Un fichier = une responsabilité principale**
- **Services** dans `/app/services/`
- **Routes** dans `/app/routers/`
- **Tests** miroir de la structure de `/app`
- **Documentation** organisée par catégorie dans `/docs`

### Imports
- Imports standards en premier
- Imports de bibliothèques tierces
- Imports locaux en dernier
- Utiliser des imports absolus depuis `app/`

## Fichiers ignorés par git

Les fichiers suivants sont ignorés (voir `.gitignore`) :
- `venv/` : Environnement virtuel Python
- `data/` : Données générées à l'exécution
- `__pycache__/` : Cache Python
- `.env` : Variables d'environnement (contient des secrets)
- `*.log` : Fichiers de log
- `*.faiss`, `*.index` : Fichiers d'indices vectoriels
- `.pytest_cache/` : Cache pytest
- `.coverage` : Rapports de couverture de code

## Maintenance

Pour maintenir cette structure :

1. **Placez les nouveaux fichiers dans le dossier approprié**
   - Code source → `/app`
   - Tests → `/tests`
   - Documentation → `/docs`
   - Scripts → `/scripts`

2. **Suivez les conventions de nommage**
   - Utilisez `snake_case` pour les fichiers Python
   - Utilisez des noms descriptifs

3. **Mettez à jour ce fichier si la structure change**
   - Ajoutez de nouveaux dossiers/fichiers
   - Documentez les changements

4. **Documentez les nouveaux dossiers**
   - Créez un `README.md` dans les nouveaux dossiers si nécessaire

5. **Gardez la racine propre**
   - Évitez d'ajouter trop de fichiers à la racine
   - Utilisez les dossiers appropriés

## Structure des imports

```python
# Exemple d'import depuis app/
from app.config import settings
from app.services.fetcher import WebFetcher
from app.routers.ingest import router
from app.auth.dependencies import get_current_active_user
```

## Workflow de développement

1. **Développement** : Code dans `/app`
2. **Tests** : Tests dans `/tests`
3. **Documentation** : Docs dans `/docs`
4. **Scripts** : Scripts utilitaires dans `/scripts`
5. **Déploiement** : Configs dans `/deployment`

## Points d'entrée

- **Application** : `python run.py` ou `uvicorn app.main:app --reload`
- **Tests** : `pytest` ou `python tests/run_all_tests.py`
- **Docker** : `docker-compose up`
- **Interface web** : `http://localhost:8000/`
- **API docs** : `http://localhost:8000/docs`
