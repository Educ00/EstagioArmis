import os

from dependency_injector.wiring import inject, Provide
from flask import Blueprint, jsonify, request, send_from_directory

from application.services.files_service import FilesService

from dependency_container import DependencyContainer

files_blueprint = Blueprint("Files", __name__, url_prefix="/files")

class FileController:

    @files_blueprint.route("/import-file", methods=["POST"])
    @staticmethod
    @inject
    def upload_file(file_service : FilesService = Provide[DependencyContainer.files_service]):
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Nome de arquivo inválido"}), 400
    
        result = file_service.upload_file(file)
    
        return jsonify(result), 201

    @files_blueprint.route("/favicon.ico", methods=["GET"])
    @staticmethod
    def favicon():
        return send_from_directory(os.path.join(os.getcwd(), "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon")
