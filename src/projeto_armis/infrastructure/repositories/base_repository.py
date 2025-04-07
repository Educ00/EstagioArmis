from infrastructure.adapters.neo4j_adapter import Neo4jAdapter

class BaseRepository:
    def __init__(self, adapter : Neo4jAdapter):
        self.adapter = adapter
        
    def run_query(self, query: str, params: dict = None):
        """Executa uma query Cypher no Neo4j"""
        return self.adapter.run_query(query, params or {})