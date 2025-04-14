from os import getenv


from langchain_neo4j import Neo4jGraph

class Neo4jAdapter:
    def __init__(self):    
        print("[Neo4j Adapter]: A iniciar conexão a base de dados...")
        self.db = Neo4jGraph(url=getenv("NEO4J_URI"), username=getenv("NEO4J_USERNAME"),
                             password=getenv("NEO4J_PASSWORD"))
        print("[Neo4j Adapter]: Conexão estabelecida!")

    def run_query(self, query: str, params: dict = None):
        """
        Runs a query in the database
        :param query: query
        :param params: parameters of the query
        :return: query results
        """
        result = self.db.query(query, params or {})
        return result

    def initialize_db(self):
        """
        Initializes the Neo4jGraph instance
        :return: Neo4jGraph instance
        """
        return self.db