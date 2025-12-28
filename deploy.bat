@echo off
REM Script de déploiement Docker pour NexTraction (Windows)

echo 🐳 Construction de l'image Docker...
docker build -t nextraction-api .

if %errorlevel% neq 0 (
    echo ❌ Erreur lors de la construction de l'image
    exit /b 1
)

echo 🚀 Démarrage du conteneur...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Erreur lors du démarrage du conteneur
    exit /b 1
)

echo ✅ Déploiement terminé!
echo 📝 L'API est accessible sur http://localhost:8000
echo 📚 Documentation Swagger: http://localhost:8000/docs
echo.
echo Pour voir les logs: docker-compose logs -f
echo Pour arrêter: docker-compose down

