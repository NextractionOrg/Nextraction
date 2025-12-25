# Script de deploiement local SANS Docker (Version simplifiee)
# Usage: .\deploy-simple.ps1

$ErrorActionPreference = "Stop"

Write-Host "Deploiement de NexTraction (Sans Docker)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier Python et determiner la commande
$pythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
    $pythonVersion = py --version 2>&1
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
    $pythonVersion = python --version 2>&1
} else {
    Write-Host "[ERREUR] Python n'est pas installe" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Python trouve: $pythonVersion" -ForegroundColor Green

# Verifier pip
try {
    & $pythonCmd -m pip --version | Out-Null
    Write-Host "[OK] pip est disponible" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] pip n'est pas disponible" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verifier/creer l'environnement virtuel
if (-not (Test-Path venv)) {
    Write-Host "[INFO] Creation de l'environnement virtuel..." -ForegroundColor Yellow
    & $pythonCmd -m venv venv
    Write-Host "[OK] Environnement virtuel cree" -ForegroundColor Green
}

# Activer l'environnement virtuel
Write-Host "[INFO] Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Mettre a jour pip
Write-Host "[INFO] Mise a jour de pip..." -ForegroundColor Yellow
& $pythonCmd -m pip install --upgrade pip --quiet

# Installer les dependances
Write-Host "[INFO] Installation des dependances..." -ForegroundColor Yellow
Write-Host "[INFO] Cela peut prendre plusieurs minutes..." -ForegroundColor Yellow
& $pythonCmd -m pip install -r requirements.txt

Write-Host "[OK] Dependances installees" -ForegroundColor Green
Write-Host ""

# Creer les dossiers necessaires
Write-Host "[INFO] Creation des dossiers de donnees..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data\chunks" | Out-Null
New-Item -ItemType Directory -Force -Path "data\indices" | Out-Null
Write-Host "[OK] Dossiers crees" -ForegroundColor Green
Write-Host ""

# Verifier/creer le fichier .env
if (-not (Test-Path .env)) {
    Write-Host "[ATTENTION] Le fichier .env n'existe pas" -ForegroundColor Yellow
    Write-Host "[INFO] Creation du fichier .env..."
    
    # Generer des cles securisees
    Write-Host "[INFO] Generation des cles securisees..." -ForegroundColor Yellow
    try {
        $jwtSecret = & $pythonCmd -c "import secrets; print(secrets.token_urlsafe(32))"
        $passwordSalt = & $pythonCmd -c "import secrets; print(secrets.token_urlsafe(16))"
    } catch {
        Write-Host "[ATTENTION] Impossible de generer les cles avec Python" -ForegroundColor Yellow
        $jwtSecret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        $passwordSalt = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    }
    
    # Creer le fichier .env
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
    
    Write-Host "[OK] Fichier .env cree" -ForegroundColor Green
    Write-Host ""
    Write-Host "[IMPORTANT] Editez le fichier .env et ajoutez votre OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ouvrez le fichier .env et remplacez 'your_openai_api_key_here' par votre vraie cle OpenAI" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Appuyez sur Entree apres avoir edite le fichier .env"
}

# Verifier que OPENAI_API_KEY est configure
$envContent = Get-Content .env -Raw
if ($envContent -match "your_openai_api_key_here") {
    Write-Host "[ATTENTION] OPENAI_API_KEY n'est pas configure dans .env" -ForegroundColor Yellow
    Write-Host "L'application ne fonctionnera pas sans cle OpenAI."
    $continue = Read-Host "Continuer quand meme? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

Write-Host ""
Write-Host "[INFO] Demarrage de l'application..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Votre application sera disponible sur:" -ForegroundColor Green
Write-Host "   - API: http://localhost:8000" -ForegroundColor White
Write-Host "   - Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - Health: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Pour arreter l'application, appuyez sur Ctrl+C" -ForegroundColor Yellow
Write-Host ""
Write-Host "Demarrage..." -ForegroundColor Green
Write-Host ""

# Lancer l'application
& $pythonCmd run.py

