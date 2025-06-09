from flask import Flask
from flask_cors import CORS
import logging

from presentation.routes import setup_blueprints
from dependency_container import setup_dependency_container
from config import read_env_config, config_upload_folder
from core.utils.exceptions import error_handler
from core.utils.utils import get_port


logger = logging.getLogger(__name__)

def before_all():
    read_env_config()

def init_application():
    app = Flask(__name__)
    CORS(app)

    app = config_upload_folder(app)
    
    setup_blueprints(app)
    
    app = setup_dependency_container(app, packages=["presentation.controllers"])
    
    app.register_error_handler(Exception, error_handler)
    
    app.run(port=get_port())
    


if __name__ == '__main__':
    before_all()
    init_application()
