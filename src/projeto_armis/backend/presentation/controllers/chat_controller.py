from dependency_injector.wiring import inject, Provide

from application.dtos.response_dto import ResponseDTO
from application.services.azure_service import AzureService

from dependency_container import DependencyContainer

from flask import Blueprint, jsonify, request, make_response

chat_blueprint = Blueprint("Chat", __name__, url_prefix="/chat")

@chat_blueprint.route("/make-question", methods=["GET"])
@inject
def make_question(service: AzureService = Provide[DependencyContainer.azure_service]):
    try:
        question = request.args.get("question")
        if not question:
            return jsonify({"error": "Pergunta não incluída", "exemplo": f"{request.path}?question=minhapergunta"})
        
        response_dto : ResponseDTO = service.make_question(question)
        return make_response(response_dto.to_dict(), 200)
    except Exception as e:
        return jsonify(str(e)), 400