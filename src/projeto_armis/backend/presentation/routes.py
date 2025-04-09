from flask import Flask

from presentation.controllers.azure_controller import azure_blueprint
from presentation.controllers.chat_controller import chat_blueprint
from presentation.controllers.default_controller import default_blueprint
from presentation.controllers.file_controller import files_blueprint
from presentation.controllers.neo4j_controller import neo4j_blueprint

def setup_blueprints(app: Flask):
    app.register_blueprint(default_blueprint)
    app.register_blueprint(files_blueprint)
    app.register_blueprint(neo4j_blueprint)
    app.register_blueprint(azure_blueprint)
    app.register_blueprint(chat_blueprint)