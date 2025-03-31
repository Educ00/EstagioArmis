from flask import Blueprint, jsonify, request
import os

from services.files_service import FilesService

files_blueprint = Blueprint("Files", __name__)


@files_blueprint.route("/import-file", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo inválido"}), 400

    service = FilesService()
    result = service.upload_file(file)

    return jsonify(result), 201