# Script de déploiement local SANS Docker
# Usage: .\deploy-local.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Déploiement de NexTraction (Sans Docker)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python n'est pas installé" -ForegroundColor Red
    exit 1
}

# Vérifier pip
try {
    pip --version | Out-Null
    Write-Host "✅ pip est disponible" -ForegroundColor Green
} catch {
    Write-Host "❌ pip n'est pas disponible" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Vérifier/créer l'environnement virtuel
if (-not (Test-Path venv)) {
    Write-Host "📦 Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Environnement virtuel créé" -ForegroundColor Green
}

# Activer l'environnement virtuel
Write-Host "🔧 Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Mettre à jour pip
Write-Host "📦 Mise à jour de pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Installer les dépendances
Write-Host "📦 Installation des dépendances..." -ForegroundColor Yellow
Write-Host "⏳ Cela peut prendre plusieurs minutes..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "✅ Dépendances installées" -ForegroundColor Green
Write-Host ""

# Créer les dossiers nécessaires
Write-Host "📁 Création des dossiers de données..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data\chunks" | Out-Null
New-Item -ItemType Directory -Force -Path "data\indices" | Out-Null
Write-Host "✅ Dossiers créés" -ForegroundColor Green
Write-Host ""

# Vérifier/créer le fichier .env
if (-not (Test-Path .env)) {
    Write-Host "⚠️  Le fichier .env n'existe pas" -ForegroundColor Yellow
    Write-Host "Création du fichier .env..."
    
    # Générer des clés sécurisées
    Write-Host "🔐 Génération des clés sécurisées..." -ForegroundColor Yellow
    try {
        $jwtSecret = python -c "import secrets; print(secrets.token_urlsafe(32))"
        $passwordSalt = python -c "import secrets; print(secrets.token_urlsafe(16))"
    } catch {
        Write-Host "⚠️  Impossible de générer les clés avec Python" -ForegroundColor Yellow
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
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Éditez le fichier .env et ajoutez votre OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ouvrez le fichier .env et remplacez 'your_openai_api_key_here' par votre vraie clé OpenAI" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Appuyez sur Entrée après avoir édité le fichier .env"
}

# Vérifier que OPENAI_API_KEY est configuré
$envContent = Get-Content .env -Raw
if ($envContent -match "your_openai_api_key_here") {
    Write-Host "⚠️  OPENAI_API_KEY n'est pas configuré dans .env" -ForegroundColor Yellow
    Write-Host "L'application ne fonctionnera pas sans clé OpenAI."
    $continue = Read-Host "Continuer quand même? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 Démarrage de l'application..." -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Votre application sera disponible sur:" -ForegroundColor Green
Write-Host "   - API: http://localhost:8000" -ForegroundColor White
Write-Host "   - Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - Health: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "💡 Pour arrêter l'application, appuyez sur Ctrl+C" -ForegroundColor Yellow
Write-Host ""
Write-Host "Demarrage..." -ForegroundColor Green
Write-Host ""

# Lancer l'application
python run.py

