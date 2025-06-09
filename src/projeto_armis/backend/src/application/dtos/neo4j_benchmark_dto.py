class Neo4jBenchmarkDTO:
    def __init__(self, neo4j_response: str = None, neo4j_query: str = None, neo4j_query_response: str = None):
        self.neo4j_response = neo4j_response
        self.neo4j_query = neo4j_query
        self.neo4j_query_response = neo4j_query_response