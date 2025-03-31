from services.teste_service import Teste_Service

from flask import Blueprint, jsonify

blueprint = Blueprint("TESTE", __name__)

@blueprint.route('/get-all-graph-info', methods=['GET'])
def get_application_status():
    service = Teste_Service()
    results = service.get_all_nodes()
    return jsonify(results), 200
