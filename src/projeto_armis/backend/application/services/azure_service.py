import json
import os
from datetime import datetime, timedelta

from flask import current_app
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from neo4j.exceptions import CypherSyntaxError

from application.dtos.response_dto import ResponseDTO
from core.constants import prompt_template1, prompt_instructions1, prompt_instructions2, prompt_instructions3, \
    json_schema1, json_schema2, prompt_template2, instructions_correct_syntax, instructions_generate_cypher_query, \
    prompt_template3, instructions_format_answer_to_question, prompt_template0, instructions_group_results
from domain.models.benchmark import Benchmark
from infrastructure.adapters.azure_adapter import AzureAdapter
from infrastructure.repositories.neo4j_repository import Neo4jRepository


class AzureService:    
    def __init__(self, azure_adapter: AzureAdapter, neo4j_repository: Neo4jRepository):
        self.azure_adapter = azure_adapter
        self.neo4j_repository = neo4j_repository
        
    def make_question(self, question, neo4j : bool = False, chromaDB : bool = False, azureAISearch: bool = False) :
        """
        Accepts a question and return an answer.
        :param neo4j: if True queries neo4j
        :param chromaDB: if True queries chromaDB
        :return: 
        :param question: question string
        :return: ResponseDTO
        """
        benchmark = Benchmark()
        # neo4j
        benchmark.start_benchmark(completion_model=self.azure_adapter.llm_base.deployment_name, embeddings_model="None")
        
        query, query_response, benchmark = self.generate_chyper_query_and_query_neo4j(question, benchmark=benchmark)
        
        self.azure_adapter.change_schema(json_schema=json_schema2)
        print("[Azure Service]: Formatting Answer...")
        llm_response, start, end = self.azure_adapter.call_llm(prompt_template=prompt_template3, instructions=instructions_format_answer_to_question, question=question, answer=query_response)
        benchmark.add_thinking_time("Formatting Answer", start=start, end=end)
        
        benchmark.end_benchmark()
        benchmark.display()
        return llm_response["response"], query, query_response
        
    
    def generate_chyper_query_and_query_neo4j(self, question: str, max_correction_attempts : int = 5, benchmark: Benchmark = None) -> (any, int, Benchmark):
        """
        Accepts a question, converts to a valid Chyper query and retreives the query result.
        :param benchmark: Benchmark object
        :param question: question to parse to Cypher
        :param max_correction_attempts: max number of correction attempts
        :return: Query results, graph result and Benchmark object
        """
        total_llm_thinking_time_ms = 0
        
        print("[Azure Service]: Generating query...")
        graph_schema = self.neo4j_repository.get_schema()
        self.azure_adapter.change_schema(json_schema=json_schema2)
        
        llm_response, start, end = self.azure_adapter.call_llm(prompt_template=prompt_template2, instructions=instructions_generate_cypher_query ,schema=graph_schema, question=question)
        
        if benchmark:
            time_ms = benchmark.add_thinking_time("Generate Graph Query", start=start, end=end)
            total_llm_thinking_time_ms += time_ms
        
        graph_response = "Não foi possivel consultar a base de dados porque a query era inválida!"
        
        try:            
            graph_response = self.neo4j_repository.run_query(llm_response["response"])
            
        except CypherSyntaxError:
            correction_attempt = 0
            while correction_attempt <= max_correction_attempts:
                print(f"[Azure Service]: Tentativa de correção #{correction_attempt+1}/{max_correction_attempts}")
                correction_attempt += 1
                llm_response, start, end = self.azure_adapter.call_llm(prompt_template=prompt_template2, instructions=instructions_correct_syntax, schema=graph_schema, question=question)
                if benchmark:
                    time_ms = benchmark.add_thinking_time(f"Correction of Cypher Syntax  {correction_attempt+1}", start=start, end=end)
                    total_llm_thinking_time_ms += time_ms
                try:
                    graph_response = self.neo4j_repository.run_query(llm_response["response"])
                    break
                except CypherSyntaxError:
                    print("[Azure Service]: Resposta errada de novo: " + llm_response["response"])
        
        return llm_response["response"],graph_response, benchmark
        
        
    def extract_entities_and_relations(self, file_name: str, save_to_file: bool = True):
        """
        Extracts entities and relationships from a file.
        :param file_name: name of the file
        :param save_to_file: if True, saves to resposta.txt in outputs folder
        :return: JSON with entities and relationships
        """
        self.azure_adapter.change_schema(json_schema=json_schema1)

        upload_folder_name = current_app.config['UPLOAD_FOLDER']
        output_folder_name = current_app.config['OUTPUT_FOLDER']
        file_path = upload_folder_name + "/" + file_name
        chunks = self._split_text(file_path=file_path, chunk_size=250, chunk_overlap=25)
        
        messages = [{"role": "system", "content": prompt_instructions3}]
        response, start, end = self.azure_adapter.call_llm(prompt_template=prompt_template0, instructions="Please follow everything.")
        response_str = json.dumps(response)
        messages.append({"role": "assistant", "content": response_str})

        responses = []
        for i, chunk in enumerate(chunks):
            print(f"   Chunk #{i+1}/{len(chunks)}...")
            messages.append({"role": "user", "content": f"Chunk Content #{i + 1}/{len(chunks)}: {chunk}"})

            response, start, end = self.azure_adapter.call_llm(prompt_template=prompt_template1, instructions=f"Process chunk {i + 1}",text=chunk)
            response_str = json.dumps(response)
            responses.append(response)
            messages.append({"role": "assistant", "content": response_str})

        final_response, start, end = self.azure_adapter.call_llm(prompt_template1, instructions=instructions_group_results, text=str(json.dumps(responses, indent=4,ensure_ascii=False)))
        print(f"[Azure Service]: Saving to file: {output_folder_name + os.sep + "resposta.txt"}")
        if save_to_file:
            with open(output_folder_name + os.sep + "resposta.txt", 'w', encoding='utf-8') as outp:  # Apaga ficheiro existente.
                json.dump(final_response, outp, indent=4, ensure_ascii=False)
        
        return {"all": responses, "final": final_response}
            


    def _split_text(self, file_path: str, chunk_size: int = 600, chunk_overlap: int = 50):
        """
        Splits a file in to designated chunks.
        :param file_path: path for the file
        :param chunk_size: size of the chunks
        :param chunk_overlap: overlap beetween the chunks
        :return: list of Document objects
        """
        loader = TextLoader(file_path)
        documents = loader.load()
    
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_documents(documents)
        return chunks

