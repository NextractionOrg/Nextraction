# 📥 Guide d'Exemples pour Tester l'Ingestion

## Vue d'ensemble

Ce guide fournit des exemples concrets pour tester l'endpoint `/ingest` du pipeline NexTraction.

---

## 🎯 Exemples Rapides

### Exemple 1 : Site Simple (Recommandé pour débuter)

**URLs de test :**
```
https://example.com
```

**Configuration :**
- Domaines autorisés : `example.com`
- Max pages : `3`
- Profondeur : `0` (seulement la page de départ)

**Résultat attendu :** Ingestion rapide d'une seule page

---

### Exemple 2 : Documentation Python

**URLs de test :**
```
https://docs.python.org/3/tutorial/introduction.html
```

**Configuration :**
- Domaines autorisés : `docs.python.org`
- Max pages : `5`
- Profondeur : `1` (page de départ + liens directs)

**Résultat attendu :** Ingestion de plusieurs pages de documentation

---

### Exemple 3 : Blog/Article

**URLs de test :**
```
https://www.python.org/about/gettingstarted/
```

**Configuration :**
- Domaines autorisés : `python.org`, `www.python.org`
- Max pages : `10`
- Profondeur : `1`

**Résultat attendu :** Ingestion d'un article et de pages liées

---

## 🌐 Méthode 1 : Via l'Interface Web

### Étape par Étape

1. **Démarrer le serveur**
   ```bash
   python run.py
   ```

2. **Ouvrir l'interface**
   - Aller sur : http://localhost:8000/
   - S'inscrire ou se connecter

3. **Remplir le formulaire d'ingestion**

   **Exemple Simple :**
   ```
   URLs (une par ligne) :
   https://example.com
   
   Domaines autorisés (séparés par virgule) :
   example.com
   
   Max pages : 3
   Profondeur : 0
   ```

   **Exemple Avancé :**
   ```
   URLs (une par ligne) :
   https://docs.python.org/3/tutorial/introduction.html
   https://docs.python.org/3/tutorial/interpreter.html
   
   Domaines autorisés :
   docs.python.org
   
   Max pages : 10
   Profondeur : 1
   ```

4. **Cliquer sur "Démarrer l'ingestion"**

5. **Vérifier le statut**
   - Le Job ID s'affiche
   - Cliquer sur "Vérifier le statut" pour suivre la progression
   - Attendre que l'état passe à "done"

---

## 💻 Méthode 2 : Via l'API (curl/PowerShell)

### Exemple 1 : Ingestion Simple

#### PowerShell

```powershell
# 1. Se connecter d'abord pour obtenir un token
$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method POST `
    -Body (@{
        username = "testuser"
        password = "testpass123"
    } | ConvertTo-Json) `
    -ContentType "application/json"

# Si erreur, utiliser form-data
$loginForm = "username=testuser&password=testpass123"
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method POST `
    -Body $loginForm `
    -ContentType "application/x-www-form-urlencoded"

$token = $loginResponse.access_token
Write-Host "Token obtenu: $token"

# 2. Lancer l'ingestion
$ingestBody = @{
    seed_urls = @("https://example.com")
    domain_allowlist = @("example.com")
    max_pages = 3
    max_depth = 0
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$ingestResponse = Invoke-RestMethod -Uri "http://localhost:8000/ingest" `
    -Method POST `
    -Body $ingestBody `
    -Headers $headers

Write-Host "Job ID: $($ingestResponse.job_id)"
Write-Host "Pages acceptées: $($ingestResponse.accepted_pages)"
```

#### curl (Bash/Linux)

```bash
# 1. Se connecter
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123" \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Lancer l'ingestion
curl -X POST "http://localhost:8000/ingest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_urls": ["https://example.com"],
    "domain_allowlist": ["example.com"],
    "max_pages": 3,
    "max_depth": 0
  }'
```

### Exemple 2 : Ingestion Multi-URLs

#### PowerShell

```powershell
$ingestBody = @{
    seed_urls = @(
        "https://docs.python.org/3/tutorial/introduction.html",
        "https://docs.python.org/3/tutorial/interpreter.html"
    )
    domain_allowlist = @("docs.python.org")
    max_pages = 10
    max_depth = 1
    user_notes = "Test documentation Python"
} | ConvertTo-Json

