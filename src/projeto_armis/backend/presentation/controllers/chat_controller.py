from dependency_injector.wiring import inject, Provide

from application.dtos.response_dto import ResponseDTO
from application.services.azure_service import AzureService
from application.services.neo4j_service import Neo4jService

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
    
@chat_blueprint.route("/import-file", methods=["GET"])
@inject
def import_file(azure_service: AzureService = Provide[DependencyContainer.azure_service], neo4j_service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
    filename = request.args.get("filename")
    if not filename:
        return {"error": "Nome do ficheiro não incluído", "exemplo": f"{request.path}?filename=meuficheiro.txt"}, 400
    clear = True
    try:
        if clear:
            azure_service.clear_azure_index()
            #azure_service.clear_azure_index2()
            neo4j_service.clean_db()
        imported_docs = azure_service.import_file(filename=filename)
        for doc in imported_docs:
            print(f"[Chat Controller]: Imported {doc} to Azure Ai Search.")
        azure_service.extract_entities_and_relations(filename=filename, output_filename="yeye.txt")
        imported_nodes, imported_relationshipts = neo4j_service.import_file(filename="yeye.txt")
        print(f"[Chat Controller]: Imported {imported_relationshipts} nodes to Neo4j.")
        print(f"[Chat Controller]: Imported {imported_relationshipts} relationships to Neo4j.")
        response_dto = ResponseDTO(
            title="Importing files to neo4j and azure ai search.",
            imported_docs=imported_docs,
            imported_nodes=[node.to_dict() for node in imported_nodes],
            imported_relationshipts=[rela.to_dict() for rela in imported_relationshipts]
        )
        return make_response(response_dto.to_dict(), 200)
        
    except Exception as e:
        return jsonify(str(e)), 400