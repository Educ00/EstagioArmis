from dependency_injector import containers, providers

from infrastructure.adapters.neo4j_connection import Neo4jConnection
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

    neo4j_connection = providers.Singleton(Neo4jConnection)
    
    neo4j_repository = providers.Factory(Neo4jRepository, connection = neo4j_connection)
    #neo4j_repository = providers.Factory(Neo4jRepository)
    neo4j_service = providers.Factory(Neo4jService, repository=neo4j_repository)
    
    
    files_service = providers.Factory(FilesService)
    