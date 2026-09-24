import os
from flask import Flask, render_template, flash, redirect, url_for
from app.controllers.file_controller import create_file_blueprint

def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'views', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.secret_key = 'clave_secreta_para_sesiones_y_mensajes'

    # Límite máximo por archivo individual / petición: 16 MB
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    upload_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
    app.register_blueprint(create_file_blueprint(upload_folder))

    # Manejar error cuando un archivo excede el tamaño máximo
    @app.errorhandler(413)
    def request_entity_too_large(error):
        flash("El archivo supera el tamaño máximo permitido por subida (16 MB).", "danger")
        return redirect(url_for('files.browse'))

    return app
