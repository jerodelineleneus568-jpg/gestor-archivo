from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.file_manager import FileManagerModel

def create_file_blueprint(upload_folder: str):
    bp = Blueprint('files', __name__)
    model = FileManagerModel(upload_folder)

    @bp.route('/', defaults={'subpath': ''}, methods=['GET'])
    @bp.route('/browse/<path:subpath>', methods=['GET'])
    def browse(subpath):
        try:
            items = model.list_contents(subpath)
            parent = "/".join(subpath.rstrip("/").split("/")[:-1]) if subpath else None
            return render_template('explorer.html', items=items, current_path=subpath, parent=parent)
        except Exception as e:
            flash(f"Error al listar: {str(e)}", "danger")
            return redirect(url_for('files.browse'))

    @bp.route('/upload', methods=['POST'])
    def upload_file():
        subpath = request.form.get('subpath', '')
        file = request.files.get('file')
        if not file or file.filename == '':
            flash("No se seleccionó ningún archivo", "warning")
        else:
            try:
                model.save_file(subpath, file)
                flash("Archivo subido con éxito", "success")
            except Exception as e:
                flash(f"Error al subir: {str(e)}", "danger")
        return redirect(url_for('files.browse', subpath=subpath))

    @bp.route('/upload_folder', methods=['POST'])
    def upload_folder():
        subpath = request.form.get('subpath', '')
        files = request.files.getlist('files[]')
        paths = request.form.getlist('paths[]')

        if not files or len(files) == 0:
            return jsonify({"status": "error", "message": "No se recibieron archivos"}), 400

        try:
            for file, rel_path in zip(files, paths):
                model.save_relative_file(subpath, rel_path, file)
            return jsonify({"status": "success", "message": "Carpeta subida con éxito"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @bp.route('/mkdir', methods=['POST'])
    def make_directory():
        subpath = request.form.get('subpath', '')
        folder_name = request.form.get('folder_name', '')
        try:
            model.create_folder(subpath, folder_name)
            flash("Carpeta creada correctamente", "success")
        except Exception as e:
            flash(f"Error al crear carpeta: {str(e)}", "danger")
        return redirect(url_for('files.browse', subpath=subpath))

    @bp.route('/view/<path:subpath>', methods=['GET'])
    def view_file(subpath):
        try:
            file_data = model.read_file(subpath)
            parent = "/".join(subpath.rstrip("/").split("/")[:-1])
            return render_template('viewer.html', file_data=file_data, parent=parent, subpath=subpath)
        except Exception as e:
            flash(f"Error al abrir archivo: {str(e)}", "danger")
            return redirect(url_for('files.browse'))

    return bp