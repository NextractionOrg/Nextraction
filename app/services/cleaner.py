from bs4 import BeautifulSoup
import re
from typing import List, Dict
import hashlib
from app.config import settings
from app.utils.logger import logger


class ContentCleaner:
    """Service for cleaning HTML and chunking text"""
    
    def __init__(self):
        self.processed_content: List[Dict] = []
    
    def _remove_boilerplate(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove navigation, footer, and other boilerplate"""
        # Remove script and style elements
        for element in soup(["script", "style", "noscript", "iframe"]):
            element.decompose()
        
        # Remove common boilerplate classes/ids
        for selector in [
            "nav", "footer", "header", "aside",
            "[class*='nav']", "[class*='menu']",
            "[class*='footer']", "[class*='sidebar']",
            "[id*='nav']", "[id*='menu']",
            "[id*='footer']", "[id*='sidebar']"
        ]:
            for element in soup.select(selector):
                element.decompose()
        
        return soup
    
    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract page title"""
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try h1 as fallback
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()
        
        # Use URL as last resort
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.path.split("/")[-1] or parsed.netloc
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content using readability-style heuristics"""
        # Try common content selectors
        content_selectors = [
            "main", "article", "[role='main']",
            ".content", ".post", ".entry",
            "#content", "#main", "#article"
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                return " ".join([elem.get_text() for elem in elements])
        
        # Fallback: use body
        body = soup.find("body")
        if body:
            return body.get_text()
        
        return soup.get_text()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
    
    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = max(
                    text.rfind(". ", start, end),
                    text.rfind("! ", start, end),
                    text.rfind("? ", start, end),
                    text.rfind("\n", start, end)
                )
                
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start with overlap
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def _generate_chunk_id(self, url: str, chunk_index: int) -> str:
        """Generate a stable chunk ID"""
        content = f"{url}:{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _deduplicate_pages(self, pages: List[Dict]) -> List[Dict]:
        """Remove near-duplicate pages based on content hash"""
        seen_hashes = set()
        unique_pages = []
        
        for page in pages:
            # Create content hash (first 1000 chars)
            content_preview = page.get("text", "")[:1000]
            content_hash = hashlib.md5(content_preview.encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_pages.append(page)
            else:
                logger.info(f"Skipping duplicate page: {page.get('url')}")
        
        return unique_pages
    
    def clean_and_chunk(self, pages: List[Dict]) -> List[Dict]:
        """Clean HTML pages and chunk into passages"""
        self.processed_content = []
        
        for page in pages:
            try:
                html = page["html"]
                url = page["url"]
                fetched_at = page["fetched_at"]
                
                soup = BeautifulSoup(html, "html.parser")
                
                # Remove boilerplate
                soup = self._remove_boilerplate(soup)
                
                # Extract title
                title = self._extract_title(soup, url)
                
                # Extract main content
                raw_text = self._extract_main_content(soup)
                text = self._clean_text(raw_text)
                
                # Skip if too short (likely not useful content)
                if len(text) < 100:
                    logger.warning(f"Skipping page with too little content: {url}")
                    continue
                
                # Chunk the text
                chunks = self._chunk_text(text, settings.chunk_size, settings.chunk_overlap)
                
                # Create chunk documents
                for idx, chunk_text in enumerate(chunks):
                    chunk_id = self._generate_chunk_id(url, idx)
                    
                    chunk_doc = {
                        "chunkid": chunk_id,
                        "url": url,
                        "title": title,
                        "text": chunk_text,
                        "chunk_index": idx,
                        "total_chunks": len(chunks),
                        "fetched_at": fetched_at,
                    }
                    
                    self.processed_content.append(chunk_doc)
                
                logger.info(f"Processed {url}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error processing page {page.get('url', 'unknown')}: {str(e)}")
                continue
        
        # Deduplicate
        self.processed_content = self._deduplicate_pages(self.processed_content)
        
        logger.info(f"Created {len(self.processed_content)} chunks from {len(pages)} pages")
        return self.processed_content

