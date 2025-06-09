from pathlib import Path
from string import Template

from os import makedirs, sep

from dotenv import load_dotenv


def read_env_config():
    root_path = Path(__file__).resolve().parents[4]
    env_path = root_path / ".env"
    load_dotenv(dotenv_path=env_path)


def config_upload_folder(app):
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['OUTPUT_FOLDER'] = 'outputs'
    makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    return app