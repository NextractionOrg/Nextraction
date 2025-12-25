"""
Tests d'intégration pour l'authentification
"""
import requests
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_register():
    """Test d'inscription d'utilisateur"""
    print("="*60)
    print("TEST: Inscription d'utilisateur")
    print("="*60)
    
    user_data = {
        "username": f"testuser_{int(__import__('time').time())}",
        "email": f"test_{int(__import__('time').time())}@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        if response.status_code == 201:
            user = response.json()
            print(f"[OK] Utilisateur créé: {user['username']}")
            print(f"     ID: {user['id']}")
            return user
        elif response.status_code == 400:
            print(f"[INFO] Utilisateur existe déjà: {response.json()['detail']}")
            return None
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            print(f"         {response.text}")
            return None
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        return None


def test_login(username: str, password: str):
    """Test de connexion"""
    print("\n" + "="*60)
    print("TEST: Connexion")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result["access_token"]
            print(f"[OK] Connexion réussie!")
            print(f"     Token: {token[:30]}...{token[-20:]}")
            return token
        else:
            print(f"[ERREUR] Échec: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        return None


def test_me(token: str):
    """Test de route protégée /auth/me"""
    print("\n" + "="*60)
    print("TEST: Route protégée /auth/me")
    print("="*60)
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"[OK] Accès réussi!")
            print(f"     Username: {user_info['username']}")
            print(f"     Email: {user_info['email']}")
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        return False


def test_protected_route_without_token():
    """Test d'accès à une route protégée sans token"""
    print("\n" + "="*60)
    print("TEST: Route protégée sans token (devrait échouer)")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/ingest",
            json={
                "seed_urls": ["https://example.com"],
                "domain_allowlist": ["example.com"],
                "max_pages": 1,
                "max_depth": 0
            }
        )
        
        if response.status_code == 401 or response.status_code == 403:
            print(f"[OK] Protection active! (Status: {response.status_code})")
            return True
        else:
            print(f"[ATTENTION] Status inattendu: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        return False


def run_all_tests():
    """Exécute tous les tests d'authentification"""
    print("\n" + "="*60)
    print("TESTS D'AUTHENTIFICATION COMPLETS")
    print("="*60 + "\n")
    
    # Test 1: Inscription
    user = test_register()
    
    if not user:
        # Essayer avec des identifiants par défaut
        username = "testuser"
        password = "testpassword123"
        print(f"\n[INFO] Utilisation d'identifiants par défaut: {username}")
    else:
        username = user["username"]
        password = "testpassword123"
    
    # Test 2: Connexion
    token = test_login(username, password)
    
    if not token:
        print("\n[ERREUR] Impossible de continuer sans token")
        return False
    
    # Test 3: Route protégée avec token
    test_me(token)
    
    # Test 4: Route protégée sans token
    test_protected_route_without_token()
    
    print("\n" + "="*60)
    print("TESTS TERMINÉS")
    print("="*60)
    
    return True


if __name__ == "__main__":
    run_all_tests()

