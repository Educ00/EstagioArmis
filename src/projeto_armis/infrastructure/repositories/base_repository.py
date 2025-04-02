from infrastructure.adapters.neo4j_connection import Neo4jConnection

class BaseRepository:
    def __init__(self, connection : Neo4jConnection):
        self.db = connection
        
    def run_query(self, query: str, params: dict = None):
        """Executa uma query Cypher no Neo4j"""
        return self.db.run_query(query, params or {})