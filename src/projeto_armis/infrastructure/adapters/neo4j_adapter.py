from os import getenv


from langchain_neo4j import Neo4jGraph

class Neo4jAdapter:
    def __init__(self):    
        print("A iniciar conexão a base de dados...")
        self.db = Neo4jGraph(url=getenv("NEO4J_URI"), username=getenv("NEO4J_USERNAME"),
                             password=getenv("NEO4J_PASSWORD"))
        print("Conexão estabelecida!")

    def run_query(self, query: str, params: dict = None):
        """Executa uma query Cypher no Neo4j"""
        result = self.db.query(query, params or {})
        return result

    def initialize_db(self):
        return self.db