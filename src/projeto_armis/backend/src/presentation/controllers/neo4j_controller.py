import json

from dependency_injector.wiring import inject, Provide

from application.dtos.response_dto import ResponseDTO
from application.services.neo4j_service import Neo4jService
from dependency_container import DependencyContainer

from flask import Blueprint, request, make_response

neo4j_blueprint = Blueprint("Neo4j", __name__, url_prefix="/neo4j")

class Neo4jController:

    @neo4j_blueprint.route("/import-file", methods=["GET"])
    @staticmethod
    @inject
    def import_file(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
        """
        Importa um arquivo com nós e relacionamentos para a Base de Dados Neo4j configurada
        :param service: Instância do serviço NEo4jService, injetada automaticamente
        :return: JSON com os resultados da importação ou mensagem de erro.
        """
        filename = request.args.get("filename")
        if not filename:
            return {"error": "Nome do ficheiro não incluído", "exemplo": f"{request.path}?filename=meuficheiro.txt"}, 400
        try:
            imported_nodes, imported_relationships = service.import_file(filename)
            response_dto : ResponseDTO = ResponseDTO(
                imported_nodes=[node.to_dict() for node in imported_nodes],
                imported_relationships=[rel.to_dict() for rel in imported_relationships]
            )
            return response_dto.to_dict(), 201
        except Exception as e:
            return {"error": str(e)}, 400
        
    
    @neo4j_blueprint.route('/get-all-nodes', methods=['GET'])
    @staticmethod
    @inject
    def get_all_nodes(service : Neo4jService= Provide[DependencyContainer.neo4j_service]):
        """
        Retorna todos os nós do banco de dados Neo4j.
    
        :param service: Instância do serviço Neo4jService, injetada automaticamente.
        :return: JSON com a lista de nós ou mensagem de erro.
        """
        try:
            results = service.get_all_nodes()
            response_dto = ResponseDTO(results=results)
            return make_response(response_dto.to_dict(), 200)
        except Exception as e:
            return {"error": str(e)}, 400
    
    @neo4j_blueprint.route("/clean-db", methods=["GET"])
    @staticmethod
    @inject
    def clean_db(service : Neo4jService = Provide[DependencyContainer.neo4j_service]):
        """
        Limpa o banco de dados Neo4j, removendo todos os nós e relacionamentos.
    
        :param service: Instância do serviço Neo4jService, injetada automaticamente.
        :return: JSON confirmando a limpeza do banco de dados ou mensagem de erro.
        """
        try:
            service.clean_db()
            return {"message": "done!"}, 200
        except Exception as e:
            return {"error": str(e)}, 400

