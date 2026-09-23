import os
from flask import Flask
from app.controllers.file_controller import create_file_blueprint

def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'views', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.secret_key = 'clave_secreta_para_sesiones_y_mensajes'

    upload_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
    app.register_blueprint(create_file_blueprint(upload_folder))

    return app