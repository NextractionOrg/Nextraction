#!/bin/bash

# Script de déploiement automatisé pour NexTraction
# Usage: ./deploy.sh

set -e  # Arrêter en cas d'erreur

echo "🚀 Déploiement de NexTraction avec Docker"
echo "=========================================="
echo ""

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    echo "Installez Docker : https://docs.docker.com/get-docker/"
    exit 1
fi

# Vérifier que Docker Compose est disponible
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas disponible${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker est installé${NC}"
echo ""

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Le fichier .env n'existe pas${NC}"
    echo "Création du fichier .env..."
    
    # Générer des clés sécurisées
    echo "Génération des clés sécurisées..."
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || python -c "import secrets; print(secrets.token_urlsafe(32))")
    PASSWORD_SALT=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))" 2>/dev/null || python -c "import secrets; print(secrets.token_urlsafe(16))")
    
    # Créer le fichier .env
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=

# Embedding Provider (local = free, no API key needed)
EMBEDDING_PROVIDER=local

# LLM Provider
LLM_PROVIDER=openai

# Authentication (Generated automatically)
JWT_SECRET_KEY=${JWT_SECRET}
PASSWORD_SALT=${PASSWORD_SALT}

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Vector Store
FAISS_INDEX_PATH=./data/faiss_index

# Data Directories
DATA_DIR=./data
CHUNKS_DIR=./data/chunks
EOF
    
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Éditez le fichier .env et ajoutez votre OPENAI_API_KEY${NC}"
    echo ""
    read -p "Appuyez sur Entrée après avoir édité le fichier .env... "
fi

# Vérifier que OPENAI_API_KEY est configuré
if grep -q "your_openai_api_key_here" .env 2>/dev/null || ! grep -q "OPENAI_API_KEY=" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY n'est pas configuré dans .env${NC}"
    echo "Le déploiement continuera, mais l'application ne fonctionnera pas sans clé OpenAI."
    read -p "Continuer quand même? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📦 Construction de l'image Docker..."
docker compose build

echo ""
echo "🚀 Démarrage des conteneurs..."
docker compose up -d

echo ""
echo "⏳ Attente du démarrage de l'application (10 secondes)..."
sleep 10

echo ""
echo "🔍 Vérification du health check..."
if curl -f http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✅ Application démarrée avec succès!${NC}"
    echo ""
    echo "📍 Votre application est disponible sur:"
    echo "   - API: http://localhost:8000"
    echo "   - Docs: http://localhost:8000/docs"
    echo "   - Health: http://localhost:8000/health"
    echo ""
    echo "📊 Commandes utiles:"
    echo "   - Voir les logs: docker compose logs -f"
    echo "   - Arrêter: docker compose down"
    echo "   - Redémarrer: docker compose restart"
    echo "   - Statut: docker compose ps"
else
    echo -e "${YELLOW}⚠️  Le health check a échoué${NC}"
    echo "Vérifiez les logs avec: docker compose logs"
fi

echo ""
echo -e "${GREEN}✨ Déploiement terminé!${NC}"

