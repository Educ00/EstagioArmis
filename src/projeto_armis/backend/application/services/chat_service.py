from application.dtos.azure_ai_search_benchmark_dto import AzureAiSearchBenchmarkDTO
from application.dtos.chromadb_benchmark_dto import ChromaDBBenchmarkDTO
from application.dtos.neo4j_benchmark_dto import Neo4jBenchmarkDTO
from core.constants import json_schema2, prompt_template3, instructions_format_answer_to_question
from domain.models.benchmark import Benchmark
from infrastructure.adapters.azure_adapter import AzureAdapter
from infrastructure.repositories.azure_repository import AzureRepository
from infrastructure.repositories.neo4j_repository import Neo4jRepository


class ChatService:
    def __init__(self, neo4j_repository: Neo4jRepository, azure_repository: AzureRepository, azure_adapter: AzureAdapter):
        self.neo4j_repository = neo4j_repository
        self.azure_repository = azure_repository
        self.azure_adapter = azure_adapter

    def make_question(self, question: str, neo4j: bool = False, azure_ai_search: bool = False, chroma_db: bool = False, display_benchmark_info: bool = False) -> tuple[Neo4jBenchmarkDTO | None, AzureAiSearchBenchmarkDTO | None, ChromaDBBenchmarkDTO | None]:
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
