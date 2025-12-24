import asyncio
import httpx
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict, Optional
from datetime import datetime
import hashlib
from app.config import settings
from app.utils.logger import logger


class WebFetcher:
    """Service for fetching and crawling web pages"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.fetch_timeout,
            follow_redirects=True,
            headers={"User-Agent": settings.fetch_user_agent}
        )
        self.visited_urls: Set[str] = set()
        self.fetched_pages: List[Dict] = []
        self.rate_limiter = asyncio.Semaphore(1)  # Simple rate limiting
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _is_allowed_domain(self, url: str, allowlist: List[str]) -> bool:
        """Check if URL belongs to an allowed domain"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return any(allowed.lower() in domain for allowed in allowlist)
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication"""
        parsed = urlparse(url)
        # Remove fragment and normalize
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized.lower()
    
    async def _fetch_page(self, url: str, allowlist: List[str]) -> Optional[Dict]:
        """Fetch a single page with retries"""
        normalized = self._normalize_url(url)
        
        if normalized in self.visited_urls:
            return None
        
        if not self._is_allowed_domain(url, allowlist):
            logger.warning(f"URL not in allowlist: {url}")
            return None
        
        # Rate limiting
        async with self.rate_limiter:
            await asyncio.sleep(settings.fetch_rate_limit)
            
            for attempt in range(settings.fetch_max_retries):
                try:
                    response = await self.client.get(url)
                    response.raise_for_status()
                    
                    # Check content type
                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" not in content_type:
                        logger.warning(f"Non-HTML content: {url} ({content_type})")
                        return None
                    
                    self.visited_urls.add(normalized)
                    
                    return {
                        "url": url,
                        "html": response.text,
                        "status_code": response.status_code,
                        "content_type": content_type,
                        "fetched_at": datetime.utcnow().isoformat(),
                    }
                    
                except httpx.HTTPStatusError as e:
                    logger.warning(f"HTTP error for {url}: {e.response.status_code}")
                    if e.response.status_code == 404:
                        return None
                    if attempt < settings.fetch_max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        return None
                        
                except (httpx.RequestError, asyncio.TimeoutError) as e:
                    logger.warning(f"Request error for {url}: {str(e)}")
                    if attempt < settings.fetch_max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        return None
        
        return None
    
    def _extract_links(self, html: str, base_url: str, allowlist: List[str]) -> List[str]:
        """Extract links from HTML that are in the allowlist"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, "html.parser")
        links = []
        
        for tag in soup.find_all("a", href=True):
            href = tag.get("href")
            if not href:
                continue
            
            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)
            
            # Remove fragment
            parsed = urlparse(absolute_url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                clean_url += f"?{parsed.query}"
            
            if self._is_allowed_domain(clean_url, allowlist):
                links.append(clean_url)
        
        return links
    
    async def crawl(
        self,
        seed_urls: List[str],
        domain_allowlist: List[str],
        max_pages: int,
        max_depth: int
    ) -> List[Dict]:
        """Crawl web pages starting from seed URLs"""
        self.visited_urls.clear()
        self.fetched_pages.clear()
        
        queue: List[tuple[str, int]] = [(url, 0) for url in seed_urls]
        
        while queue and len(self.fetched_pages) < max_pages:
            url, depth = queue.pop(0)
            
            if depth > max_depth:
                continue
            
            page = await self._fetch_page(url, domain_allowlist)
            
            if page:
                self.fetched_pages.append(page)
                
                # Extract links for next level if not at max depth
                if depth < max_depth and len(self.fetched_pages) < max_pages:
                    links = self._extract_links(page["html"], url, domain_allowlist)
                    for link in links:
                        normalized = self._normalize_url(link)
                        if normalized not in self.visited_urls:
                            queue.append((link, depth + 1))
        
        logger.info(f"Fetched {len(self.fetched_pages)} pages")
        return self.fetched_pages

