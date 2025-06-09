import json
import os

from flask import current_app
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from neo4j.exceptions import CypherSyntaxError

from application.dtos.azure_ai_search_benchmark_dto import AzureAiSearchBenchmarkDTO
from application.dtos.chromadb_benchmark_dto import ChromaDBBenchmarkDTO
from application.dtos.entity_dto import EntityDTO
from application.dtos.neo4j_benchmark_dto import Neo4jBenchmarkDTO
from application.dtos.relationship_dto import RelationshipDTO
from application.mappers.entity_mapper import EntityMapper
from application.mappers.relationship_mapper import RelationshipMapper
from core.constants import prompt_template1, prompt_instructions1, prompt_instructions2, prompt_instructions3, \
    json_schema1, json_schema2, prompt_template2, instructions_correct_syntax, instructions_generate_cypher_query, \
    prompt_template3, instructions_format_answer_to_question, prompt_template0, instructions_group_results, \
    prompt_instructions4
from domain.models.benchmark import Benchmark
from domain.models.entity import Entity
from domain.models.graph_agent import GraphAgent
from domain.models.relationship import Relationship
from infrastructure.adapters.azure_adapter import AzureAdapter
from infrastructure.repositories.azure_repository import AzureRepository
from infrastructure.repositories.neo4j_repository import Neo4jRepository


