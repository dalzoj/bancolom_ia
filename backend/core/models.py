from dataclasses import dataclass

@dataclass
class PrincipalData:
    url: str
    title: str
    extracted_date: str
    clean_text: str