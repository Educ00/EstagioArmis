import json

from flask import current_app
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from neo4j.exceptions import CypherSyntaxError

from application.dtos.entity_dto import EntityDTO
from application.dtos.relationship_dto import RelationshipDTO
from application.mappers.entity_mapper import EntityMapper
from application.mappers.relationship_mapper import RelationshipMapper
from core.constants import prompt_template1, prompt_instructions1, prompt_instructions2, prompt_instructions3, \
    json_schema1, json_schema2, prompt_template2, instructions_correct_syntax, instructions_generate_cypher_query, \
    prompt_template3, instructions_format_answer_to_question, prompt_template0, instructions_group_results, \
    prompt_instructions4
from domain.models.graph_agent import GraphAgent
from infrastructure.adapters.azure_adapter import AzureAdapter
from infrastructure.repositories.azure_repository import AzureRepository
from infrastructure.repositories.neo4j_repository import Neo4jRepository


class AzureService:    
    def __init__(self, azure_adapter: AzureAdapter, azure_repository: AzureRepository, neo4j_repository: Neo4jRepository):
        self.azure_adapter = azure_adapter
        self.azure_repository = azure_repository
        self.neo4j_repository = neo4j_repository


    def generate_chyper_query_and_query_neo4j(self, question: str, max_correction_attempts : int = 5):
        """
        Accepts a question, converts to a valid Chyper query and retreives the query result.
        :param question: question to parse to Cypher
        :param max_correction_attempts: max number of correction attempts
        :return: Query results, graph result and Benchmark object
        """
        
        print("[Azure Service]: Generating query...")
        graph_schema = self.neo4j_repository.get_schema()
        self.azure_adapter.change_schema(json_schema=json_schema2)
        
        llm_response = self.azure_adapter.call_llm(prompt_template=prompt_template2, instructions=instructions_generate_cypher_query ,schema=graph_schema, question=question)
        
        graph_response = "Não foi possivel consultar a base de dados porque a query era inválida!"
        
        try:            
            graph_response = self.neo4j_repository.run_query(llm_response["response"])
            
        except CypherSyntaxError:
            correction_attempt = 0
            while correction_attempt <= max_correction_attempts:
                print(f"[Azure Service]: Tentativa de correção #{correction_attempt+1}/{max_correction_attempts}")
                correction_attempt += 1
                llm_response = self.azure_adapter.call_llm(prompt_template=prompt_template2, instructions=instructions_correct_syntax, schema=graph_schema, question=question)
                try:
                    graph_response = self.neo4j_repository.run_query(llm_response["response"])
                    break
                except CypherSyntaxError:
                    print("[Azure Service]: Resposta errada de novo: " + llm_response["response"])
        
        return llm_response["response"],graph_response
        
    def extract_entities_and_relations(self, documents : list[Document], chunk_size: int = 0, chunk_overlap : int = 0):
        """
        Extracts entities and relationships from a file in a single pass.
        :param documents: documents to extract
        :param chunk_size: chunk size
        :param chunk_overlap: overlapping size of chunks
        :return: JSON with entities and relationships
        """
        self.azure_adapter.change_schema(json_schema=json_schema1)

        chunks = self._split_text(documents=documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        messages = [{"role": "system", "content": prompt_instructions4}]
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
        
        return final_response

    def extract_entities_and_relations2(self, documents : list[Document], chunk_size : int = 0, chunk_overlap : int = 0):
        """
        Extracts entities and relationships from a text file using an Agent.
        The agent first extracts the entities and only then extracts relationships between them.
        :param documents: list of documents to import
        :param chunk_size : chunk size
        :param chunk_overlap : overlap between chunks
        :return: JSON with entities and relationships
        """
        
        chunks = self._split_text(documents=documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        llm = self.azure_adapter.get_llm_base()
        agent = GraphAgent(llm=llm)

        all_entities : list[EntityDTO]= []
        all_relations : list[RelationshipDTO] = []
        for i, chunk in enumerate(chunks, start=1):
            print(f"[Azure Service] Processing Chunk: {i}/{len(chunks)}")
            #print(f"[Azure Service] {chunk.page_content}")
            schema_result = agent.extract_from_chunk(chunk=chunk.page_content)
            all_entities.extend(EntityMapper.to_dto(EntityMapper.to_domain(schema_result.entities)))
            all_relations.extend(RelationshipMapper.to_dto(RelationshipMapper.to_domain(schema_result.relations)))
        
        results = {
            "entities": [
                {
                    "name": e.name, 
                    "category": e.category, 
                    "description": e.description
                } 
                for e in all_entities
            ],
            "relationships": [
                {
                    "source": r.source, 
                    "target": r.target, 
                    "value": r.value
                }
                for r in all_relations
            ]
        }

        return results

    def import_documents_to_azure(self, documents, chunk_size : int = 0, chunk_overlap : int = 0):
        print(f"[Azure Service]: Importing to estagio-eduardocarreiro-teste1...")
        self.azure_repository.change_index("estagio-eduardocarreiro-teste1")
        chunks = self._split_text(documents=documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        imported_docs = self.azure_repository.import_documents(chunks)
        return imported_docs

    def get_llm_base_name(self):
        return self.azure_repository.get_llm_base_name()

    def get_embeddings_llm_name(self):
        return self.azure_repository.get_embeddings_model_deployment_name()

    def call_llm(self,prompt_template: str, **kwargs):
        return self.azure_adapter.call_llm(prompt_template=prompt_template, **kwargs)

    def run_query(self, query: str):
        return self.azure_repository.run_query(query=query)

    def change_schema(self, json_schema):
        return self.azure_adapter.change_schema(json_schema=json_schema)

    def clear_azure_index(self) -> int:
        print("[Azure Service]: Cleaning estagio-eduardocarreiro-teste1...")
        self.azure_repository.change_index("estagio-eduardocarreiro-teste1")
        deleted_count = 0
        while True:
            results = list(self.azure_repository.search_client.search(search_text="*", top=1000))
            if not results:
                break
            documents_to_delete = [{"@search.action": "delete", "id": doc["id"]} for doc in results]
            self.azure_repository.search_client.upload_documents(documents=documents_to_delete)
            deleted_count += len(documents_to_delete)
        print(deleted_count)
        return deleted_count

    def clear_azure_index2(self) -> int:
        print("[Azure Service]: Cleaning estagio-eduardocarreiro-teste2...")
        self.azure_repository.change_index("estagio-eduardocarreiro-teste2")
        deleted_count = 0
        while True:
            results = list(self.azure_repository.search_client.search(search_text="*", top=1000))
            if not results:
                break
            documents_to_delete = [{"@search.action": "delete", "id": doc["id"]} for doc in results]
            self.azure_repository.search_client.upload_documents(documents=documents_to_delete)
            deleted_count += len(documents_to_delete)
        print(deleted_count)
        return deleted_count
        
    
    def print_azure_index(self):
        self.azure_repository.change_index("estagio-eduardocarreiro-teste1")
        results = self.azure_repository.search_client.search(search_text="*")
        for doc in results:
            print(doc)
        #return results

    def print_azure_index2(self):
        self.azure_repository.change_index("estagio-eduardocarreiro-teste2")
        results = self.azure_repository.search_client.search(search_text="*")
        for doc in results:
            print(doc)
        #return results

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

    def extract_entities_and_relations_from_filename(self, input_filename : str , chunk_size: int = 0, chunk_overlap : int = 0, method : int = 2):
        """
        Extracts entities and relationships from filename of a file already imported
        :param input_filename: filename of the file
        :param chunk_size: chunk size
        :param chunk_overlap: overlap of the chunks
        :param method: 1 or 2
        :return: extraction results
        """
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        output_filepath = upload_folder + "/" + input_filename

        loader = TextLoader(output_filepath)
        docs = loader.load()
        extraction_results : dict = {}
        match method:
            case 1:
                extraction_results = self.extract_entities_and_relations(documents=docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            case 2:
                extraction_results = self.extract_entities_and_relations2(documents=docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        return extraction_results