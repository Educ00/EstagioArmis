from infrastructure.adapters.chroma_adapter import ChromaAdapter


class ChromaRepository:
    def __init__(self, chroma_adapter : ChromaAdapter):
        self.chroma_adapter : ChromaAdapter = chroma_adapter
        
    def import_documents(self, docs):
        return self.chroma_adapter.import_documents(docs=docs)
        
    def run_query(self, query):
        return self.chroma_adapter.run_query(query=query)

    def clean_db(self):
        return self.chroma_adapter.clean_db()