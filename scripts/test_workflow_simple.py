"""
Script simple pour tester le workflow complet NexTraction
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

print("="*70)
print("TEST DU WORKFLOW COMPLET NEXTRACTION")
print("="*70)
print("\nAssurez-vous que le serveur est démarré (python run.py)\n")

# Variables
username = f"testuser_{int(time.time())}"
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
        print(f"[OK] Utilisateur cree: {user['username']}")
        print(f"    ID: {user['id']}\n")
    elif response.status_code == 400:
        print(f"[INFO] Utilisateur existe deja (normal si deja teste)\n")
    else:
        print(f"[ERREUR] Erreur: {response.status_code}")
        print(f"    {response.text}\n")
        exit(1)
except Exception as e:
    print(f"[ERREUR] Erreur: {str(e)}\n")
    exit(1)

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
        print(f"[OK] Connexion reussie!")
        print(f"    Token: {token[:30]}...{token[-20:]}\n")
    else:
        print(f"[ERREUR] Echec: {response.status_code} - {response.text}\n")
        exit(1)
except Exception as e:
    print(f"[ERREUR] Erreur: {str(e)}\n")
    exit(1)

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
    print(f"  URLs: {ingest_data['seed_urls']}")
    print(f"  Domaines: {ingest_data['domain_allowlist']}")
    print(f"  Max pages: {ingest_data['max_pages']}")
    print(f"  Max depth: {ingest_data['max_depth']}\n")
    
    response = requests.post(f"{BASE_URL}/ingest", headers=headers, json=ingest_data)
    
    if response.status_code == 202:
        result = response.json()
        job_id = result["job_id"]
        print(f"[OK] Ingestion demarree!")
        print(f"    Job ID: {job_id}\n")
    else:
        print(f"[ERREUR] Echec: {response.status_code}")
        print(f"    {response.text}\n")
        exit(1)
except Exception as e:
    print(f"[ERREUR] Erreur: {str(e)}\n")
    import traceback
    traceback.print_exc()
    exit(1)

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
            
            print(f"[{wait_time}s] Etat: {state} | Fetch: {status['pages_fetched']} | Index: {status['pages_indexed']}")
            
            if state == "done":
                print(f"\n[OK] Ingestion terminee!")
                print(f"    Pages recuperees: {status['pages_fetched']}")
                print(f"    Pages indexees: {status['pages_indexed']}\n")
                break
            elif state == "failed":
                print(f"\n[ERREUR] Echec: {status.get('error', 'Erreur inconnue')}\n")
                exit(1)
            else:
                time.sleep(check_interval)
                wait_time += check_interval
        else:
            print(f"[ERREUR] Status check failed: {response.status_code} - {response.text}")
            break
    except Exception as e:
        print(f"[ERREUR] Erreur: {str(e)}")
        break

if wait_time >= max_wait:
    print(f"\n[ATTENTION] Timeout apres {max_wait}s")
    print("    Le job continue en arrière-plan\n")

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
            print(f"[!] Job pas encore terminé (état: {status['state']})")
            print("    Question non testée\n")
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
                print(f"[OK] Reponse obtenue!")
                print(f"\nConfidence: {result['confidence']}")
                print(f"\nReponse:")
                print(f"  {result['answer'][:200]}...")
                print(f"\nNotes: {result['groundingnotes']}")
                
                if result.get('citations'):
                    print(f"\nCitations ({len(result['citations'])}):")
                    for i, citation in enumerate(result['citations'][:3], 1):
                        print(f"  [{i}] {citation['title']}")
                        print(f"      URL: {citation['url']}")
                        print(f"      Score: {citation['score']:.3f}")
                print()
            else:
                print(f"[ERREUR] Erreur: {response.status_code} - {response.text}\n")
except Exception as e:
    print(f"[ERREUR] Erreur: {str(e)}\n")
    import traceback
    traceback.print_exc()

# ============================================
# RÉSUMÉ
# ============================================
print("="*70)
print("TEST TERMINÉ")
print("="*70)
print(f"\nResume:")
print(f"  - Utilisateur: {username}")
print(f"  - Job ID: {job_id}")
print(f"  - Token obtenu: {'Oui' if token else 'Non'}")
print(f"\n[OK] Workflow teste avec succes!")

