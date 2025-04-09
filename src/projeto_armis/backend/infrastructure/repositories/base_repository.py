from infrastructure.adapters.neo4j_adapter import Neo4jAdapter

class BaseRepository:
    def __init__(self, adapter : Neo4jAdapter):
        self.adapter = adapter
        
    def run_query(self, query: str, params: dict = None):
        """
        Runs a query in the database
        :param query: query
        :param params: parameters of the query
        :return: query results
        """
        return self.adapter.run_query(query, params or {})