$ingestResponse = Invoke-RestMethod -Uri "http://localhost:8000/ingest" `
    -Method POST `
    -Body $ingestBody `
    -Headers $headers

Write-Host "Job ID: $($ingestResponse.job_id)"
```

### Exemple 3 : Vérifier le Statut

#### PowerShell

```powershell
$jobId = "votre_job_id_ici"

$statusResponse = Invoke-RestMethod -Uri "http://localhost:8000/status/$jobId" `
    -Method GET `
    -Headers $headers

Write-Host "État: $($statusResponse.state)"
Write-Host "Pages récupérées: $($statusResponse.pages_fetched)"
Write-Host "Pages indexées: $($statusResponse.pages_indexed)"
```

---

## 🐍 Méthode 3 : Via Script Python

### Script Simple

Créez un fichier `test_ingestion.py` :

```python
import requests
import time
import json

BASE_URL = "http://localhost:8000"

# 1. Connexion
print("1. Connexion...")
login_data = {
    "username": "testuser",
    "password": "testpass123"
}
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data=login_data
)
token = login_response.json()["access_token"]
print(f"✅ Token obtenu: {token[:20]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. Ingestion
print("\n2. Lancement de l'ingestion...")
ingest_data = {
    "seed_urls": ["https://example.com"],
    "domain_allowlist": ["example.com"],
    "max_pages": 3,
    "max_depth": 0,
    "user_notes": "Test d'ingestion simple"
}

ingest_response = requests.post(
    f"{BASE_URL}/ingest",
    json=ingest_data,
    headers=headers
)

job_id = ingest_response.json()["job_id"]
print(f"✅ Job créé: {job_id}")

# 3. Vérifier le statut
print("\n3. Vérification du statut...")
while True:
    status_response = requests.get(
        f"{BASE_URL}/status/{job_id}",
        headers=headers
    )
    status = status_response.json()
    
    print(f"État: {status['state']} | "
          f"Pages: {status.get('pages_fetched', 0)}/{status.get('pages_indexed', 0)}")
    
    if status["state"] in ["done", "failed"]:
        break
    
    time.sleep(2)

print(f"\n✅ Ingestion terminée: {status['state']}")
```

Exécuter :
```bash
python test_ingestion.py
```

---

## 📋 Exemples de Données de Test

### Exemple 1 : Site Éducatif

```json
{
  "seed_urls": [
    "https://www.python.org/about/gettingstarted/"
  ],
  "domain_allowlist": ["python.org", "www.python.org"],
  "max_pages": 5,
  "max_depth": 1,
  "user_notes": "Documentation Python pour débutants"
}
```

### Exemple 2 : Documentation Technique

```json
{
  "seed_urls": [
    "https://docs.python.org/3/tutorial/introduction.html",
    "https://docs.python.org/3/tutorial/interpreter.html"
  ],
  "domain_allowlist": ["docs.python.org"],
  "max_pages": 10,
  "max_depth": 1,
  "user_notes": "Tutoriel Python officiel"
}
```

### Exemple 3 : Blog/Article

```json
{
  "seed_urls": [
    "https://realpython.com/python-web-scraping-practical-introduction/"
  ],
  "domain_allowlist": ["realpython.com"],
  "max_pages": 3,
  "max_depth": 0,
  "user_notes": "Article sur le web scraping"
}
```

### Exemple 4 : Site d'Actualités

```json
{
  "seed_urls": [
    "https://news.ycombinator.com"
  ],
  "domain_allowlist": ["news.ycombinator.com"],
  "max_pages": 5,
  "max_depth": 0,
  "user_notes": "Page d'accueil Hacker News"
}
```

---

## 🔍 Vérification du Résultat

### 1. Vérifier le Statut

```powershell
# Via PowerShell
$status = Invoke-RestMethod -Uri "http://localhost:8000/status/$jobId" `
    -Headers $headers
$status | ConvertTo-Json
```

### 2. Poser une Question

Une fois l'ingestion terminée, testez avec `/ask` :

```powershell
$askBody = @{
    job_id = $jobId
    question = "Qu'est-ce que Python ?"
} | ConvertTo-Json

$answer = Invoke-RestMethod -Uri "http://localhost:8000/ask" `
    -Method POST `
    -Body $askBody `
    -Headers $headers

$answer | ConvertTo-Json -Depth 10
```