class AzureService:    
    def __init__(self, azure_adapter: AzureAdapter, azure_repository: AzureRepository, neo4j_repository: Neo4jRepository):
        self.azure_adapter = azure_adapter
        self.azure_repository = azure_repository
        self.neo4j_repository = neo4j_repository
        
    def make_question(self, question, neo4j : bool = False, azure_ai_search: bool = False, chroma_db : bool = False, display_benchmark_info: bool = False) -> tuple[Neo4jBenchmarkDTO | None, AzureAiSearchBenchmarkDTO | None, ChromaDBBenchmarkDTO | None]:
        """
        Accepts a question and returns the answer from Neo4j, Azure Ai Search and ChromaDB and some metrics in the form of Benchmark objects.
        :param question: question string
        :param neo4j: if True queries neo4j
        :param chroma_db: if True queries chromaDB
        :param azure_ai_search: if True queries Azure Ai Search
        :param display_benchmark_info: if true displays benchmark info of the operations
        :return: Neo4j Benchmark Object, Azure Ai Search Benchmark Object, ChromaDb Benchmark Object
        """
        
        neo4j_benchmark : Benchmark | None = None
        neo4j_benchmark_dto : Neo4jBenchmarkDTO | None = None
        
        azure_ai_search_benchmark : Benchmark | None = None
        azure_ai_search_benchmark_dto : AzureAiSearchBenchmarkDTO | None = None
        
        chroma_db_benchmark : Benchmark | None = None
        chroma_db_benchmark_dto : ChromaDBBenchmarkDTO | None = None
            
        if neo4j:
            neo4j_benchmark = Benchmark("neo4j method 1")
            neo4j_benchmark.start_benchmark(completion_model=self.azure_repository.get_llm_base_name(), embeddings_model="None")
            
            print("[Azure Service] A usar Neo4j:")
            neo4j_query, neo4j_query_response, neo4j_benchmark = self.generate_chyper_query_and_query_neo4j(question=question, benchmark=neo4j_benchmark)
            
            self.azure_adapter.change_schema(json_schema=json_schema2)
            print("[Azure Service]: Formatting Answer...")
            llm_response, start, end, cb = self.azure_adapter.call_llm(prompt_template=prompt_template3, instructions=instructions_format_answer_to_question, question=question, answer=neo4j_query_response)
            neo4j_response = llm_response["response"]
            neo4j_benchmark.add_thinking_time(operation_name="Formatting Answer", start=start, end=end)
            neo4j_benchmark.process_callback(operation_name="Formatting Answer", callback=cb)
            neo4j_benchmark.end_benchmark()
            neo4j_benchmark_dto = Neo4jBenchmarkDTO(neo4j_response=neo4j_response, neo4j_query=neo4j_query, neo4j_query_response=neo4j_query_response)
            print("[Azure Service] Acabou com Neo4j.")
        
        if azure_ai_search:
            print("[Azure Service] A usar Azure Ai Search:")
            azure_ai_search_benchmark = Benchmark(name="Azure Ai Search neo4j method 1")
            azure_ai_search_benchmark.start_benchmark(completion_model=self.azure_repository.get_llm_base_name(), embeddings_model=self.azure_repository.get_embeddings_model_deployment_name())
            azure_ai_search_response, start, end = self.azure_repository.run_query(query=question)
            docs = []
            for doc in azure_ai_search_response:
                docs.append(doc.page_content)
            self.azure_adapter.change_schema(json_schema=json_schema2)
            print("[Azure Service]: Formatting Answer...")
            llm_response, start, end, cb = self.azure_adapter.call_llm(prompt_template=prompt_template3,instructions=instructions_format_answer_to_question, question=question, answer=docs)
            azure_ai_search_response = llm_response["response"]
            azure_ai_search_benchmark.add_thinking_time("Formatting Answer", start=start, end=end)
            azure_ai_search_benchmark.process_callback("Formatting Answer", callback=cb)
            azure_ai_search_benchmark.end_benchmark()
            azure_ai_search_benchmark_dto = AzureAiSearchBenchmarkDTO(response=azure_ai_search_response, docs=docs)
            print("[Azure Service] Acabou Azure Ai Search")
            
        if chroma_db:
            print("[Azure Service] A usar Chroma DB:")
            chroma_db_benchmark = Benchmark(name="Chroma DB")
            
            print("[Azure Service] Acabou Chroma DB")
            
        
        if display_benchmark_info:
            if neo4j_benchmark:
                neo4j_benchmark.display()
            if azure_ai_search_benchmark:
                azure_ai_search_benchmark.display()
            if chroma_db_benchmark:
                chroma_db_benchmark.display()
                
        return neo4j_benchmark_dto, azure_ai_search_benchmark_dto, chroma_db_benchmark_dto

    def make_question2(self, question: str, neo4j: bool = False, azure_ai_search: bool = False, chroma_db: bool = False, display_benchmark_info: bool = False) -> tuple[Neo4jBenchmarkDTO | None, AzureAiSearchBenchmarkDTO | None, ChromaDBBenchmarkDTO | None]:
        """
        Accepts a question and returns the answer from Neo4j, Azure Ai Search and Chroma DB using langchain.
        :param question: 
        :param neo4j: 
        :param azure_ai_search: 
        :param chroma_db: 
        :param display_benchmark_info: 
        :return: 
        """
        neo4j_benchmark : Benchmark | None = None
        neo4j_benchmark_dto : Neo4jBenchmarkDTO | None = None

        azure_ai_search_benchmark : Benchmark | None = None
        azure_ai_search_benchmark_dto : AzureAiSearchBenchmarkDTO | None = None

        chroma_db_benchmark : Benchmark | None = None
        chroma_db_benchmark_dto : ChromaDBBenchmarkDTO | None = None

        if neo4j:
            neo4j_benchmark = Benchmark("neo4j neo4j method 2")
            print("[Azure Service] A usar Neo4j pela Langchain:")

            neo4j_benchmark.start_benchmark(completion_model=self.azure_adapter.llm_base.deployment_name, embeddings_model="None")
            response, start, end, cb = self.neo4j_repository.query_graph(
                question=question,
                llm= self.azure_adapter.get_llm_base(),
                allow_dangerous_requests=True,
                return_intermediate_steps=True,
                validate_cypher=True
            )

            print("[Azure Service] Acabou Neo4j pela Langchain.")
            neo4j_benchmark.add_thinking_time(operation_name="Processing - THIS INCLUDES LLM THINKING TIME...", start=start, end=end)
            neo4j_benchmark.process_callback(operation_name="Processing - THIS INCLUDES LLM THINKING TIME...", callback=cb)
            neo4j_benchmark.end_benchmark()
            neo4j_response = response["result"]
            neo4j_query = response["intermediate_steps"][0]["query"]
            neo4j_query_response = response["intermediate_steps"][1]["context"]
            neo4j_benchmark_dto = Neo4jBenchmarkDTO(neo4j_response=neo4j_response, neo4j_query=neo4j_query, neo4j_query_response=neo4j_query_response)

        if azure_ai_search:
            print("[Azure Service] A usar Azure Ai Search:")
            azure_ai_search_benchmark = Benchmark(name="Azure Ai Search neo4j method 1")
            azure_ai_search_benchmark.start_benchmark(completion_model=self.azure_adapter.llm_base.deployment_name, embeddings_model=self.azure_adapter.llm_embeddings_base.model)
            azure_ai_search_response, start, end = self.azure_repository.run_query(query=question)
            docs = []
            for doc in azure_ai_search_response:
                docs.append(doc.page_content)
            self.azure_adapter.change_schema(json_schema=json_schema2)
            print("[Azure Service]: Formatting Answer...")
            llm_response, start, end, cb = self.azure_adapter.call_llm(prompt_template=prompt_template3,instructions=instructions_format_answer_to_question, question=question, answer=docs)
            azure_ai_search_response = llm_response["response"]
            azure_ai_search_benchmark.add_thinking_time("Formatting Answer", start=start, end=end)
            azure_ai_search_benchmark.process_callback("Formatting Answer", callback=cb)
            azure_ai_search_benchmark.end_benchmark()
            azure_ai_search_benchmark_dto = AzureAiSearchBenchmarkDTO(response=azure_ai_search_response, docs=docs)
            print("[Azure Service] Acabou Azure Ai Search")

        if chroma_db:
            print("[Azure Service] A usar Chroma DB:")
            chroma_db_benchmark = Benchmark(name="Chroma DB")

            print("[Azure Service] Acabou Chroma DB")


        if display_benchmark_info:
            if neo4j_benchmark:
                neo4j_benchmark.display()
            if azure_ai_search_benchmark:
                azure_ai_search_benchmark.display()
            if chroma_db_benchmark:
                chroma_db_benchmark.display()
        return neo4j_benchmark_dto, azure_ai_search_benchmark_dto, chroma_db_benchmark_dto


    def generate_chyper_query_and_query_neo4j(self, question: str, benchmark: Benchmark, max_correction_attempts : int = 5) -> (any, int, Benchmark):
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
        
        llm_response, start, end, cb = self.azure_adapter.call_llm(prompt_template=prompt_template2, instructions=instructions_generate_cypher_query ,schema=graph_schema, question=question)
        time_ms = benchmark.add_thinking_time("Generate Graph Query", start=start, end=end)
        total_llm_thinking_time_ms += time_ms
        benchmark.process_callback(operation_name="Generate Graph Query", callback=cb)
        
        graph_response = "Não foi possivel consultar a base de dados porque a query era inválida!"
        
        try:            
            graph_response = self.neo4j_repository.run_query(llm_response["response"])
            
        except CypherSyntaxError:
            correction_attempt = 0
            while correction_attempt <= max_correction_attempts:
                print(f"[Azure Service]: Tentativa de correção #{correction_attempt+1}/{max_correction_attempts}")
                correction_attempt += 1
                llm_response, start, end, cb = self.azure_adapter.call_llm(prompt_template=prompt_template2, instructions=instructions_correct_syntax, schema=graph_schema, question=question)
                time_ms = benchmark.add_thinking_time(operation_name=f"Correction of Cypher Syntax  {correction_attempt+1}", start=start, end=end)
                total_llm_thinking_time_ms += time_ms
                benchmark.process_callback(operation_name=f"Correction of Cypher Syntax  {correction_attempt+1}", callback=cb)
                try:
                    graph_response = self.neo4j_repository.run_query(llm_response["response"])
                    break
                except CypherSyntaxError:
                    print("[Azure Service]: Resposta errada de novo: " + llm_response["response"])
        
        return llm_response["response"],graph_response, benchmark
        
        
    def extract_entities_and_relations(self, filename: str, save_to_file: bool = True, output_filename: str = None):
        """
        Extracts entities and relationships from a file in a single pass.
        :param filename: name of the file
        :param save_to_file: if True, saves to a file in outputs folder
        :param output_filename: if it's None the output filename will be resposta.txt
        :return: JSON with entities and relationships
        """
        self.azure_adapter.change_schema(json_schema=json_schema1)

        upload_folder_name = current_app.config['UPLOAD_FOLDER']
        output_folder_name = current_app.config['OUTPUT_FOLDER']
        filename = upload_folder_name + "/" + filename
        chunks = self._split_text(filepath=filename, chunk_size=250, chunk_overlap=50)
        
        messages = [{"role": "system", "content": prompt_instructions4}]
        response, start, end, cb = self.azure_adapter.call_llm(prompt_template=prompt_template0, instructions="Please follow everything.")
        response_str = json.dumps(response)
        messages.append({"role": "assistant", "content": response_str})

        responses = []
        for i, chunk in enumerate(chunks):
            print(f"   Chunk #{i+1}/{len(chunks)}...")
            messages.append({"role": "user", "content": f"Chunk Content #{i + 1}/{len(chunks)}: {chunk}"})

            response, start, end, cb = self.azure_adapter.call_llm(prompt_template=prompt_template1, instructions=f"Process chunk {i + 1}",text=chunk)
            response_str = json.dumps(response)
            responses.append(response)
            messages.append({"role": "assistant", "content": response_str})

        final_response, start, end, cb = self.azure_adapter.call_llm(prompt_template1, instructions=instructions_group_results, text=str(json.dumps(responses, indent=4,ensure_ascii=False)))
        
        if output_filename:
            output_filepath = output_folder_name + os.sep + output_filename
        else:
            output_filepath = output_folder_name + os.sep + "resposta.txt"
            
        print(f"[Azure Service]: Saving to file: {output_filepath}")
        if save_to_file:
            with open(output_filepath, 'w', encoding='utf-8') as outp:  # Apaga ficheiro existente.
                json.dump(final_response, outp, indent=4, ensure_ascii=False)
        
        return {"all": responses, "final": final_response}

    def extract_entities_and_relations2(self, filename: str, save_to_file: bool = True, output_filename: str = None):
        """
        Extracts entities and relationships from a text file using an Agent.
        The agent first extracts the entities and only then extracts relationships between them.
        :param filename: name of the file
        :param save_to_file: if True, saves to a file in outputs folder
        :param output_filename: if it's None the output filename will be resposta.txt
        :return: JSON with entities and relationships
        """
        upload_folder_name = current_app.config['UPLOAD_FOLDER']
        output_folder_name = current_app.config['OUTPUT_FOLDER']
        filename = upload_folder_name + "/" + filename
        chunks = self._split_text(filepath=filename, chunk_size=1200, chunk_overlap=250)
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

        if output_filename:
            output_filepath = output_folder_name + os.sep + output_filename
        else:
            output_filepath = output_folder_name + os.sep + "resposta.txt"

        print(f"[Azure Service]: Saving to file: {output_filepath}")
        if save_to_file:
            with open(output_filepath, 'w', encoding='utf-8') as outp:  # Apaga ficheiro existente.
                json.dump(results, outp, indent=4, ensure_ascii=False)

        return {"all": results}

    def import_file(self, filename):
        upload_folder_name = current_app.config['UPLOAD_FOLDER']
        filepath = upload_folder_name + "/" + filename
        print(f"[Azure Service]: Importing {filepath} to estagio-eduardocarreiro-teste1...")
        loader = TextLoader(filepath)
        doc = loader.load()
        #docs = self._split_text(filepath=filepath)
        self.azure_repository.change_index("estagio-eduardocarreiro-teste1")
        imported_docs = self.azure_repository.import_documents(doc)
        return imported_docs
            

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

    def _split_text(self, filepath: str, chunk_size: int = 600, chunk_overlap: int = 50):
        """
        Splits a file in to designated chunks.
        :param filepath: path for the file
        :param chunk_size: size of the chunks
        :param chunk_overlap: overlap beetween the chunks
        :return: list of Document objects
        """
        loader = TextLoader(filepath)
        documents = loader.load()
    
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_documents(documents)
        return chunks

