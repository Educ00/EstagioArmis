from datetime import datetime

from langchain_community.callbacks import OpenAICallbackHandler
from langchain_core.documents import Document


class IndexBenchmarkDto:
    def __init__(self, filename: str, method: int, completion_llm_name: str, embeddings_llm_name: str, neo4j_cb : OpenAICallbackHandler, doc : Document, start_azure : datetime, end_azure: datetime, azure_chunk_size: int, azure_chunk_overlap : int, start_neo4j : datetime, end_neo4j: datetime, number_nodes : int, number_relationships : int, neo4j_chunk_size : int, neo4j_chunk_overlap : int, start_chroma : datetime, end_chroma : datetime, embedding_tokens : int, chroma_chunk_size : int, chroma_chunk_overlap : int):
        self.filename : str = filename
        self.method : int = method
        self.completion_llm_name : str = completion_llm_name
        self.embeddings_llm_name : str = embeddings_llm_name
        self.neo4j_prompt_tokens : int = neo4j_cb.prompt_tokens
        self.neo4j_prompt_tokens_cached : int = neo4j_cb.prompt_tokens_cached
        self.neo4j_completion_tokens : int = neo4j_cb.completion_tokens
        self.neo4j_reasoning_tokens : int = neo4j_cb.reasoning_tokens
        self.neo4j_successful_requests : int = neo4j_cb.successful_requests
        self.neo4j_total_cost_usd : float = neo4j_cb.total_cost
        self.document_size : int = self._get_char_size(doc)
        self.start_azure : str = str(start_azure)
        self.end_azure : str = str(end_azure)
        self.azure_chunk_size : int = azure_chunk_size
        self.azure_chunk_overlap : int = azure_chunk_overlap
        self.start_neo4j : str = str(start_neo4j)
        self.end_neo4j : str = str(end_neo4j)
        self.number_nodes : int = number_nodes
        self.number_relationships : int = number_relationships
        self.neo4j_chunk_size : int = neo4j_chunk_size
        self.neo4j_chunk_overlap : int = neo4j_chunk_overlap
        self.start_chroma : str =  str(start_chroma)
        self.end_chroma : str = str(end_chroma)
        self.embedding_tokens : int = embedding_tokens
        self.chroma_chunk_size : int = chroma_chunk_size
        self.chroma_chunk_overlap : int = chroma_chunk_overlap


    def _get_char_size(self, doc : Document) -> int:
        return len(doc.page_content)

    def to_dict(self) -> dict:
        """
        Convert the DTO instance into a standard dictionary.
        """
        return self.__dict__.copy()