# Tests NexTraction Web RAG

Ce dossier contient tous les tests pour le projet NexTraction Web RAG.

## Structure

```
tests/
├── unit/              # Tests unitaires
│   └── test_cleaner.py
├── integration/       # Tests d'intégration
│   ├── test_auth.py
│   ├── test_ingest.py
│   └── test_workflow.py
├── conftest.py        # Configuration pytest
└── README.md          # Ce fichier
```

## Types de tests

### Tests unitaires (`tests/unit/`)
- Testent des composants individuels en isolation
- Rapides à exécuter
- Ne nécessitent pas de serveur en cours d'exécution

### Tests d'intégration (`tests/integration/`)
- Testent le workflow complet de l'application
- Nécessitent que le serveur soit en cours d'exécution
- Testent les interactions entre différents composants

## Exécution des tests

### Prérequis

1. Installer les dépendances de test :
```bash
pip install pytest requests
```

2. Démarrer le serveur :
```bash
python run.py
```

### Tests unitaires

```bash
# Tous les tests unitaires
pytest tests/unit/

# Un test spécifique
pytest tests/unit/test_cleaner.py

# Avec verbosité
pytest tests/unit/ -v
```

### Tests d'intégration

```bash
# Tous les tests d'intégration
pytest tests/integration/

# Un test spécifique
pytest tests/integration/test_auth.py

# Tests d'authentification
python tests/integration/test_auth.py

# Tests de workflow complet
python tests/integration/test_workflow.py

# Tests d'ingestion
python tests/integration/test_ingest.py
```

### Tous les tests

```bash
pytest tests/
```

## Tests individuels (scripts Python)

Vous pouvez également exécuter les tests directement comme des scripts Python :

```bash
# Test d'authentification
python tests/integration/test_auth.py

# Test de workflow complet
python tests/integration/test_workflow.py

# Test d'ingestion
python tests/integration/test_ingest.py
```

## Configuration

Les tests utilisent par défaut `http://localhost:8000` comme URL de base. Vous pouvez la modifier en définissant la variable d'environnement :

```bash
export BASE_URL=http://localhost:8000
# ou sur Windows
set BASE_URL=http://localhost:8000
```

## Notes

- Les tests d'intégration créent des utilisateurs de test avec des noms uniques (basés sur le timestamp)
- Les tests peuvent prendre du temps car ils attendent que les jobs d'ingestion se terminent
- Certains tests peuvent échouer si les clés API (OpenAI, Gemini) ne sont pas configurées

## Dépannage

### Le serveur n'est pas démarré
```
Erreur: Le serveur n'est pas démarré!
```
Solution : Démarrer le serveur avec `python run.py`

### Erreur d'authentification
```
Erreur: 401 Unauthorized
```
Solution : Les tests créent automatiquement des utilisateurs de test. Si cela échoue, vérifiez que le serveur fonctionne correctement.

### Timeout lors de l'ingestion
```
[ATTENTION] Timeout après 90s
```
Solution : C'est normal si l'ingestion prend du temps. Le job continue en arrière-plan.

