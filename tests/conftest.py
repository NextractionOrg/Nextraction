"""
Configuration pytest pour les tests
"""
import pytest
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration pytest
@pytest.fixture(scope="session")
def base_url():
    """URL de base pour les tests d'intégration"""
    import os
    return os.getenv("BASE_URL", "http://localhost:8000")
