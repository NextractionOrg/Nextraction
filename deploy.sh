#!/bin/bash

# Script de déploiement Docker pour NexTraction

echo "🐳 Construction de l'image Docker..."
docker build -t nextraction-api .

echo "🚀 Démarrage du conteneur..."
docker-compose up -d

echo "✅ Déploiement terminé!"
echo "📝 L'API est accessible sur http://localhost:8000"
echo "📚 Documentation Swagger: http://localhost:8000/docs"
echo ""
echo "Pour voir les logs: docker-compose logs -f"
echo "Pour arrêter: docker-compose down"

