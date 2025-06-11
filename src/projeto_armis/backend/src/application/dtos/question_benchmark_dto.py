from datetime import datetime

from langchain_community.callbacks import OpenAICallbackHandler


class QuestionBenchmarkDto :
    def __init__(self, method: int, completion_llm_name: str, embeddings_llm_name: str, neo4j_cb : OpenAICallbackHandler, azure_cb : OpenAICallbackHandler, start_azure : datetime, end_azure: datetime, start_neo4j : datetime, end_neo4j: datetime):
        self.method : int = method
        self.completion_llm_name : str = completion_llm_name
        self.embeddings_llm_name : str = embeddings_llm_name
        self.neo4j_prompt_tokens : int = neo4j_cb.prompt_tokens
        self.neo4j_prompt_tokens_cached : int = neo4j_cb.prompt_tokens_cached
        self.neo4j_completion_tokens : int = neo4j_cb.completion_tokens
        self.neo4j_reasoning_tokens : int = neo4j_cb.reasoning_tokens
        self.neo4j_successful_requests : int = neo4j_cb.successful_requests
        self.neo4j_total_cost_usd : float = neo4j_cb.total_cost
        self.azure_prompt_tokens : int = azure_cb.prompt_tokens
        self.azure_prompt_tokens_cached : int = azure_cb.prompt_tokens_cached
        self.azure_completion_tokens : int = azure_cb.completion_tokens
        self.azure_reasoning_tokens : int = azure_cb.reasoning_tokens
        self.azure_successful_requests : int = azure_cb.successful_requests
        self.azure_total_cost_usd : float = azure_cb.total_cost
        self.start_azure : str = str(start_azure)
        self.end_azure : str = str(end_azure)
        self.start_neo4j : str = str(start_neo4j)
        self.end_neo4j : str = str(end_neo4j)


    def to_dict(self) -> dict:
        """
        Convert the DTO instance into a standard dictionary.
        """
        return self.__dict__.copy()