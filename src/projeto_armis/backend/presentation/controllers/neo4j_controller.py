from dependency_injector.wiring import inject, Provide

from application.services.neo4j_service import Neo4jService
from dependency_container import DependencyContainer

from flask import Blueprint, jsonify, request

neo4j_blueprint = Blueprint("Neo4j", __name__, url_prefix="/neo4j")

@neo4j_blueprint.route("/import-file", methods=["GET"])
@inject
def import_file(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
    """
    Importa um arquivo com nós e relacionamentos para a Base de Dados Neo4j configurada
    :param service: Instância do serviço NEo4jService, injetada automaticamente
    :return: JSON com os resultados da importação ou mensagem de erro.
    """
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Nome do ficheiro não incluído", "exemplo": f"{request.path}?filename=meuficheiro.txt"}), 400
    try:
        results = service.import_file(filename)
    except Exception as e:
        return jsonify(str(e)), 400
    return jsonify(results), 201

@neo4j_blueprint.route("/import-nodes", methods=["GET"])
@inject
def import_nodes(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
    """
    Importa nós para o Neo4j a partir de um ficheiro.

    :param service: Instância do serviço Neo4jService, injetada automaticamente.
    :return: JSON com os resultados da importação ou mensagem de erro. 
    """
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Nome do ficheiro não incluído", "exemplo": f"{request.path}?filename=meuarquivo.txt"}), 400
    try:
        results = service.import_nodes(filename)
    except Exception as e:
        return jsonify(str(e)), 400
    return jsonify(results), 201

@neo4j_blueprint.route("/import-relationships", methods=["GET"])
@inject
def import_relationships(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
    """
    Importa relacionamentos para o Neo4j a partir de um ficheiro.

    :param service: Instância do serviço Neo4jService, injetada automaticamente.
    :return: JSON com os resultados da importação ou mensagem de erro.
    """
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Nome do ficheiro não incluído", "exemplo": f"{request.path}?filename=meuarquivo.txt"}), 400
    try:
        results = service.import_relationships(filename)
    except Exception as e:
        return jsonify(str(e)), 400
    return jsonify(results), 201

@neo4j_blueprint.route('/get-all-nodes', methods=['GET'])
@inject
def get_all_nodes(service : Neo4jService= Provide[DependencyContainer.neo4j_service]):
    """
    Retorna todos os nós do banco de dados Neo4j.

    :param service: Instância do serviço Neo4jService, injetada automaticamente.
    :return: JSON com a lista de nós ou mensagem de erro.
    """
    try:
        results = service.get_all_nodes()
    except Exception as e:
        return jsonify(str(e)), 400
    return jsonify(results), 200

@neo4j_blueprint.route("/clean-db", methods=["GET"])
@inject
def clean_db(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
    """
    Limpa o banco de dados Neo4j, removendo todos os nós e relacionamentos.

    :param service: Instância do serviço Neo4jService, injetada automaticamente.
    :return: JSON confirmando a limpeza do banco de dados ou mensagem de erro.
    """
    try:
        service.clean_db()
    except Exception as e:
        return jsonify(str(e)), 400
    return jsonify({"message": "done!"}), 200
