# Guide de Test - Authentification

## 🧪 Méthode 1: Swagger UI (Interface Web)

### Étapes:

1. **Ouvrez votre navigateur** et allez sur:
   ```
   http://localhost:8000/docs
   ```

2. **Trouvez l'endpoint `/auth/register`**
   - Cherchez dans la liste des endpoints
   - Cliquez dessus pour l'étendre

3. **Cliquez sur "Try it out"**

4. **Remplissez le formulaire JSON:**
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "testpassword123"
   }
   ```

5. **Cliquez sur "Execute"**

6. **Vérifiez la réponse:**
   - Si `201 Created`: ✅ Inscription réussie!
   - Si `400 Bad Request`: L'utilisateur existe déjà

---

## 🐍 Méthode 2: Script Python

### Utiliser le script fourni:

```bash
python test_register.py
```

### Ou créer votre propre script:

```python
import requests

BASE_URL = "http://localhost:8000"

user_data = {
    "username": "mon_utilisateur",
    "email": "mon_email@example.com",
    "password": "mon_mot_de_passe"
}

response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
print(response.json())
```

---

## 💻 Méthode 3: curl (Ligne de commande)

### Windows PowerShell:

```powershell
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "testpassword123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### Linux/Mac:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

---

## 📋 Exemple de Réponse Succès

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2024-12-25T09:45:00",
  "is_active": true
}
```

---

## ⚠️ Erreurs Possibles

### 400 Bad Request - "Username already exists"
L'utilisateur existe déjà. Essayez avec un autre username.

### 400 Bad Request - "Email already exists"
L'email est déjà utilisé. Utilisez un autre email.

### 422 Unprocessable Entity
Les données ne sont pas valides (email invalide, etc.)

### 500 Internal Server Error
Erreur serveur. Vérifiez les logs.

---

## 🔄 Après l'inscription

Une fois inscrit, vous pouvez:

1. **Vous connecter** avec `/auth/login`
2. **Obtenir votre token JWT**
3. **Utiliser le token** pour accéder aux routes protégées

---

## 🎯 Test Complet (Inscription → Login → Route Protégée)

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Inscription
register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print("Inscription:", response.json())

# 2. Login
login_data = {
    "username": "testuser",
    "password": "testpassword123"
}
response = requests.post(
    f"{BASE_URL}/auth/login",
    data=login_data
)
token = response.json()["access_token"]
print("Token:", token[:50] + "...")

# 3. Utiliser le token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print("User info:", response.json())
```

