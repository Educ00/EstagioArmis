import json
from flask import current_app
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.constants import prompt_template, prompt_instructions1
from infrastructure.adapters.azure_adapter import AzureAdapter


class AzureService:
    def __init__(self, adapter: AzureAdapter):
        self.adapter = adapter
        
        
    def extract_entities_and_relations(self, file_name: str, save_to_file: bool = True):
        folder_name = current_app.config['UPLOAD_FOLDER']
        file_path = folder_name + "/" + file_name
        chunks = self._split_text(file_path=file_path, chunk_size=250, chunk_overlap=25)
        responses = []
        for chunk in chunks:
            responses.append(self.adapter.call_llm(prompt_template=prompt_template, instructions=prompt_instructions1, text= chunk))
        
        if save_to_file:
            with open(folder_name + "\\" + "resposta.txt", 'w', encoding='utf-8') as outp:  # Overwrites any existing file.
                json.dump(responses[-1], outp, indent=4, ensure_ascii=False)
        
        return responses[-1]
        


    def _split_text(self, file_path: str, chunk_size: int = 250, chunk_overlap: int = 50):
        loader = TextLoader(file_path)
        documents = loader.load()
    
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_documents(documents)
        return chunks