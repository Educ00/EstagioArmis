from dependency_injector.wiring import inject, Provide

from application.services.azure_service import AzureService

from dependency_container import DependencyContainer

from flask import Blueprint, jsonify, current_app, request

azure_blueprint = Blueprint("Azure", __name__, url_prefix="/azure")

@azure_blueprint.route("/generate-query", methods=["GET"])
@inject
def generate_query(service: AzureService = Provide[DependencyContainer.azure_service]):
    try:
        response = service.generate_query_and_query("Por onde foi a Sofia?")
        print(response)
        return jsonify(response), 400
    except Exception as e:
        return jsonify(e), 400
        

@azure_blueprint.route("/extract-entities-and-relations", methods=["GET"])
@inject
def process_file(service: AzureService = Provide[DependencyContainer.azure_service]):
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Nome do ficheiro não incluído", "exemplo": f"{request.path}?filename=meuarquivo.txt"}), 400
    
    results = service.extract_entities_and_relations(file_name=filename, save_to_file=True)
    return jsonify(results), 200