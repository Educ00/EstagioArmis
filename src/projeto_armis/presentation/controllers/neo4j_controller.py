from dependency_injector.wiring import inject, Provide

from application.services.neo4j_service import Neo4jService
from dependency_container import DependencyContainer

from flask import Blueprint, jsonify, request

neo4j_blueprint = Blueprint("Neo4j", __name__, url_prefix="/neo4j")

@neo4j_blueprint.route("/import-file", methods=["GET"])
@inject
def import_file(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Nome do ficheiro não incluído", "exemplo": f"{request.path}?filename=meuarquivo.txt"}), 400
    try:
        results = service.import_file(filename)
    except Exception as e:
        return jsonify(e), 400
    return jsonify(results), 201

@neo4j_blueprint.route("/import-nodes", methods=["GET"])
@inject
def import_nodes(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Nome do ficheiro não incluído", "exemplo": f"{request.path}?filename=meuarquivo.txt"}), 400
    try:
        results = service.import_nodes(filename)
    except Exception as e:
        return jsonify(e), 400
    return jsonify(results), 201

@neo4j_blueprint.route("/import-relationships", methods=["GET"])
@inject
def import_relationships(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Nome do ficheiro não incluído", "exemplo": f"{request.path}?filename=meuarquivo.txt"}), 400
    try:
        results = service.import_relationships(filename)
    except Exception as e:
        return jsonify(e), 400
    return jsonify(results), 201

@neo4j_blueprint.route('/get-all-nodes', methods=['GET'])
@inject
def get_all_nodes(service : Neo4jService= Provide[DependencyContainer.neo4j_service]):
    try:
        results = service.get_all_nodes()
    except Exception as e:
        return jsonify(e), 400
    return jsonify(results), 200

@neo4j_blueprint.route("/clean-db", methods=["GET"])
@inject
def clean_db(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
    try:
        service.clean_db()
    except Exception as e:
        return jsonify(e), 400
    return jsonify({"message": "done!"}), 200
