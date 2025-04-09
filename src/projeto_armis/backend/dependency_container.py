from dependency_injector import containers, providers

from application.services.azure_service import AzureService
from infrastructure.adapters.azure_adapter import AzureAdapter
from infrastructure.adapters.neo4j_adapter import Neo4jAdapter
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
    neo4j_repository = providers.Factory(Neo4jRepository, adapter = neo4j_adapter)
    neo4j_service = providers.Factory(Neo4jService, repository=neo4j_repository)
    
    azure_adapter = providers.Singleton(AzureAdapter)
    azure_service = providers.Factory(AzureService, azure_adapter=azure_adapter, neo4j_repository=neo4j_repository)
    
    files_service = providers.Factory(FilesService)
    