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

        
@dataclass
class SearchResult:
    url: str
    title: str
    chunk_text: str
    chunk_index: int
    extracted_date: str
    score: float


@dataclass
class LLMResponse:
    content: str
    input_tokens: int
    output_tokens: int
    model: str


@dataclass
class ConversationMessage:
    conversation_id: str
    message_id: int
    message_timestamp: str
    human_message: str
    llm_response: str
    input_tokens: int
    output_tokens: int
    model_name: str
    prompt_version: str