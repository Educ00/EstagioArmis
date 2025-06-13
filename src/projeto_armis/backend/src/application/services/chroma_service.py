from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from infrastructure.repositories.chroma_repository import ChromaRepository


class ChromaService:
    def __init__(self, chroma_repository : ChromaRepository):
        self.chroma_repository : ChromaRepository = chroma_repository

    def import_documents(self, documents, chunk_size, chunk_overlap):
        chunks = self._split_text(documents=documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        imported_docs, tokens = self.chroma_repository.import_documents(chunks)
        return imported_docs, tokens

    def run_query(self, query):
        return self.chroma_repository.run_query(query=query)



    def _split_text(self, documents : list[Document], chunk_size: int = 600, chunk_overlap: int = 50):
        """
        Splits a file in to designated chunks.
        :param documents: documents to split
        :param chunk_size: size of the chunks
        :param chunk_overlap: overlap beetween the chunks
        :return: list of Document objects
        """

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_documents(documents)
        return chunks

    def clean_db(self):
        return self.chroma_repository.clean_db()
        
        
        
        