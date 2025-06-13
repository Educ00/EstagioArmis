import datetime

from dependency_injector.wiring import inject, Provide

from application.dtos.response_dto import ResponseDTO
from application.services.azure_service import AzureService
from application.services.chat_service import ChatService
from application.services.chroma_service import ChromaService
from application.services.neo4j_service import Neo4jService

from dependency_container import DependencyContainer

from flask import Blueprint, jsonify, request, make_response

chat_blueprint = Blueprint("Chat", __name__, url_prefix="/chat")

class ChatController:
    
    @chat_blueprint.route("/make-question", methods=["GET"])
    @staticmethod
    @inject
    def make_question(chat_service : ChatService = Provide[DependencyContainer.chat_service]):
        try:
            question = request.args.get("question")
            if not question:
                return jsonify({"error": "Pergunta não incluída", "exemplo": f"{request.path}?question=minhapergunta"})
            method = int(request.args.get("method"))
            if not method:
                method = 2
                print("[Chat Controller] Método definido por definição para <2>. usar method=<number> para definir.")
            question_benchmark_dto, neo4j_tuple, azure_tuple, chroma_tuple = chat_service.make_question(question=question, method=method)
               
            response_dto = ResponseDTO(
                neo4j_query=neo4j_tuple[0], 
                neo4j_query_response=neo4j_tuple[1],
                neo4j_response=neo4j_tuple[2], 
                azure_ai_search_response=azure_tuple[0],
                azure_ai_search_docs = azure_tuple[1],
                chroma_response=chroma_tuple[0],
                chroma_docs=chroma_tuple[1]
            )
            return make_response(response_dto.to_dict(), 200)
        except Exception as e:
            return jsonify(str(e)), 400
        
    @chat_blueprint.route("/import-file", methods=["GET"])
    @staticmethod
    @inject
    def import_file(chat_service : ChatService = Provide[DependencyContainer.chat_service], azure_service: AzureService = Provide[DependencyContainer.azure_service], neo4j_service : Neo4jService = Provide[DependencyContainer.neo4j_service], chroma_service : ChromaService = Provide[DependencyContainer.chroma_service]):
        clear = True
        
        try:
            filename = request.args.get("filename")
            if not filename:
                return {"error": "Nome do ficheiro não incluído", "exemplo": f"{request.path}?filename=meuficheiro.txt"}, 400
    
            method = int(request.args.get("method"))
            if not method:
                method = 2
                print("[Chat Controller] Método definido por definição para <2>. usar method=<number> para definir.")

            if clear:
                azure_service.clear_azure_index()
                #azure_service.clear_azure_index2()
                neo4j_service.clean_db()
                chroma_service.clean_db()
                
            index_benchmark_dto, azure_results, chroma_results, extraction_results = chat_service.import_file(input_filename=filename, chunk_size=500, chunk_overlap = 250, split_azure_ai_search=True, split_neo4j=True, split_chroma=True ,method=method)
            
            response_dto = ResponseDTO(
                document_size=index_benchmark_dto.document_size,
                start_azure=index_benchmark_dto.start_azure,
                end_azure=index_benchmark_dto.end_azure,
                azure_chunk_size=index_benchmark_dto.azure_chunk_size,
                azure_chunk_overlap=index_benchmark_dto.azure_chunk_overlap,
                start_neo4j=index_benchmark_dto.start_neo4j,
                end_neo4j=index_benchmark_dto.end_neo4j,
                number_nodes=index_benchmark_dto.number_nodes,
                number_relationships=index_benchmark_dto.number_relationships,
                neo4j_chunk_size=index_benchmark_dto.neo4j_chunk_size,
                neo4j_chunk_overlap=index_benchmark_dto.neo4j_chunk_overlap,
                azure_results = azure_results,
                extraction_results = extraction_results,
                chroma_results = chroma_results,
                embedding_tokens=index_benchmark_dto.embedding_tokens
            )
            
            return make_response(response_dto.to_dict(), 200)
            
        except Exception as e:
            return jsonify(str(e)), 400