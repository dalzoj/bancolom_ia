import time
import json
import pandas as pd
from datetime import datetime
from backend.core.config_loader import config
from playwright.sync_api import sync_playwright
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from pathlib import Path
from bs4 import BeautifulSoup


class Finder():
    
    def __init__(self):
        self._base_url = config.scraping_base_url
        self._domain = urlparse(self._base_url).netloc
        self._max_pages = config.scraping_max_pages
        self._max_depth = config.scraping_max_depth
        self._delay = config.scraping_delay
        self._respect_robots = config.scraping_respect_robots
        self._robot_parser = self._load_robots()
        self._output_path = Path(config.scraping_output_path)
        self._output_path.mkdir(parents=True, exist_ok=True)
        
    def _load_robots(self):
        if not self._respect_robots:
            return None
        rfp = RobotFileParser()
        rfp.set_url(f"https://{self._domain}/robots.txt")
        rfp.read()
        return rfp
        
    def _is_allowed(self, url):
        if self._robot_parser is None:
            return True
        return self._robot_parser.can_fetch("*", url)
    
    def _normalize_url(self, base, href):
        url = urljoin(base, href)
        parsed = urlparse(url)
        return parsed._replace(fragment="", query="").geturl()
    
    def _is_internal(self, url):
        parsed = urlparse(url)
        return parsed.netloc == self._domain or parsed.netloc == ""
    
    def _save_data(self, data):
        print(f"INFO: Guardando datos raw en: {self._output_path}")
        
        df = pd.DataFrame(data, columns = ["url", "title", "extracted_date", "html"])
        df.to_csv(self._output_path/"raw_data.csv", index=False, encoding="utf-8", sep="|")
        df.to_parquet(self._output_path/"raw_data.parquet", index=False)
        
    def find(self):
        print(f"INFO: Iniciando buscador desde: {self._base_url}")
        
        visited = set()
        queue = [(self._base_url, 0)]
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
 
            while queue and len(results) < self._max_pages:
                url, depth = queue.pop(0)
 
                if url in visited or depth > self._max_depth:
                    continue
                if not self._is_allowed(url):
                    continue
 
                visited.add(url)

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_load_state("domcontentloaded")
                    html = page.content()
                    title = page.title()
                except Exception as e:
                    print(f"ERROR: No se puede extraer la página {url} — {e}")
                    continue
 
                results.append({
                    "url": url,
                    "title": title,
                    "extracted_date": datetime.utcnow().isoformat(),
                    "html": html.replace("\n", " ").replace("\r", " ")
                })
 
                print(f"INFO: Encontrado [{len(results)}/{self._max_pages}]: -> {url}")
 
                soup = BeautifulSoup(html, "html.parser")
                plain_text = soup.get_text(separator=" ", strip=True)
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"]
                    full_url = self._normalize_url(url, href)
                    if (
                        self._is_internal(full_url)
                        and full_url not in visited
                        and full_url.startswith(self._base_url)
                    ):
                        queue.append((full_url, depth + 1))
 
                time.sleep(self._delay)
 
            browser.close()
            
        self._save_data(results)
        
        return results