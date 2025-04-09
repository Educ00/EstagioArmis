import json
import os

from flask import current_app
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from neo4j.exceptions import CypherSyntaxError

from core.constants import prompt_template1, prompt_instructions1, prompt_instructions2, prompt_instructions3, \
    json_schema1, json_schema2, prompt_template2, instructions_correct_syntax, instructions_generate_cypher_query, \
    prompt_template3, instructions_format_answer_to_question, prompt_template0, instructions_group_results
from infrastructure.adapters.azure_adapter import AzureAdapter
from infrastructure.repositories.neo4j_repository import Neo4jRepository


class AzureService:    
    def __init__(self, azure_adapter: AzureAdapter, neo4j_repository: Neo4jRepository):
        self.azure_adapter = azure_adapter
        self.neo4j_repository = neo4j_repository
        
    def make_question(self, question):
        query, answer = self.generate_query_and_query(question)
        self.azure_adapter.create_new_llm(json_schema=json_schema2)
        print("Formatting Answer...")
        llm_response = self.azure_adapter.call_llm(prompt_template=prompt_template3, instructions=instructions_format_answer_to_question, question=question, answer=answer)
        return llm_response["response"], query, answer
        
    
    def generate_query_and_query(self, question, max_correction_attempts : int = 5):
        print("Generating query...")
        graph_schema = self.neo4j_repository.get_schema()
        self.azure_adapter.create_new_llm(json_schema=json_schema2)
        
        llm_response = self.azure_adapter.call_llm(prompt_template=prompt_template2, instructions=instructions_generate_cypher_query ,schema=graph_schema, question=question)
        graph_response = "Não foi possivel consultar a base de dados porque a query era inválida!"
        try:
            graph_response = self.neo4j_repository.run_query(llm_response["response"])
        except CypherSyntaxError:
            correction_attempt = 0
            while correction_attempt <= max_correction_attempts:
                print(f"Tentativa de correção #{correction_attempt+1}/{max_correction_attempts}")
                correction_attempt += 1
                llm_response = self.azure_adapter.call_llm(prompt_template=prompt_template2, instructions=instructions_correct_syntax, schema=graph_schema, question=question)
                try:
                    graph_response = self.neo4j_repository.run_query(llm_response["response"])
                    break
                except CypherSyntaxError:
                    print("Resposta errada de novo: " + llm_response["response"])
        return llm_response["response"],graph_response
        
        
    def extract_entities_and_relations(self, file_name: str, save_to_file: bool = True):
        self.azure_adapter.create_new_llm(json_schema=json_schema1)

        upload_folder_name = current_app.config['UPLOAD_FOLDER']
        output_folder_name = current_app.config['OUTPUT_FOLDER']
        file_path = upload_folder_name + "/" + file_name
        chunks = self._split_text(file_path=file_path, chunk_size=250, chunk_overlap=25)
        
        messages = [{"role": "system", "content": prompt_instructions3}]
        response = self.azure_adapter.call_llm(prompt_template=prompt_template0, instructions="Please follow everything.")
        response_str = json.dumps(response)
        messages.append({"role": "assistant", "content": response_str})

        responses = []
        for i, chunk in enumerate(chunks):
            print(f"   Chunk #{i+1}/{len(chunks)}...")
            messages.append({"role": "user", "content": f"Chunk Content #{i + 1}/{len(chunks)}: {chunk}"})

            response = self.azure_adapter.call_llm(prompt_template=prompt_template1, instructions=f"Process chunk {i + 1}",text=chunk)
            response_str = json.dumps(response)
            responses.append(response)
            messages.append({"role": "assistant", "content": response_str})

        final_response = self.azure_adapter.call_llm(prompt_template1, instructions=instructions_group_results, text=str(json.dumps(responses, indent=4,ensure_ascii=False)))
        print(f"   Saving to file: {output_folder_name + os.sep + "resposta.txt"}")
        if save_to_file:
            with open(output_folder_name + os.sep + "resposta.txt", 'w', encoding='utf-8') as outp:  # Apaga ficheiro existente.
                json.dump(final_response, outp, indent=4, ensure_ascii=False)
        
        return {"all": responses, "final": final_response}
            


    def _split_text(self, file_path: str, chunk_size: int = 600, chunk_overlap: int = 50):
        loader = TextLoader(file_path)
        documents = loader.load()
    
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_documents(documents)
        return chunks

