# Guide: Utiliser /auth/login dans Swagger UI

## ⚠️ Erreur 401 "Incorrect username or password"

Si vous obtenez cette erreur, voici comment la résoudre :

## ✅ Solution Étape par Étape

### 1. D'abord, créez un utilisateur avec /auth/register

Dans Swagger UI :

1. **Trouvez `/auth/register`**
2. **Cliquez sur "Try it out"**
3. **Remplissez le JSON :**
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "testpassword123"
   }
   ```
4. **Cliquez sur "Execute"**
5. **Vérifiez que vous obtenez un `201 Created`**

### 2. Ensuite, utilisez /auth/login

Dans Swagger UI :

1. **Trouvez `/auth/login`**
2. **Cliquez sur "Try it out"**
3. **Important : Ne remplissez QUE ces champs :**
   - `username`: `testuser`
   - `password`: `testpassword123`
   
4. **Laissez les autres champs vides ou par défaut :**
   - `grant_type`: laissez vide ou `password` (Swagger le gère)
   - `scope`: laissez vide
   - `client_id`: laissez vide ou `string`
   - `client_secret`: laissez vide ou `string`

5. **Cliquez sur "Execute"**

### 3. Résultat attendu

Vous devriez obtenir une réponse `200` avec :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 🔍 Vérifications

Si ça ne fonctionne toujours pas :

1. **Vérifiez que l'utilisateur existe :**
   - Testez `/auth/register` à nouveau
   - Si vous obtenez `400` avec "Username already exists", c'est bon

2. **Vérifiez les identifiants :**
   - Username et password doivent correspondre exactement à ceux utilisés lors de l'inscription
   - Attention aux espaces et à la casse

3. **Vérifiez que le serveur tourne :**
   - Allez sur `http://localhost:8000/health`
   - Vous devriez voir `{"status":"healthy"}`

## 🐍 Alternative : Utiliser le script Python

Si Swagger pose problème, utilisez le script :

```powershell
python test_auth_complete.py
```

Ce script fait automatiquement :
1. L'inscription
2. Le login
3. Le test avec le token

## 📝 Note sur Swagger

Swagger UI utilise `OAuth2PasswordRequestForm` qui peut ajouter des paramètres supplémentaires. Ces paramètres sont ignorés par notre endpoint, mais assurez-vous que `username` et `password` sont bien remplis.

