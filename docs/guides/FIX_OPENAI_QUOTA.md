# 🔧 Résoudre l'Erreur "Insufficient Quota" OpenAI

## Problème

Vous recevez une erreur **429 "insufficient_quota"** lors de l'ingestion. Cela signifie que votre clé API OpenAI a dépassé son quota ou n'a pas de crédits disponibles.

## Solutions

### Solution 1 : Utiliser les Embeddings Locaux (Recommandé)

Les embeddings locaux ne nécessitent pas de clé API et fonctionnent gratuitement.

#### Étape 1 : Installer sentence-transformers

```bash
pip install sentence-transformers
```

#### Étape 2 : Configurer .env

Éditez votre fichier `.env` et changez :

```env
EMBEDDING_PROVIDER=local
```

Au lieu de :
```env
EMBEDDING_PROVIDER=openai
```

#### Étape 3 : Redémarrer le serveur

```bash
python run.py
```

**Avantages :**
- ✅ Gratuit
- ✅ Pas de limite de quota
- ✅ Fonctionne hors ligne
- ✅ Pas besoin de clé API

**Inconvénients :**
- ⚠️ Légèrement moins performant que OpenAI
- ⚠️ Dimensions différentes (384 au lieu de 1536)

### Solution 2 : Vérifier et Recharger votre Clé OpenAI

1. **Vérifier votre compte OpenAI**
   - Allez sur https://platform.openai.com/account/billing
   - Vérifiez que vous avez des crédits disponibles
   - Vérifiez votre plan et limites

2. **Ajouter des crédits**
   - Si nécessaire, ajoutez des crédits à votre compte
   - Attendez quelques minutes pour que les changements prennent effet

3. **Vérifier votre clé API**
   - Vérifiez que votre clé API est valide
   - Régénérez une nouvelle clé si nécessaire

### Solution 3 : Utiliser Gemini (Alternative)

Si vous avez une clé Gemini :

1. **Installer la bibliothèque**
   ```bash
   pip install google-generativeai
   ```

2. **Configurer .env**
   ```env
   EMBEDDING_PROVIDER=gemini
   GEMINI_API_KEY=votre_cle_gemini_ici
   ```

## Fallback Automatique

Le système essaie maintenant automatiquement de basculer vers les embeddings locaux si OpenAI échoue avec une erreur de quota. Cependant, vous devez avoir `sentence-transformers` installé.

## Vérification

Pour vérifier que les embeddings locaux fonctionnent :

```bash
python -c "from sentence_transformers import SentenceTransformer; print('OK')"
```

Si vous voyez "OK", les embeddings locaux sont prêts.

## Recommandation

Pour le développement et les tests, **utilisez les embeddings locaux** (`EMBEDDING_PROVIDER=local`). C'est gratuit, rapide à configurer, et suffisant pour la plupart des cas d'usage.

Utilisez OpenAI uniquement si vous avez besoin de :
- Meilleure qualité d'embeddings
- Dimensions spécifiques (1536)
- Production avec beaucoup de données

## Support

Si vous continuez à avoir des problèmes :
1. Vérifiez les logs du serveur pour plus de détails
2. Vérifiez que `sentence-transformers` est installé
3. Vérifiez votre fichier `.env`

