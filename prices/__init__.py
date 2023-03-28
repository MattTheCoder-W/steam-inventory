import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {'xlsx'}

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'zaq1@WSX'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
