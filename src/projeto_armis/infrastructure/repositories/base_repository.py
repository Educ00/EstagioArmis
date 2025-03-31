from infrastructure.database.connection import DatabaseConnection


class BaseRepository:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def run_query(self, query: str, params: dict = None):
        """Executa uma query Cypher no Neo4j"""
        return self.db.run_query(query, params or {})