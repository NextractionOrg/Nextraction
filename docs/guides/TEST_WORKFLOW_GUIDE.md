# Guide de Test du Workflow NexTraction

## ✅ Résultats du Test

Le test du workflow a été exécuté avec les résultats suivants :

### ✅ Étapes réussies :
1. **Inscription** - ✅ Réussie
   - Utilisateur créé avec succès
   - ID généré correctement

2. **Connexion** - ✅ Réussie
   - Token JWT obtenu
   - Authentification fonctionnelle

3. **Ingestion** - ⚠️ Erreur 500
   - Job créé mais erreur lors du traitement
   - Cause probable : Embedding provider non configuré

### ⚠️ Problèmes identifiés :

1. **Embedding Provider**
   - Si aucune clé API n'est configurée, le système essaie d'utiliser des embeddings locaux
   - Nécessite `sentence-transformers` installé
   - Solution : Installer `sentence-transformers` ou configurer une clé API

2. **Erreur 500 lors de l'ingestion**
   - Peut être causée par :
     - Embedding provider non disponible
     - Erreur lors du traitement en arrière-plan
     - Problème de configuration

## 🔧 Solutions

### Option 1 : Installer sentence-transformers (embeddings locaux)
```bash
pip install sentence-transformers
```

### Option 2 : Configurer une clé OpenAI
```bash
# Dans .env
OPENAI_API_KEY=votre_cle_ici
```

### Option 3 : Vérifier les logs du serveur
Les erreurs détaillées sont dans les logs du serveur. Vérifiez la console où le serveur tourne.

## 📝 Test Manuel via l'Interface Web

1. **Démarrer le serveur** :
   ```bash
   python run.py
   ```

2. **Ouvrir l'interface** :
   - Aller sur `http://localhost:8000/`

3. **Tester le workflow** :
   - S'inscrire avec un nouveau compte
   - Se connecter
   - Démarrer une ingestion
   - Vérifier le statut
   - Poser une question

## 🐛 Débogage

Si vous rencontrez des erreurs :

1. **Vérifier les logs du serveur** :
   - Les erreurs détaillées apparaissent dans la console du serveur

2. **Vérifier la configuration** :
   - `.env` existe et contient les bonnes valeurs
   - Clés API configurées si nécessaire

3. **Vérifier les dépendances** :
   ```bash
   pip install -r requirements.txt
   pip install sentence-transformers  # Pour embeddings locaux
   ```

## ✅ Workflow Testé

Le workflow de base fonctionne :
- ✅ Authentification (inscription + connexion)
- ✅ Création de job
- ⚠️ Traitement du job (nécessite configuration embedding)

Une fois l'embedding provider configuré, le workflow complet devrait fonctionner.

