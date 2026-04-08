from dataclasses import dataclass


@dataclass
class PrincipalData:
    url: str
    title: str
    extracted_date: str
    clean_text: str
    category: str


@dataclass
class ChunkData:
    url: str
    title: str
    extracted_date: str
    chunk_index: int
    chunk_text: str
    category: str


@dataclass
class VectorData:
    id: str
    values: list
    url: str
    title: str
    extracted_date: str
    chunk_index: int
    chunk_text: str
    category: str


@dataclass
class SearchResult:
    url: str
    title: str
    chunk_text: str
    chunk_index: int
    extracted_date: str
    score: float
    category: str


@dataclass
class LLMResponse:
    content: str
    input_tokens: int
    output_tokens: int
    model: str


@dataclass
class LLMToolCall:
    id: str
    tool_name: str
    tool_args: dict


@dataclass
class LLMFirstTurnResponse:
    tool_calls: list | None
    tool_plan: str | None
    content: str | None
    input_tokens: int
    output_tokens: int
    model: str

    @property
    def has_tool_calls(self):
        return bool(self.tool_calls)


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
    interaction_time: float
