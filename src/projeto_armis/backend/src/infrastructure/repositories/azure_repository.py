from datetime import datetime
from os import getenv


from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain_community.vectorstores import AzureSearch

from infrastructure.adapters.azure_adapter import AzureAdapter


class AzureRepository:
    vector_store : AzureSearch = None
    search_client : SearchClient = None
    def __init__(self, azure_adapter : AzureAdapter):
        self.azure_adapter : AzureAdapter = azure_adapter
        self.vector_store : AzureSearch = self.get_vector_store()
        self.search_client : SearchClient = self.get_search_client()

    def get_vector_store(self):
        print("[Azure Adapter]: Initializing Azure Search Instance...")
        if self.vector_store is None:
            self.vector_store = AzureSearch(
                azure_search_endpoint=getenv("AZURE_URL"),
                azure_search_key=getenv("AZURE_URL_KEY"),
                index_name=getenv("INDEX_NAME_1"),
                embedding_function=self.azure_adapter.llm_embeddings_base
            )
        print("[Azure Adapter]: Azure Search Instance Created.")
        return self.vector_store

    def get_search_client(self):
        print("[Azure Adapter]: Initializing Azure Search Client Instance...")
        if self.search_client is None:
            self.search_client = SearchClient(
                endpoint=getenv("AZURE_URL"),
                index_name=getenv("INDEX_NAME_1"),
                credential=AzureKeyCredential(getenv("AZURE_URL_KEY"))
            )
        print("[Azure Adapter]: Azure Search Client Instance Created.")

        return self.search_client

    def change_index(self, index: str):
        self.vector_store = AzureSearch(
            azure_search_endpoint=getenv("AZURE_URL"),
            azure_search_key=getenv("AZURE_URL_KEY"),
            index_name=index,
            embedding_function=self.azure_adapter.get_llm_embeddings_base()
        )
        self.search_client = SearchClient(
            endpoint=getenv("AZURE_URL"),
            index_name=index,
            credential=AzureKeyCredential(getenv("AZURE_URL_KEY"))
        )

    def run_query(self, query):
        print("[Azure Adapter]: Calling Azure Ai Search")
        response = self.vector_store.similarity_search(query, search_type="hybrid")
        print("[Azure Adapter]: Azure Ai Search Called")
        return response

    def import_documents(self, docs):
        return self.vector_store.add_documents(documents=docs)
    
    def get_embeddings_model_deployment_name(self):
        return self.azure_adapter.llm_embeddings_base.model
    
    def get_llm_base_name(self):
        return self.azure_adapter.llm_base.deployment_name