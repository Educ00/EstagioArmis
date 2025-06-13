import json
import os
from datetime import datetime

from flask import current_app
from langchain_community.callbacks import get_openai_callback
from langchain_community.document_loaders import TextLoader
from openai import embeddings

from application.dtos.entity_dto import EntityDTO
from application.dtos.index_benchmark_dto import IndexBenchmarkDto
from application.dtos.question_benchmark_dto import QuestionBenchmarkDto
from application.dtos.relationship_dto import RelationshipDTO
from application.services.azure_service import AzureService
from application.services.chroma_service import ChromaService
from application.services.neo4j_service import Neo4jService
from core.constants import prompt_template3, instructions_format_answer_to_question, json_schema2


class ChatService:
    def __init__(self, azure_service : AzureService, neo4j_service : Neo4jService, chroma_service : ChromaService):
        self.azure_service : AzureService = azure_service
        self.neo4j_service : Neo4jService = neo4j_service
        self.chroma_service : ChromaService = chroma_service
        
    def make_question(self, question : str, method: int):
        benchmark_folder = current_app.config["BENCHMARK_FOLDER"]
        question_folder = current_app.config["QUESTION_FOLDER"]
        
        question_file_filename = "question_method" + str(method) + "_" + question.replace(" ", "") + ".txt"
        benchmark_file_filename = "benchmark_" + question_file_filename

        # -------- azure ----------
        start_azure = datetime.now()
        with get_openai_callback() as azure_cb:
            response = self.azure_service.run_query(query=question)

            self.azure_service.change_schema(json_schema=json_schema2)
            azure_docs = []
            for doc in response:
                azure_docs.append(doc.page_content)
            llm_response = self.azure_service.call_llm(prompt_template=prompt_template3,instructions=instructions_format_answer_to_question, question=question, answer=azure_docs)

            azure_ai_search_response = llm_response["response"]
        end_azure = datetime.now()
        
        # ------- chroma ---------
        start_chroma = datetime.now()
        with get_openai_callback() as chroma_cb:
            response = self.chroma_service.run_query(query=question)
            chroma_docs = []
            for doc in response:
                chroma_docs.append(doc.page_content)
                llm_response = self.azure_service.call_llm(prompt_template=prompt_template3,instructions=instructions_format_answer_to_question, question=question, answer=chroma_docs)
            chroma_search_response = llm_response["response"]
        end_chroma = datetime.now()

    # -------- neo4j ----------
        start_neo4j : datetime = datetime.min
        end_neo4j : datetime = datetime.min
        neo4j_response = None
        match method:
            case 1:
                start_neo4j = datetime.now()
                with get_openai_callback() as neo4j_cb:
                    neo4j_query, neo4j_query_response = self.azure_service.generate_cypher_query_and_query_neo4j(question=question)
                    self.azure_service.change_schema(json_schema=json_schema2)
                    llm_response = self.azure_service.call_llm(prompt_template=prompt_template3, instructions=instructions_format_answer_to_question, question=question, answer=neo4j_query_response)
                end_neo4j = datetime.now()    
                neo4j_response = llm_response["response"]
                
            case 2:
                start_neo4j = datetime.now()
                # aqui recebe-se o callback porque senão não é possivel ver as coisas.
                response, neo4j_cb = self.neo4j_service.query_graph(question=question, allow_dangerous_requests=True, return_intermediate_steps=True, validate_cypher=True)
                end_neo4j = datetime.now()
                neo4j_query = response["intermediate_steps"][0]["query"]
                neo4j_query_response = response["intermediate_steps"][1]["context"]
                neo4j_response = response["result"]
        
        question_results = {
            "neo4j_response": neo4j_response,
            "azure_ai_search_response": azure_ai_search_response,
            "chroma_db_response": chroma_search_response
        }
        
        self.save_to_file(content=question_results, output_folder=question_folder, output_filename=question_file_filename)
        
        question_benchmark_dto = QuestionBenchmarkDto(
            method=method,
            completion_llm_name= self.azure_service.get_llm_base_name(),
            embeddings_llm_name= self.azure_service.get_embeddings_llm_name(),
            neo4j_cb=neo4j_cb,
            azure_cb=azure_cb,
            chroma_cb=chroma_cb,
            start_neo4j=start_neo4j,
            end_neo4j=end_neo4j,
            start_azure=start_azure,
            end_azure=end_azure,
            start_chroma=start_chroma,
            end_chroma=end_chroma
        )

        self.save_to_file(content=question_benchmark_dto.to_dict(), output_folder=benchmark_folder, output_filename=benchmark_file_filename)
                
        neo4j_tuple = (neo4j_query, neo4j_query_response, neo4j_response)
        azure_tuple = (azure_ai_search_response, azure_docs)
        chroma_tuple = (chroma_search_response, chroma_docs)
        
        return question_benchmark_dto, neo4j_tuple, azure_tuple, chroma_tuple
        
        
        
    
    def import_file(self, input_filename : str, chunk_size: int = 0, chunk_overlap: int = 0, split_azure_ai_search : bool = False, split_chroma : bool = False,split_neo4j : bool = False,method : int = 2):
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        extraction_folder = current_app.config["EXTRACTION_FOLDER"]
        benchmark_folder = current_app.config["BENCHMARK_FOLDER"]
        
        output_filepath = upload_folder + "/" + input_filename
        
        extraction_file_filename = "extraction_method" + str(method) + "_" + input_filename
        benchmark_file_filename = "benchmark_" + extraction_file_filename

        loader = TextLoader(output_filepath)
        docs = loader.load()
        
        # -------- azure ----------
        azure_chunk_size = chunk_size
        azure_chunk_overlap = chunk_overlap
        start_azure = datetime.now()
        if not split_azure_ai_search:
            azure_chunk_size = 999999999
            azure_chunk_overlap = 0
        azure_results = self.azure_service.import_documents_to_azure(documents=docs, chunk_size=azure_chunk_size, chunk_overlap=azure_chunk_overlap)
        end_azure = datetime.now()
        
        # -------- chroma ---------
        chroma_chunk_size = chunk_size
        chroma_chunk_overlap = chunk_overlap
        start_chroma = datetime.now()
        if not split_chroma:
            chroma_chunk_size = 999999999
            chroma_chunk_overlap = 0
        
        chroma_results, embedding_tokens = self.chroma_service.import_documents(documents=docs, chunk_size=chroma_chunk_size, chunk_overlap=chroma_chunk_overlap)
        end_chroma = datetime.now()
        
        # -------- neo4j ----------
        start_neo4j : datetime = datetime.min
        end_neo4j : datetime = datetime.min
        number_nodes : int = 0
        number_relationships : int = 0
        neo4j_chunk_size : int = chunk_size
        neo4j_chunk_overlap : int = chunk_overlap
        extraction_results : dict = {}
        
        if not split_neo4j:
            neo4j_chunk_size = 999999999
            neo4j_chunk_overlap = 0
        match method:
            case 1:
                start_neo4j = datetime.now()
                with get_openai_callback() as neo4j_cb:
                    extraction_results = self.azure_service.extract_entities_and_relations(documents=docs, chunk_size=neo4j_chunk_size, chunk_overlap=neo4j_chunk_overlap)
                entities, relationships = self.import_entities_and_relationships_to_neo4j(data=extraction_results)
                end_neo4j = datetime.now()
                number_nodes = len(entities)
                number_relationships = len(relationships)
            case 2:
                start_neo4j = datetime.now()
                with get_openai_callback() as neo4j_cb:
                    extraction_results = self.azure_service.extract_entities_and_relations2(documents=docs, chunk_size=neo4j_chunk_size, chunk_overlap=neo4j_chunk_overlap)
                entities, relationships = self.import_entities_and_relationships_to_neo4j(data=extraction_results)
                end_neo4j = datetime.now()
                number_nodes = len(entities)
                number_relationships = len(relationships)
        self.save_to_file(content=extraction_results, output_folder=extraction_folder, output_filename=extraction_file_filename)
                
        index_benchmark_dto = IndexBenchmarkDto(
            filename=input_filename,
            method=method,
            completion_llm_name= self.azure_service.get_llm_base_name(),
            embeddings_llm_name= self.azure_service.get_embeddings_llm_name(),
            neo4j_cb=neo4j_cb,
            doc=docs[0], 
            start_azure=start_azure, 
            end_azure=end_azure,
            azure_chunk_size=azure_chunk_size, 
            azure_chunk_overlap=azure_chunk_overlap,
            start_neo4j=start_neo4j, 
            end_neo4j=end_neo4j, 
            number_nodes=number_nodes,
            number_relationships=number_relationships,
            neo4j_chunk_size=neo4j_chunk_size,
            neo4j_chunk_overlap=neo4j_chunk_overlap,
            start_chroma=start_chroma,
            end_chroma=end_chroma,
            embedding_tokens=embedding_tokens,
            chroma_chunk_size=chroma_chunk_size,
            chroma_chunk_overlap=chroma_chunk_overlap
        )
        
        self.save_to_file(content=index_benchmark_dto.to_dict(), output_folder=benchmark_folder, output_filename=benchmark_file_filename)
        
        
        
        return index_benchmark_dto, azure_results, chroma_results, extraction_results
    
    
    def import_entities_and_relationships_to_neo4j(self, data : dict) -> tuple[list[EntityDTO], list[RelationshipDTO]]:
        nodes : list[EntityDTO] = []
        relationships : list[RelationshipDTO] = [] 
        for entity in data["entities"]:
            name = entity["name"]
            category = entity["category"]
            description = entity["description"]
            nodes.append(EntityDTO(name=name, category=category, description=description))
        for entity in data["relationships"]:
            source = entity["source"]
            target = entity["target"]
            value = entity["value"]
            relationships.append(RelationshipDTO(source=source, target=target, value=value))

        entities = self.neo4j_service.import_nodes(nodes=nodes)
        relationships = self.neo4j_service.import_relationships(relationships=relationships)
        return entities, relationships
        
        
    
    def save_to_file(self, content : dict, output_folder : str = None, output_filename : str = None):
        if output_folder:
            output_folder_final = output_folder
        else:
            output_folder_final = current_app.config["OUTPUT_FOLDER"]
        
        if output_filename:
            special_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
            for char in special_chars:
                output_filename = output_filename.replace(char, "")
            output_filepath = output_folder_final + os.sep + output_filename
        else:
            name = "output"
            output_filepath = output_folder_final + os.sep + name + datetime.now()
        print(f"[Azure Service]: Saving to file: {output_filepath}")
        
        with open(output_filepath, "w", encoding="utf-8") as outp:  # Apaga ficheiro existente.
            json.dump(content, outp, indent=4, ensure_ascii=False)