# Configurations de Déploiement

Ce dossier contient les fichiers de configuration pour déployer NexTraction sur différentes plateformes.

## Fichiers disponibles

### `render.yaml`
Configuration pour déploiement sur Render.com

### `railway.json`
Configuration pour déploiement sur Railway

### `Procfile`
Configuration pour déploiement sur Heroku

### `runtime.txt`
Spécification de la version Python pour les plateformes de déploiement

## Utilisation

### Render
1. Connectez votre repository GitHub à Render
2. Render détectera automatiquement `deployment/render.yaml`

### Railway
1. Connectez votre repository GitHub à Railway
2. Railway utilisera `deployment/railway.json`

### Heroku
1. Déployez avec Heroku CLI :
```bash
heroku create votre-app
git push heroku main
```

## Note

Le `Dockerfile` et `docker-compose.yml` restent à la racine car ils sont utilisés pour le développement local et peuvent être référencés par les plateformes de déploiement.

