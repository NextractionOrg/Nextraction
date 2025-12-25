"""
Tests unitaires pour le service de nettoyage de contenu
"""
import pytest
from app.services.cleaner import ContentCleaner


def test_clean_text():
    """Test text cleaning"""
    cleaner = ContentCleaner()
    
    # Test whitespace collapse
    text = "This   has    multiple    spaces"
    cleaned = cleaner._clean_text(text)
    assert cleaned == "This has multiple spaces"
    
    # Test strip
    text = "  Leading and trailing  "
    cleaned = cleaner._clean_text(text)
    assert cleaned == "Leading and trailing"


def test_chunk_text():
    """Test text chunking"""
    cleaner = ContentCleaner()
    
    # Short text should return single chunk
    short_text = "This is a short text."
    chunks = cleaner._chunk_text(short_text, chunk_size=500, chunk_overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == short_text
    
    # Long text should be split
    long_text = ". ".join([f"Sentence {i}" for i in range(100)])
    chunks = cleaner._chunk_text(long_text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    
    # Check overlap
    if len(chunks) > 1:
        # Verify chunks don't exceed size
        for chunk in chunks:
            assert len(chunk) <= 100


def test_generate_chunk_id():
    """Test chunk ID generation"""
    cleaner = ContentCleaner()
    
    url = "https://example.com/page"
    chunk_id_1 = cleaner._generate_chunk_id(url, 0)
    chunk_id_2 = cleaner._generate_chunk_id(url, 1)
    
    assert chunk_id_1 != chunk_id_2
    assert len(chunk_id_1) == 32  # MD5 hash length


def test_clean_and_chunk_empty():
    """Test cleaning with empty pages"""
    cleaner = ContentCleaner()
    
    pages = []
    chunks = cleaner.clean_and_chunk(pages)
    assert chunks == []


def test_clean_and_chunk_minimal():
    """Test cleaning with minimal content"""
    cleaner = ContentCleaner()
    
    pages = [{
        "url": "https://example.com",
        "title": "Example",
        "html": "<html><body><p>Short content</p></body></html>"
    }]
    
    chunks = cleaner.clean_and_chunk(pages)
    # Should return empty if content is too short
    assert isinstance(chunks, list)

