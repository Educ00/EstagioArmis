import json
from flask import current_app
from infrastructure.repositories.neo4j_repository import Neo4jRepository

class Neo4jService:
    def __init__(self, repository: Neo4jRepository):
        self.repository = repository

    def get_all_nodes(self):
        return self.repository.get_all_nodes()
    
    def import_file(self, filename: str):  
        imported_nodes = self.import_nodes(filename)
        imported_relationships = self.import_relationships(filename)
        return imported_nodes, imported_relationships
    
    
    def import_nodes(self, filename : str):
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
        return self.repository.clean_db()
        