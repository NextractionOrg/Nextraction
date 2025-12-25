# Guide d'Authentification JWT

## 🔐 Système d'Authentification

Le projet inclut maintenant un système d'authentification complet avec JWT (JSON Web Tokens).

## 📋 Endpoints d'Authentification

### 1. POST /auth/register
Créer un nouveau compte utilisateur.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Response:**
```json
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T00:00:00",
  "is_active": true
}
```

### 2. POST /auth/login
Se connecter et obtenir un token JWT.

**Request (form-data):**
```
username: john_doe
password: secure_password123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. GET /auth/me
Obtenir les informations de l'utilisateur connecté.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T00:00:00",
  "is_active": true
}
```

## 🔒 Routes Protégées

Les routes suivantes nécessitent maintenant une authentification:

- `POST /ingest` - Démarre une ingestion
- `GET /status/{job_id}` - Vérifie le statut d'un job
- `POST /ask` - Pose une question

**Note:** `/health` reste publique (pas d'authentification requise)

## 📝 Utilisation avec curl

### 1. S'inscrire
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. Se connecter
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

Sauvegardez le `access_token` de la réponse.

### 3. Utiliser une route protégée
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "seed_urls": ["https://example.com"],
    "domain_allowlist": ["example.com"],
    "max_pages": 10,
    "max_depth": 1
  }'
```

## 🐍 Utilisation avec Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. S'inscrire
response = requests.post(f"{BASE_URL}/auth/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
})
print(response.json())

# 2. Se connecter
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "testuser", "password": "password123"}
)
token = response.json()["access_token"]
print(f"Token: {token}")

# 3. Utiliser une route protégée
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/ingest",
    headers=headers,
    json={
        "seed_urls": ["https://example.com"],
        "domain_allowlist": ["example.com"],
        "max_pages": 10,
        "max_depth": 1
    }
)
print(response.json())
```

## ⚙️ Configuration

Variables d'environnement à ajouter dans `.env`:

```env
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Password Hashing
PASSWORD_SALT=your-salt-here-change-in-production
```

**Important:** Changez ces valeurs en production!

## 🔐 Sécurité

- Les mots de passe sont hashés avec SHA-256 + salt
- Les tokens JWT expirent après 24h (configurable)
- Les routes protégées vérifient automatiquement le token
- Les utilisateurs inactifs ne peuvent pas se connecter

## 📊 Stockage des Utilisateurs

**Actuellement:** Stockage en mémoire (perdu au redémarrage)

**Pour la production:** Remplacez `users_db` dans `app/auth/service.py` par une base de données (PostgreSQL, MongoDB, etc.)

## 🧪 Test dans l'Interface Swagger

1. Allez sur `http://localhost:8000/docs`
2. Cliquez sur `/auth/register` → "Try it out" → Créez un utilisateur
3. Cliquez sur `/auth/login` → "Try it out" → Connectez-vous
4. Cliquez sur le bouton "Authorize" en haut
5. Entrez: `Bearer <votre_token>`
6. Toutes les routes protégées seront maintenant accessibles

