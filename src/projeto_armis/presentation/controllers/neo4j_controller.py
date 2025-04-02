from dependency_injector.wiring import inject, Provide

from application.services.neo4j_service import Neo4jService
from dependency_container import DependencyContainer

from flask import Blueprint, jsonify

neo4j_blueprint = Blueprint("TESTE", __name__)

@teste_blueprint.route('/get-all-graph-info', methods=['GET'])
@inject
def get_all_nodes(service : Neo4jService= Provide[DependencyContainer.neo4j_service]):
    results = service.get_all_nodes()
    return jsonify(results), 200

@neo4j_blueprint.route("/clean-db", methods=["GET"])
@inject
def clean_db(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
    service.clean_db()
    return jsonify({"message": "done!"}), 200
