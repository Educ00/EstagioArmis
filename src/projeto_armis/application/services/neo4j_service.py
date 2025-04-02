
from infrastructure.repositories.neo4j_repository import Neo4jRepository

class Neo4jService:
    def __init__(self, repository: Neo4jRepository):
        self.repository = repository

    def get_all_nodes(self):
        return self.repository.get_all_nodes()
    
    def import_nodes(self, nodes: (str, str, str)) -> int :
        return self.repository.import_nodes(nodes)
        