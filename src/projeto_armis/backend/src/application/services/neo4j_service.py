import json
import os

from flask import current_app

from application.dtos.entity_dto import EntityDTO
from application.dtos.relationship_dto import RelationshipDTO
from application.mappers.relationship_mapper import RelationshipMapper
from domain.models.relationship import Relationship
from infrastructure.adapters.azure_adapter import AzureAdapter
from infrastructure.repositories.neo4j_repository import Neo4jRepository

class Neo4jService:
    def __init__(self, neo4j_repository: Neo4jRepository, azure_adapter: AzureAdapter):
        self.neo4j_repository = neo4j_repository
        self.azure_adapter = azure_adapter

    def query_graph(self, question : str, allow_dangerous_requests : bool = True, return_intermediate_steps : bool = True, validate_cypher : bool = True):
        response, cb = self.neo4j_repository.query_graph(
            question=question,
            llm= self.azure_adapter.get_llm_base(),
            allow_dangerous_requests=allow_dangerous_requests,
            return_intermediate_steps=return_intermediate_steps,
            validate_cypher=validate_cypher
        )
        return response, cb

    def get_all_nodes(self):
        """
        Returns all nodes
        :return: nodes
        """
        return self.neo4j_repository.get_all_nodes()
    
    def import_file(self, filename: str, folder : str = None) -> tuple[list[EntityDTO], list[RelationshipDTO]]: 
        """
        Imports a file composed of entities and relationships from upload folder
        :param filename: name of the file. If None looks into OUTPUT_FOLDER
        :param folder: folder path
        :return: number of imported nodes, number of imported relationships
        """
        if folder is None:
            folder_name = current_app.config['OUTPUT_FOLDER']
        else:
            folder_name = folder

        file_path = folder + os.sep + filename
        with open(file_path, "r", encoding="utf-8") as json_data:
            data = json.load(json_data)

        nodes : list[EntityDTO] = []
        for entity in data["entities"]:
            name = entity["name"]
            category = entity["category"]
            description = entity["description"]
            nodes.append(EntityDTO(name=name, category=category, description=description))

        relationships : list[RelationshipDTO]= []
        for entity in data["relationships"]:
            source = entity["source"]
            target = entity["target"]
            value = entity["value"]
            relationships.append(RelationshipMapper.to_dto(Relationship(source=source, target=target, value=value)))
        
        imported_nodes = self.import_nodes(nodes=nodes)
        imported_relationships = self.import_relationships(relationships=relationships)
        
        return imported_nodes, imported_relationships
    
    
    def import_nodes(self, nodes : list[EntityDTO]) -> list[EntityDTO]:
        """
        Imports a file composed of entities
        :param nodes: lista de EntityDTO
        :return: number of imported nodes
        """
        print(f"[Neo4j Service] Importing Entities")    
        return self.neo4j_repository.import_nodes(nodes)

    def import_relationships(self, relationships : list[RelationshipDTO]) -> list[RelationshipDTO]:
        """
        Imports a file composed of relationships from upload folder
        :param: list de RelationshipDTO
        :return: number of imported relationships
        """
        print(f"[Neo4j Service] Importing Relationships")
        return self.neo4j_repository.import_relationships(relationships)

    def clean_db(self):
        """
        Clean Entire Database
        """
        print(f"[Neo4j Service]: Cleaning Neo4j database...")
        return self.neo4j_repository.clean_db()
        