"""
Tests d'intégration pour l'ingestion
"""
import requests
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def get_auth_token(username="testuser", password="testpassword123"):
    """Obtenir un token d'authentification"""
    try:
        # Essayer de se connecter
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        
        # Si échec, créer l'utilisateur
        requests.post(f"{BASE_URL}/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        # Réessayer la connexion
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        
        return None
    except Exception as e:
        print(f"Erreur lors de l'authentification: {str(e)}")
        return None


def test_ingest():
    """Test d'ingestion simple"""
    print("="*60)
    print("TEST: Ingestion")
    print("="*60)
    
    token = get_auth_token()
    if not token:
        print("[ERREUR] Impossible d'obtenir un token")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    ingest_data = {
        "seed_urls": ["https://example.com"],
        "domain_allowlist": ["example.com"],
        "max_pages": 1,
        "max_depth": 0
    }
    
    try:
        print(f"Démarrage de l'ingestion...")
        response = requests.post(f"{BASE_URL}/ingest", headers=headers, json=ingest_data, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 202:
            result = response.json()
            job_id = result["job_id"]
            print(f"[OK] Ingestion démarrée!")
            print(f"     Job ID: {job_id}")
            return job_id
        else:
            print(f"[ERREUR] Échec: {response.status_code}")
            print(f"         {response.text}")
            return None
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        return None


def test_status(job_id: str):
    """Test de vérification du statut"""
    print("\n" + "="*60)
    print("TEST: Statut du job")
    print("="*60)
    
    token = get_auth_token()
    if not token:
        print("[ERREUR] Impossible d'obtenir un token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/status/{job_id}", headers=headers)
        
        if response.status_code == 200:
            status = response.json()
            print(f"[OK] Statut récupéré:")
            print(f"     État: {status['state']}")
            print(f"     Pages fetchées: {status['pages_fetched']}")
            print(f"     Pages indexées: {status['pages_indexed']}")
            if status.get('error'):
                print(f"     Erreur: {status['error']}")
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        return False


def test_ask(job_id: str):
    """Test de question"""
    print("\n" + "="*60)
    print("TEST: Poser une question")
    print("="*60)
    
    token = get_auth_token()
    if not token:
        print("[ERREUR] Impossible d'obtenir un token")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Vérifier d'abord que le job est terminé
    status_response = requests.get(f"{BASE_URL}/status/{job_id}", headers={"Authorization": f"Bearer {token}"})
    if status_response.status_code == 200:
        status = status_response.json()
        if status["state"] != "done":
            print(f"[INFO] Job pas encore terminé (état: {status['state']})")
            return False
    
    try:
        question = "What is this website about?"
        print(f"Question: {question}\n")
        
        response = requests.post(
            f"{BASE_URL}/ask",
            headers=headers,
            json={"job_id": job_id, "question": question}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Réponse obtenue!")
            print(f"     Confidence: {result['confidence']}")
            print(f"     Réponse: {result['answer'][:150]}...")
            print(f"     Citations: {len(result.get('citations', []))}")
            return True
        else:
            print(f"[ERREUR] Status: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        return False


def run_all_tests():
    """Exécute tous les tests d'ingestion"""
    print("\n" + "="*60)
    print("TESTS D'INGESTION")
    print("="*60 + "\n")
    
    # Test 1: Ingestion
    job_id = test_ingest()
    
    if not job_id:
        print("\n[ERREUR] Impossible de continuer sans job_id")
        return False
    
    # Test 2: Statut
    test_status(job_id)
    
    # Attendre un peu pour que le job progresse
    print("\n[INFO] Attente de 5 secondes...")
    time.sleep(5)
    
    # Test 3: Statut à nouveau
    test_status(job_id)
    
    # Test 4: Question (si job terminé)
    # Note: Le job peut ne pas être terminé, donc ce test peut échouer
    test_ask(job_id)
    
    print("\n" + "="*60)
    print("TESTS TERMINÉS")
    print("="*60)
    
    return True


if __name__ == "__main__":
    run_all_tests()

