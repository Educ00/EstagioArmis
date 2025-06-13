import os

import tiktoken
from flask import current_app

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings

from core.constants import modeloAda


class ChromaAdapter:
    embeddings : AzureOpenAIEmbeddings = None
    db : Chroma = None
    token_encoder = None
    
    def __init__(self):
        self.embeddings : AzureOpenAIEmbeddings = self.get_embeddings_llm()
        self.db = self.init_chroma()
        self.token_encoder = tiktoken.encoding_for_model(model_name=modeloAda)

    def get_embeddings_llm(self):
        if not self.embeddings:
            print("[Chroma Adapter]: Initializing LLM Embeddings instance...")
            self.embeddings = AzureOpenAIEmbeddings(
                model = modeloAda,
                azure_endpoint= os.getenv("MODELS_ENDPOINT"),
                api_key= os.getenv("MODELS_ENDPOINT_KEY")
            )
        return self.embeddings

    def init_chroma(self):
        if not self.db:
            print("[Chroma Adapter]: ChromaDB instance...")
            self.db = Chroma(
                persist_directory = current_app.config["CHROMADB"],
                embedding_function= self.get_embeddings_llm()
            )
        return self.db

    def run_query(self, query):
        return self.db.similarity_search(query=query)

    def import_documents(self, docs : list[Document]):
        tokens = 0
        for doc in docs:
            tokens += len(self.token_encoder.encode(doc.page_content))
        return self.db.add_documents(documents=docs), tokens

    def clean_db(self):
        docs = self.db.get()
        ids = docs["ids"]
        if ids:
            self.db.delete(docs["ids"])
        else:
            print("CHROMA VAZIA")