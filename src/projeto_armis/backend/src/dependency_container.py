from dependency_injector import containers, providers

from application.services.azure_service import AzureService
from application.services.chat_service import ChatService
from application.services.chroma_service import ChromaService
from infrastructure.adapters.azure_adapter import AzureAdapter
from infrastructure.adapters.chroma_adapter import ChromaAdapter
from infrastructure.adapters.neo4j_adapter import Neo4jAdapter
from infrastructure.repositories.azure_repository import AzureRepository
from infrastructure.repositories.chroma_repository import ChromaRepository
from infrastructure.repositories.neo4j_repository import Neo4jRepository
from application.services.files_service import FilesService
from application.services.neo4j_service import Neo4jService


def setup_dependency_container(app, modules=None, packages=None):
    container = DependencyContainer()
    app.container = container
    app.container.wire(modules=modules, packages=packages)
    return app

class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration()
    
    neo4j_adapter = providers.Singleton(Neo4jAdapter)
    azure_adapter = providers.Singleton(AzureAdapter)
    chroma_adapter = providers.Factory(ChromaAdapter)
    neo4j_repository = providers.Factory(Neo4jRepository, neo4j_adapter = neo4j_adapter)
    azure_repository = providers.Factory(AzureRepository, azure_adapter=azure_adapter)
    chroma_repository = providers.Factory(ChromaRepository, chroma_adapter=chroma_adapter)
    
    neo4j_service = providers.Factory(Neo4jService, neo4j_repository=neo4j_repository, azure_adapter=azure_adapter)
    azure_service = providers.Factory(AzureService, azure_adapter=azure_adapter, azure_repository=azure_repository, neo4j_repository=neo4j_repository)
    
    chroma_service = providers.Factory(ChromaService, chroma_repository=chroma_repository) 
    
    chat_service = providers.Factory(ChatService, azure_service=azure_service, neo4j_service=neo4j_service, chroma_service=chroma_service)
    
    files_service = providers.Factory(FilesService)
    