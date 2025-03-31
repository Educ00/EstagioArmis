from infrastructure.repositories.teste_repository import TesteRepository



class Teste_Service:
    def __init__(self):
        self.repository = TesteRepository()
        
    def get_all_nodes(self):
        return self.repository.get_all_nodes()
        