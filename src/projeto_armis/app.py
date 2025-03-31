from flask import Flask

from api.controllers.teste_controller import blueprint
from api.controllers.default_controller import default
from infrastructure.utils.config import read_env_config
from infrastructure.utils.exceptions import error_handler
from infrastructure.utils.utils import get_port

app = Flask(__name__)


def before_all():
    read_env_config()

def init_application():
    app.register_blueprint(blueprint)
    app.register_blueprint(default)
    app.register_error_handler(Exception, error_handler)


def start_application():
    app.run(port=get_port())


if __name__ == '__main__':
    before_all()
    init_application()
    start_application()
