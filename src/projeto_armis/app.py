from flask import Flask

from api.controllers.file_controller import files_blueprint
from api.controllers.teste_controller import teste_blueprint
from api.controllers.default_controller import default
from core.constants import UPLOAD_FOLDER
from infrastructure.utils.config import read_env_config, config_upload_folder
from infrastructure.utils.exceptions import error_handler
from infrastructure.utils.utils import get_port

app = Flask(__name__)


def before_all():
    read_env_config()
    config_upload_folder(app)

def init_application():
   
    app.register_blueprint(default)
    app.register_blueprint(teste_blueprint)
    app.register_blueprint(files_blueprint)
    app.register_error_handler(Exception, error_handler)


def start_application():
    app.run(port=get_port())


if __name__ == '__main__':
    before_all()
    init_application()
    start_application()
