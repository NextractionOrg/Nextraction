"""
Script principal pour exécuter tous les tests
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def main():
    """Exécute tous les tests"""
    print("="*70)
    print("EXÉCUTION DE TOUS LES TESTS NEXTRACTION")
    print("="*70)
    print("\nAssurez-vous que le serveur est démarré (python run.py)\n")
    
    # Tests d'authentification
    print("\n" + "="*70)
    print("1. TESTS D'AUTHENTIFICATION")
    print("="*70)
    try:
        from tests.integration.test_auth import run_all_tests as test_auth
        test_auth()
    except Exception as e:
        print(f"[ERREUR] Tests d'authentification: {str(e)}")
    
    # Tests d'ingestion
    print("\n" + "="*70)
    print("2. TESTS D'INGESTION")
    print("="*70)
    try:
        from tests.integration.test_ingest import run_all_tests as test_ingest
        test_ingest()
    except Exception as e:
        print(f"[ERREUR] Tests d'ingestion: {str(e)}")
    
    # Tests de workflow complet
    print("\n" + "="*70)
    print("3. TESTS DE WORKFLOW COMPLET")
    print("="*70)
    try:
        from tests.integration.test_workflow import test_complete_workflow
        test_complete_workflow()
    except Exception as e:
        print(f"[ERREUR] Tests de workflow: {str(e)}")
    
    print("\n" + "="*70)
    print("TOUS LES TESTS TERMINÉS")
    print("="*70)


if __name__ == "__main__":
    main()

