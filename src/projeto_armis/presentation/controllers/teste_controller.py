from dependency_injector.wiring import inject, Provide

from application.services.neo4j_service import Neo4jService
from dependency_container import DependencyContainer

from flask import Blueprint, jsonify

teste_blueprint = Blueprint("TESTE", __name__)

@teste_blueprint.route('/get-all-graph-info', methods=['GET'])
@inject
def get_application_status(service : Neo4jService= Provide[DependencyContainer.neo4j_service]):
    results = service.get_all_nodes()
    return jsonify(results), 200
