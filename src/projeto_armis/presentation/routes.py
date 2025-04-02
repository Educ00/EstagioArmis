from flask import Flask

from presentation.controllers.default_controller import default_blueprint
from presentation.controllers.file_controller import files_blueprint
from presentation.controllers.teste_controller import teste_blueprint

def setup_blueprints(app: Flask):
    app.register_blueprint(default_blueprint)
    app.register_blueprint(files_blueprint)
    app.register_blueprint(teste_blueprint)