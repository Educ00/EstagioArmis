import json
from flask import current_app
from infrastructure.repositories.neo4j_repository import Neo4jRepository

class Neo4jService:
    def __init__(self, repository: Neo4jRepository):
        self.repository = repository

    def get_all_nodes(self):
        """
        Returns all nodes
        :return: nodes
        """
        return self.repository.get_all_nodes()
    
    def import_file(self, filename: str): 
        """
        Imports a file composed of entities and relationships from upload folder
        :param filename: name of the file
        :return: number of imported nodes, number of imported relationships
        """
        imported_nodes = self.import_nodes(filename)
        imported_relationships = self.import_relationships(filename)
        return imported_nodes, imported_relationships
    
    
    def import_nodes(self, filename : str):
        """
        Imports a file composed of entities
        :param filename: name of the file
        :return: number of imported nodes
        """
        folder_name = current_app.config['OUTPUT_FOLDER']
        file_path = folder_name + "/" + filename
        print(file_path)
        with open(file_path, "r", encoding="utf-8") as json_data:
            data = json.load(json_data)

        nodes = []
        for entity in data["entities"]:
            nodes.append((entity["name"], entity["category"], entity["description"]))
        
        return self.repository.import_nodes(nodes)

    def import_relationships(self, filename : str):
        """
        Imports a file composed of relationships from upload folder
        :param filename: name of the file
        :return: number of imported relationships
        """
        folder_name = current_app.config['OUTPUT_FOLDER']
        file_path = folder_name + "/" + filename
        print(file_path)
        with open(file_path, "r", encoding="utf-8") as json_data:
            data = json.load(json_data)

        relationships = []
        for entity in data["relationships"]:
            relationships.append((entity["source"], entity["target"], entity["value"]))
        return self.repository.import_relationships(relationships)

    def clean_db(self):
        """
        Clean Entire Database
        """
        return self.repository.clean_db()
        