from dataclasses import dataclass

@dataclass
class PrincipalData:
    url: str
    title: str
    extracted_date: str
    clean_text: str


@dataclass
class ChunkData:
    url: str
    title: str
    extracted_date: str
    chunk_index: int
    chunk_text: str
    
    
@dataclass
class VectorData:
    id: str
    values: list[float]
    url: str
    title: str
    extracted_date: str
    chunk_index: int
    chunk_text: str

    def to_pinecone_format(self):
        return {
            "id": self.id,
            "values": self.values,
            "metadata": {
                "url": self.url,
                "title": self.title,
                "extracted_date": self.extracted_date,
                "chunk_index": self.chunk_index,
                "chunk_text": self.chunk_text
            }
        }