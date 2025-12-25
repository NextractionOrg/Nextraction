# Explication des Endpoints : `/` vs `/docs`

## Vue d'ensemble

Votre application FastAPI expose deux interfaces différentes :

1. **`http://localhost:8000/`** → Interface web personnalisée (UI)
2. **`http://localhost:8000/docs`** → Documentation interactive Swagger UI (générée automatiquement)

---

## 1. `http://localhost:8000/` - Endpoint Racine

### Ce que c'est
L'endpoint racine (`/`) sert votre **interface web personnalisée** (`app/static/index.html`).

### Comportement
D'après le code dans `app/main.py` :

```python
@app.get("/")
async def root():
    """Root endpoint - redirects to UI or shows API info"""
    ui_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(ui_path):
        from fastapi.responses import FileResponse
        return FileResponse(ui_path)  # ← Retourne l'interface HTML
    return {
        "message": "NexTraction Web RAG API",
        "version": settings.api_version,
        "docs": "/docs"
    }
```

### Ce que vous voyez
- ✅ **Interface web complète** avec :
  - Formulaire de connexion/inscription
  - Formulaire d'ingestion
  - Vérification du statut des jobs
  - Formulaire pour poser des questions
  - Affichage des résultats avec citations
  - Design moderne avec gradient violet

### Utilisation
- **Pour les utilisateurs finaux** : Interface graphique intuitive
- **Pour tester l'application** : Utilisation via le navigateur sans code

---

## 2. `http://localhost:8000/docs` - Documentation Swagger UI

### Ce que c'est
L'endpoint `/docs` est **généré automatiquement par FastAPI**. C'est la documentation interactive de votre API REST.

### Comportement
FastAPI génère automatiquement cette interface à partir de :
- Vos routes définies dans `app/routers/`
- Les schémas Pydantic dans `app/schemas.py`
- Les docstrings de vos fonctions

### Ce que vous voyez
- ✅ **Documentation complète** de tous les endpoints :
  - `/auth/register` - Inscription
  - `/auth/login` - Connexion
  - `/auth/me` - Informations utilisateur
  - `/ingest` - Démarrer une ingestion
  - `/status/{job_id}` - Statut d'un job
  - `/ask` - Poser une question
  - `/health` - Santé de l'API

- ✅ **Test interactif** : Vous pouvez :
  - Voir tous les endpoints disponibles
  - Lire la documentation de chaque endpoint
  - **Tester directement** les endpoints depuis le navigateur
  - Voir les schémas de requête/réponse
  - Tester avec authentification JWT

### Utilisation
- **Pour les développeurs** : Documentation et test de l'API
- **Pour l'intégration** : Comprendre les endpoints et leurs formats
- **Pour le débogage** : Tester rapidement les endpoints

---

## Comparaison visuelle

### `http://localhost:8000/`
```
┌─────────────────────────────────────┐
│  NexTraction Web RAG                │
│  ┌───────────────────────────────┐ │
│  │  [Se connecter] [Déconnexion] │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌─────────────┐  ┌─────────────┐ │
│  │  Ingestion  │  │  Statut     │ │
│  │             │  │             │ │
│  │  [Formulaire]│  │  [Formulaire]│ │
│  └─────────────┘  └─────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Poser une question            │ │
│  │  [Formulaire + Résultats]     │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```
**Interface utilisateur graphique complète**

### `http://localhost:8000/docs`
```
┌─────────────────────────────────────┐
│  NexTraction Web RAG API            │
│  ┌───────────────────────────────┐ │
│  │  POST /auth/register          │ │
│  │  POST /auth/login              │ │
│  │  GET  /auth/me                 │ │
│  │  POST /ingest                  │ │
│  │  GET  /status/{job_id}         │ │
│  │  POST /ask                     │ │
│  │  GET  /health                  │ │
│  └───────────────────────────────┘ │
│                                     │
│  [Try it out] [Request Body]        │
│  [Execute] → [Response]             │
└─────────────────────────────────────┘
```
**Documentation interactive de l'API**

---

## Quand utiliser quoi ?

### Utilisez `/` (Interface web) quand :
- ✅ Vous voulez une interface utilisateur complète
- ✅ Vous testez l'application comme un utilisateur final
- ✅ Vous voulez voir les résultats avec un design soigné
- ✅ Vous préférez une interface graphique

### Utilisez `/docs` (Swagger UI) quand :
- ✅ Vous développez et voulez tester l'API rapidement
- ✅ Vous voulez comprendre la structure de l'API
- ✅ Vous intégrez l'API dans une autre application
- ✅ Vous voulez voir les schémas de données exacts
- ✅ Vous déboguez un endpoint spécifique

---

## Autres endpoints utiles

### `/docs` (Swagger UI)
- Documentation interactive
- **URL** : `http://localhost:8000/docs`

### `/redoc` (ReDoc)
- Documentation alternative (format différent)
- **URL** : `http://localhost:8000/redoc`

### `/openapi.json`
- Schéma OpenAPI au format JSON
- **URL** : `http://localhost:8000/openapi.json`
- Utile pour générer des clients API

---

## Exemple pratique

### Scénario 1 : Utilisateur final
```
1. Ouvrir http://localhost:8000/
2. Se connecter avec l'interface graphique
3. Démarrer une ingestion via le formulaire
4. Voir les résultats avec citations
```

### Scénario 2 : Développeur
```
1. Ouvrir http://localhost:8000/docs
2. Cliquer sur "POST /auth/login"
3. Cliquer sur "Try it out"
4. Entrer username/password
5. Cliquer sur "Execute"
6. Copier le token JWT
7. Utiliser le token pour tester /ingest
```

---

## Résumé

| Caractéristique | `/` (Racine) | `/docs` (Swagger) |
|----------------|-------------|-------------------|
| **Type** | Interface web personnalisée | Documentation API automatique |
| **Contenu** | HTML/CSS/JS complet | Documentation interactive |
| **Utilisation** | Utilisateurs finaux | Développeurs |
| **Test** | Via formulaires graphiques | Via interface Swagger |
| **Personnalisation** | Complète (votre code) | Automatique (FastAPI) |
| **Authentification** | Gérée dans l'UI | Via bouton "Authorize" |

---

## Conclusion

Les deux endpoints sont complémentaires :
- **`/`** = Interface utilisateur pour les utilisateurs finaux
- **`/docs`** = Documentation et test pour les développeurs

Vous pouvez utiliser les deux selon vos besoins ! 🚀

