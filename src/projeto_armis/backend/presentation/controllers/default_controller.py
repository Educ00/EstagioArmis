from flask import Blueprint, send_from_directory
import os

default_blueprint = Blueprint("Default Routes", __name__)

class DefaultController:
    

    @default_blueprint.route("/favicon.ico", methods=["GET"])
    @staticmethod
    def favicon():
        return send_from_directory(os.path.join(os.getcwd(), "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon")
