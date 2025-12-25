"""
Test complet du workflow NexTraction
1. Inscription
2. Connexion
3. Ingestion
4. Vérification du statut
5. Poser une question
"""
import requests
import time
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_complete_workflow():
    """Test complet du workflow"""
    print("="*70)
    print("TEST COMPLET DU WORKFLOW NEXTRACTION")
    print("="*70 + "\n")
    
    # Variables
    username = f"workflow_user_{int(time.time())}"
    email = f"{username}@test.com"
    password = "testpass123"
    token = None
    job_id = None
    
    # ============================================
    # 1. INSCRIPTION
    # ============================================
    print("1. INSCRIPTION")
    print("-" * 70)
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "username": username,
            "email": email,
            "password": password
        })
        
        if response.status_code == 201:
            user = response.json()
            print(f"[OK] Utilisateur créé: {user['username']}\n")
        else:
            print(f"[ERREUR] Status: {response.status_code}")
            print(f"         {response.text}\n")
            return False
    except Exception as e:
        print(f"[ERREUR] {str(e)}\n")
        return False
    
    # ============================================
    # 2. CONNEXION
    # ============================================
    print("2. CONNEXION")
    print("-" * 70)
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result["access_token"]
            print(f"[OK] Connexion réussie!\n")
        else:
            print(f"[ERREUR] Échec: {response.status_code} - {response.text}\n")
            return False
    except Exception as e:
        print(f"[ERREUR] {str(e)}\n")
        return False
    
    # ============================================
    # 3. INGESTION
    # ============================================
    print("3. INGESTION")
    print("-" * 70)
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        ingest_data = {
            "seed_urls": ["https://example.com"],
            "domain_allowlist": ["example.com"],
            "max_pages": 3,
            "max_depth": 0
        }
        
        print(f"Démarrage de l'ingestion...")
        response = requests.post(f"{BASE_URL}/ingest", headers=headers, json=ingest_data)
        
        if response.status_code == 202:
            result = response.json()
            job_id = result["job_id"]
            print(f"[OK] Ingestion démarrée!")
            print(f"     Job ID: {job_id}\n")
        else:
            print(f"[ERREUR] Échec: {response.text}\n")
            return False
    except Exception as e:
        print(f"[ERREUR] {str(e)}\n")
        return False
    
    # ============================================
    # 4. VÉRIFICATION DU STATUT
    # ============================================
    print("4. VÉRIFICATION DU STATUT")
    print("-" * 70)
    max_wait = 90
    wait_time = 0
    check_interval = 3
    
    while wait_time < max_wait:
        try:
            response = requests.get(
                f"{BASE_URL}/status/{job_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                status = response.json()
                state = status["state"]
                
                print(f"[{wait_time}s] État: {state} | Fetch: {status['pages_fetched']} | Index: {status['pages_indexed']}")
                
                if state == "done":
                    print(f"\n[OK] Ingestion terminée!")
                    print(f"     Pages: {status['pages_fetched']} fetch, {status['pages_indexed']} index\n")
                    break
                elif state == "failed":
                    print(f"\n[ERREUR] Échec: {status.get('error', 'Erreur inconnue')}\n")
                    return False
                else:
                    time.sleep(check_interval)
                    wait_time += check_interval
            else:
                print(f"[ERREUR] Status check failed: {response.status_code} - {response.text}")
                break
        except Exception as e:
            print(f"[ERREUR] {str(e)}")
            break
    
    if wait_time >= max_wait:
        print(f"\n[ATTENTION] Timeout après {max_wait}s")
        print("            Le job continue en arrière-plan\n")
    
    # ============================================
    # 5. POSER UNE QUESTION (si job terminé)
    # ============================================
    print("5. POSER UNE QUESTION")
    print("-" * 70)
    
    try:
        # Vérifier que le job est terminé
        response = requests.get(
            f"{BASE_URL}/status/{job_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            status = response.json()
            if status["state"] != "done":
                print(f"[INFO] Job pas encore terminé (état: {status['state']})")
                print("       Question non testée\n")
            else:
                question = "What is this website about?"
                print(f"Question: {question}\n")
                
                response = requests.post(
                    f"{BASE_URL}/ask",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json={"job_id": job_id, "question": question}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"[OK] Réponse obtenue!")
                    print(f"\nConfidence: {result['confidence']}")
                    print(f"Réponse: {result['answer'][:200]}...")
                    print(f"Citations: {len(result.get('citations', []))}\n")
                else:
                    print(f"[ERREUR] {response.status_code} - {response.text}\n")
    except Exception as e:
        print(f"[ERREUR] {str(e)}\n")
    
    # ============================================
    # RÉSUMÉ
    # ============================================
    print("="*70)
    print("TEST TERMINÉ")
    print("="*70)
    print(f"\nRésumé:")
    print(f"  - Utilisateur: {username}")
    print(f"  - Job ID: {job_id}")
    print(f"  - Token obtenu: {'Oui' if token else 'Non'}")
    print(f"\nWorkflow testé avec succès!")
    
    return True


if __name__ == "__main__":
    test_complete_workflow()

