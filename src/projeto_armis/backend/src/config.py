from pathlib import Path

from os import makedirs, sep

from dotenv import load_dotenv


def read_env_config():
    root_path = Path(__file__).resolve().parents[2]
    env_path = root_path / ".env"
    load_dotenv(dotenv_path=env_path)


def config_upload_folder(app):
    app.config["UPLOAD_FOLDER"] = "uploads"
    app.config["OUTPUT_FOLDER"] = "outputs"
    app.config["EXTRACTION_FOLDER"] = "outputs/extractions"
    app.config["BENCHMARK_FOLDER"] = "outputs/benchmarks"
    app.config["QUESTION_FOLDER"] = "outputs/questions"
    makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
    makedirs(app.config["EXTRACTION_FOLDER"], exist_ok=True)
    makedirs(app.config["BENCHMARK_FOLDER"], exist_ok=True)
    makedirs(app.config["QUESTION_FOLDER"], exist_ok=True)
    return app