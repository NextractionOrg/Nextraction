# Test Rapide du Workflow

## Méthode 1 : Via l'Interface Web (Recommandé)

1. **Démarrer le serveur** :
   ```bash
   python run.py
   ```

2. **Ouvrir dans le navigateur** :
   ```
   http://localhost:8000/
   ```

3. **Tester** :
   - Cliquez sur "S'inscrire"
   - Créez un compte
   - Connectez-vous
   - Remplissez le formulaire d'ingestion :
     - URLs: `https://example.com`
     - Domaines: `example.com`
     - Max pages: `3`
     - Profondeur: `0`
   - Cliquez sur "Démarrer l'ingestion"
   - Vérifiez le statut
   - Posez une question

## Méthode 2 : Via le Script Python

```bash
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Exécuter le test
python test_workflow_simple.py
```

## Note Importante

Si vous obtenez une erreur 500 lors de l'ingestion, c'est probablement parce que :
- Aucune clé API OpenAI n'est configurée
- `sentence-transformers` n'est pas installé

**Solution rapide** :
```bash
pip install sentence-transformers
```

Cela permettra d'utiliser des embeddings locaux sans clé API.

