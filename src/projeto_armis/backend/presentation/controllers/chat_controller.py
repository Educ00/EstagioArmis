from dependency_injector.wiring import inject, Provide

from application.dtos.response_dto import ResponseDTO
from application.services.azure_service import AzureService

from dependency_container import DependencyContainer

from flask import Blueprint, jsonify, request, make_response

chat_blueprint = Blueprint("Chat", __name__, url_prefix="/chat")

@chat_blueprint.route("/make-question", methods=["GET"])
@inject
def make_question(azure_service: AzureService = Provide[DependencyContainer.azure_service]):
    try:
        question = request.args.get("question")
        if not question:
            return jsonify({"error": "Pergunta não incluída", "exemplo": f"{request.path}?question=minhapergunta"})
        
        neo4j_benchmark_dto, azure_ai_search_benchmark_dto, aa = azure_service.make_question(question, neo4j=True, azure_ai_search=True, chroma_db=False, display_benchmark_info=True)
        response_dto = ResponseDTO(
            title=f"Resposta à pergunta: {question}", 
            neo4j_response=neo4j_benchmark_dto.neo4j_response, 
            neo4j_query=neo4j_benchmark_dto.neo4j_query, 
            neo4j_query_response=neo4j_benchmark_dto.neo4j_query_response,
            azure_ai_search_response=azure_ai_search_benchmark_dto.response,
            azure_ai_search_docs = azure_ai_search_benchmark_dto.docs
        )
        return make_response(response_dto.to_dict(), 200)
    except Exception as e:
        return jsonify(str(e)), 400