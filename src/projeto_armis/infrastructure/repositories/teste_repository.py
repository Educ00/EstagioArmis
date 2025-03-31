from infrastructure.repositories.base_repository import BaseRepository


class TesteRepository(BaseRepository):
    def get_all_nodes(self):
        query_template = '''
        MATCH (m) return m
        '''
        results = self.run_query(query=query_template)
        return results