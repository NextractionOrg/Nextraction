# Script de déploiement automatisé pour NexTraction (PowerShell)
# Usage: .\deploy.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Déploiement de NexTraction avec Docker" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que Docker est installé
try {
    docker --version | Out-Null
    Write-Host "✅ Docker est installé" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker n'est pas installé" -ForegroundColor Red
    Write-Host "Installez Docker : https://docs.docker.com/get-docker/"
    exit 1
}

# Vérifier que Docker Compose est disponible
try {
    docker compose version | Out-Null
    Write-Host "✅ Docker Compose est disponible" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose n'est pas disponible" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Vérifier si le fichier .env existe
if (-not (Test-Path .env)) {
    Write-Host "⚠️  Le fichier .env n'existe pas" -ForegroundColor Yellow
    Write-Host "Création du fichier .env..."
    
    # Générer des clés sécurisées
    Write-Host "Génération des clés sécurisées..."
    
    try {
        $jwtSecret = python -c "import secrets; print(secrets.token_urlsafe(32))"
        $passwordSalt = python -c "import secrets; print(secrets.token_urlsafe(16))"
    } catch {
        Write-Host "⚠️  Impossible de générer les clés avec Python" -ForegroundColor Yellow
        Write-Host "Génération de clés alternatives..."
        $jwtSecret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        $passwordSalt = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    }
    
    # Créer le fichier .env
    $envContent = @"
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=

# Embedding Provider (local = free, no API key needed)
EMBEDDING_PROVIDER=local

# LLM Provider
LLM_PROVIDER=openai

# Authentication (Generated automatically)
JWT_SECRET_KEY=$jwtSecret
PASSWORD_SALT=$passwordSalt

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Vector Store
FAISS_INDEX_PATH=./data/faiss_index

# Data Directories
DATA_DIR=./data
CHUNKS_DIR=./data/chunks
"@
    
    $envContent | Out-File -FilePath .env -Encoding utf8
    
    Write-Host "✅ Fichier .env créé" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANT: Éditez le fichier .env et ajoutez votre OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Appuyez sur Entrée après avoir édité le fichier .env"
}

# Vérifier que OPENAI_API_KEY est configuré
$envContent = Get-Content .env -Raw
if ($envContent -match "your_openai_api_key_here" -or -not ($envContent -match "OPENAI_API_KEY=")) {
    Write-Host "⚠️  OPENAI_API_KEY n'est pas configuré dans .env" -ForegroundColor Yellow
    Write-Host "Le déploiement continuera, mais l'application ne fonctionnera pas sans clé OpenAI."
    $continue = Read-Host "Continuer quand même? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

Write-Host ""
Write-Host "📦 Construction de l'image Docker..." -ForegroundColor Cyan
docker compose build

Write-Host ""
Write-Host "🚀 Démarrage des conteneurs..." -ForegroundColor Cyan
docker compose up -d

Write-Host ""
Write-Host "⏳ Attente du démarrage de l'application (10 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "🔍 Vérification du health check..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Application démarrée avec succès!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📍 Votre application est disponible sur:" -ForegroundColor Cyan
        Write-Host "   - API: http://localhost:8000"
        Write-Host "   - Docs: http://localhost:8000/docs"
        Write-Host "   - Health: http://localhost:8000/health"
        Write-Host ""
        Write-Host "📊 Commandes utiles:" -ForegroundColor Cyan
        Write-Host "   - Voir les logs: docker compose logs -f"
        Write-Host "   - Arrêter: docker compose down"
        Write-Host "   - Redémarrer: docker compose restart"
        Write-Host "   - Statut: docker compose ps"
    }
} catch {
    Write-Host "⚠️  Le health check a échoué" -ForegroundColor Yellow
    Write-Host "Vérifiez les logs avec: docker compose logs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✨ Déploiement terminé!" -ForegroundColor Green

