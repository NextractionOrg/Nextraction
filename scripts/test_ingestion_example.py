"""
Exemple de script pour tester l'ingestion NexTraction
"""
import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_ingestion_simple():
    """Test d'ingestion simple avec example.com"""
    print_section("TEST D'INGESTION SIMPLE")
    
    # 1. Connexion
    print("\n1. Connexion...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        
        if not login_response.ok:
            print(f"❌ Erreur de connexion: {login_response.status_code}")
            print("   Assurez-vous d'avoir créé un utilisateur avec:")
            print("   - Username: testuser")
            print("   - Password: testpass123")
            return False
        
        token = login_response.json()["access_token"]
        print(f"✅ Token obtenu: {token[:20]}...")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("   Assurez-vous que le serveur est démarré (python run.py)")
        return False
    
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
        "user_notes": "Test d'ingestion simple - example.com"
    }
    
    try:
        ingest_response = requests.post(
            f"{BASE_URL}/ingest",
            json=ingest_data,
            headers=headers
        )
        
        if not ingest_response.ok:
            print(f"❌ Erreur d'ingestion: {ingest_response.status_code}")
            print(f"   {ingest_response.text}")
            return False
        
        result = ingest_response.json()
        job_id = result["job_id"]
        accepted_pages = result.get("accepted_pages", 0)
        
        print(f"✅ Job créé: {job_id}")
        print(f"   Pages acceptées: {accepted_pages}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # 3. Vérifier le statut
    print("\n3. Vérification du statut...")
    print("   (Attente de la fin de l'ingestion...)")
    
    max_wait = 60  # Maximum 60 secondes
    start_time = time.time()
    
    while True:
        try:
            status_response = requests.get(
                f"{BASE_URL}/status/{job_id}",
                headers=headers
            )
            
            if not status_response.ok:
                print(f"❌ Erreur de statut: {status_response.status_code}")
                break
            
            status = status_response.json()
            state = status.get("state", "unknown")
            pages_fetched = status.get("pages_fetched", 0)
            pages_indexed = status.get("pages_indexed", 0)
            
            print(f"   État: {state} | Pages: {pages_fetched} récupérées, {pages_indexed} indexées")
            
            if state == "done":
                print(f"\n✅ Ingestion terminée avec succès!")
                print(f"   Pages récupérées: {pages_fetched}")
                print(f"   Pages indexées: {pages_indexed}")
                return True
            elif state == "failed":
                error = status.get("error", "Erreur inconnue")
                print(f"\n❌ Ingestion échouée: {error}")
                return False
            
            # Timeout
            if time.time() - start_time > max_wait:
                print(f"\n⏱️  Timeout après {max_wait} secondes")
                return False
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrompu par l'utilisateur")
            return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

def test_ingestion_advanced():
    """Test d'ingestion avancé avec documentation Python"""
    print_section("TEST D'INGESTION AVANCÉ")
    
    # 1. Connexion
    print("\n1. Connexion...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        
        if not login_response.ok:
            print("❌ Erreur de connexion. Créez d'abord un utilisateur.")
            return False
        
        token = login_response.json()["access_token"]
        print(f"✅ Token obtenu")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Ingestion
    print("\n2. Lancement de l'ingestion (documentation Python)...")
    ingest_data = {
        "seed_urls": [
            "https://docs.python.org/3/tutorial/introduction.html"
        ],
        "domain_allowlist": ["docs.python.org"],
        "max_pages": 5,
        "max_depth": 1,
        "user_notes": "Test documentation Python"
    }
    
    try:
        ingest_response = requests.post(
            f"{BASE_URL}/ingest",
            json=ingest_data,
            headers=headers
        )
        
        if not ingest_response.ok:
            print(f"❌ Erreur: {ingest_response.status_code}")
            print(f"   {ingest_response.text}")
            return False
        
        result = ingest_response.json()
        job_id = result["job_id"]
        print(f"✅ Job créé: {job_id}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # 3. Vérifier le statut
    print("\n3. Suivi de la progression...")
    max_wait = 120  # 2 minutes pour plus de pages
    
    start_time = time.time()
    while True:
        try:
            status_response = requests.get(
                f"{BASE_URL}/status/{job_id}",
                headers=headers
            )
            status = status_response.json()
            state = status.get("state", "unknown")
            pages_fetched = status.get("pages_fetched", 0)
            pages_indexed = status.get("pages_indexed", 0)
            
            print(f"   État: {state} | Pages: {pages_fetched}/{pages_indexed}")
            
            if state == "done":
                print(f"\n✅ Ingestion terminée!")
                return True
            elif state == "failed":
                print(f"\n❌ Échec: {status.get('error', 'Erreur inconnue')}")
                return False
            
            if time.time() - start_time > max_wait:
                print(f"\n⏱️  Timeout")
                return False
            
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrompu")
            return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

def main():
    print("\n" + "="*70)
    print("  EXEMPLES DE TEST D'INGESTION - NEXTRACTION")
    print("="*70)
    print("\nAssurez-vous que:")
    print("  1. Le serveur est démarré (python run.py)")
    print("  2. Un utilisateur 'testuser' existe (password: testpass123)")
    print("  3. Vous avez configuré .env avec vos clés API (ou embeddings locaux)")
    
    print("\nChoisissez un test:")
    print("  1. Test simple (example.com - rapide)")
    print("  2. Test avancé (documentation Python - plus long)")
    print("  3. Les deux")
    
    choice = input("\nVotre choix (1/2/3): ").strip()
    
    if choice == "1":
        success = test_ingestion_simple()
    elif choice == "2":
        success = test_ingestion_advanced()
    elif choice == "3":
        success1 = test_ingestion_simple()
        if success1:
            time.sleep(2)
            success = test_ingestion_advanced()
        else:
            success = False
    else:
        print("❌ Choix invalide")
        return
    
    print("\n" + "="*70)
    if success:
        print("✅ Tests terminés avec succès!")
    else:
        print("❌ Tests échoués. Vérifiez les erreurs ci-dessus.")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompu par l'utilisateur")
        sys.exit(0)

