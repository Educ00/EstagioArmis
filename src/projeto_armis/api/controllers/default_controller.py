from flask import Blueprint, send_from_directory
import os

default = Blueprint("Default Routes", __name__)

@default.route("/favicon.ico", methods=["GET"])
def favicon():
    print(os.path.join(os.getcwd(), "static"))
    return send_from_directory(os.path.join(os.getcwd(), "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon")
