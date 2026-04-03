import re
from pathlib import Path

from bs4 import BeautifulSoup
import pandas as pd


# Etiquetas sin contenido informativo
NOISE_TAGS = [
    "nav", "header", "footer", "aside", "script",
    "style", "noscript", "iframe", "form", "button",
    "figure", "svg", "img", "input", "select"
]

# Etiquetas de navegación o banners
NOISE_CLASS_TAGS = [
    "nav", "menu", "footer", "header", "banner",
    "cookie", "breadcrumb", "sidebar", "social",
    "promo", "advertisement", "modal", "popup"
]

class Cleander ():
    
    def _normalize_data(self, text):
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[^\w\s.,;:()\-\/#@%\n\"\'áéíóúÁÉÍÓÚñÑüÜ¿¡€$]", "", text)
        return text.strip()
    
    def clean_page(self, page_url, page_html):
        
        
        soup = BeautifulSoup(page_html, "html.parser")
        
        # Eliminar elementos de ruido
        for tag in NOISE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()
                
        # Eliminar elementos de navegación o banners
        for tag in NOISE_CLASS_TAGS:
            for element in soup.find_all(tag):
                element.decompose()
                
        # Extraer texto con jerarquía de encabezados
        lines = []
        for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "td"]):
            text = element.get_text(separator=" ", strip=True)
            if not text:
                continue
            tag = element.name
            if tag == "h1":
                lines.append(f"\n # {text}\n")
            elif tag == "h2":
                lines.append(f"\n ## {text}\n")
            elif tag == "h3":
                lines.append(f"\n ### {text}\n")
            elif tag == "h4":
                lines.append(f"\n #### {text}\n")
            else:
                lines.append(text)
 
        raw_text = "\n".join(lines)
        print(f"INFO: Limpieza de: {page_url}")
        return self._normalize_data(raw_text)