"""
Script pour nettoyer les anciens fichiers de test du répertoire racine
"""
import os
import shutil
from pathlib import Path

# Fichiers de test à supprimer (remplacés par tests/)
OLD_TEST_FILES = [
    "test_auth.py",
    "test_auth_complete.py",
    "test_register.py",
    "test_login.py",
    "test_ingest_direct.py",
    "test_workflow.py",
    "test_workflow_complete.py",
    "test_simple.py",
]

def cleanup():
    """Supprime les anciens fichiers de test"""
    print("="*60)
    print("NETTOYAGE DES ANCIENS FICHIERS DE TEST")
    print("="*60)
    print("\nCes fichiers ont été remplacés par les tests organisés dans tests/\n")
    
    removed = []
    not_found = []
    
    for filename in OLD_TEST_FILES:
        filepath = Path(filename)
        if filepath.exists():
            try:
                filepath.unlink()
                removed.append(filename)
                print(f"[OK] Supprimé: {filename}")
            except Exception as e:
                print(f"[ERREUR] Impossible de supprimer {filename}: {str(e)}")
        else:
            not_found.append(filename)
    
    print("\n" + "="*60)
    print("RÉSUMÉ")
    print("="*60)
    print(f"Fichiers supprimés: {len(removed)}")
    print(f"Fichiers non trouvés: {len(not_found)}")
    
    if removed:
        print("\nFichiers supprimés:")
        for f in removed:
            print(f"  - {f}")
    
    if not_found:
        print("\nFichiers non trouvés (déjà supprimés ou inexistants):")
        for f in not_found:
            print(f"  - {f}")
    
    print("\n[INFO] Les nouveaux tests sont dans tests/")
    print("       Voir tests/README.md pour les instructions")

if __name__ == "__main__":
    response = input("Voulez-vous supprimer les anciens fichiers de test? (o/n): ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        cleanup()
    else:
        print("Annulé.")