### 3. Vérifier les Fichiers

Les données sont stockées dans :
- `data/chunks/` : Chunks de texte extraits
- `data/indices/` : Indices vectoriels FAISS

```powershell
# Lister les chunks créés
Get-ChildItem data/chunks/ | Select-Object Name, Length
```

---

## ⚠️ Erreurs Courantes et Solutions

### Erreur : "Domain not in allowlist"

**Problème :** L'URL ne correspond pas au domaine autorisé

**Solution :**
```json
{
  "seed_urls": ["https://www.example.com"],
  "domain_allowlist": ["example.com", "www.example.com"]  // Inclure les variantes
}
```

### Erreur : "Max pages reached"

**Problème :** Trop de pages à crawler

**Solution :** Réduire `max_pages` ou `max_depth`

### Erreur : "Timeout"

**Problème :** Le site est trop lent

**Solution :** 
- Réduire `max_pages`
- Utiliser `max_depth: 0` pour une seule page
- Choisir un site plus rapide

### Erreur : "No content extracted"

**Problème :** La page ne contient pas assez de texte

**Solution :** Choisir une page avec plus de contenu textuel

---

## 🎯 Sites Recommandés pour Tester

### Sites Simples (Bon pour débuter)

1. **example.com** - Site de test standard
   - URL : `https://example.com`
   - Domaine : `example.com`
   - Contenu : Simple, une page

2. **httpbin.org** - Service de test HTTP
   - URL : `https://httpbin.org/html`
   - Domaine : `httpbin.org`
   - Contenu : HTML simple

### Sites avec Contenu Riche

1. **Python.org** - Documentation Python
   - URL : `https://www.python.org/about/gettingstarted/`
   - Domaine : `python.org`, `www.python.org`
   - Contenu : Articles et documentation

2. **Real Python** - Tutoriels Python
   - URL : `https://realpython.com/python-web-scraping-practical-introduction/`
   - Domaine : `realpython.com`
   - Contenu : Articles détaillés

### Sites à Éviter (pour les tests)

- ❌ Sites avec paywall
- ❌ Sites nécessitant une authentification
- ❌ Sites avec beaucoup de JavaScript (peuvent être lents)
- ❌ Sites avec protection anti-bot agressive

---

## 📊 Exemple Complet : Workflow End-to-End

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Connexion
print("🔐 Connexion...")
login = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "testuser", "password": "testpass123"}
)
token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Ingestion
print("📥 Ingestion...")
ingest = requests.post(
    f"{BASE_URL}/ingest",
    json={
        "seed_urls": ["https://example.com"],
        "domain_allowlist": ["example.com"],
        "max_pages": 3,
        "max_depth": 0
    },
    headers=headers
)
job_id = ingest.json()["job_id"]
print(f"✅ Job ID: {job_id}")

# 3. Attendre la fin
print("⏳ Attente de la fin...")
while True:
    status = requests.get(f"{BASE_URL}/status/{job_id}", headers=headers).json()
    print(f"   État: {status['state']}")
    if status["state"] in ["done", "failed"]:
        break
    time.sleep(2)

# 4. Poser une question
print("❓ Question...")
answer = requests.post(
    f"{BASE_URL}/ask",
    json={
        "job_id": job_id,
        "question": "Quel est le contenu de cette page ?"
    },
    headers=headers
).json()

print(f"✅ Réponse: {answer['answer']}")
print(f"📚 Citations: {len(answer['citations'])}")
```

---

## ✅ Checklist de Test

- [ ] Ingestion simple (1 URL, 1 page) fonctionne
- [ ] Statut se met à jour correctement
- [ ] Multi-URLs fonctionne
- [ ] Domain allowlist fonctionne
- [ ] Max pages est respecté
- [ ] Max depth est respecté
- [ ] Erreurs sont gérées correctement
- [ ] Question/réponse fonctionne après ingestion

---

## 🎉 Prêt à Tester !

Commencez par un exemple simple :

1. Démarrer le serveur : `python run.py`
2. Ouvrir : http://localhost:8000/
3. Utiliser l'exemple 1 ci-dessus
4. Vérifier le résultat

**Bonne chance ! 🚀**

