from langchain_neo4j import Neo4jGraph

from infrastructure.persistence.connection import DatabaseConnection

from os import getenv

class BaseRepository:
    def __init__(self, connection : DatabaseConnection):
        self.db = connection
        
    def run_query(self, query: str, params: dict = None):
        """Executa uma query Cypher no Neo4j"""
        return self.db.run_query(query, params or {})