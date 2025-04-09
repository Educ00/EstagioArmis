from pathlib import Path
from string import Template

from os import makedirs, sep

from dotenv import load_dotenv


def read_env_config():
    config_path = sep + ".env"
    root_path = Path(__file__).parent.parent.parent.parent

    dot_env_file_path = Template('$root$config').substitute(root=root_path, config=config_path)
    load_dotenv(dotenv_path=dot_env_file_path)


def config_upload_folder(app):
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['OUTPUT_FOLDER'] = 'outputs'
    makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    return app