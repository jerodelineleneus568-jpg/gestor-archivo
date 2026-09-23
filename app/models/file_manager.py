import os
from pathlib import Path
from werkzeug.utils import secure_filename

class FileManagerModel:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_safe_path(self, subpath: str) -> Path:
        target_path = (self.base_dir / subpath).resolve()
        if not str(target_path).startswith(str(self.base_dir)):
            raise PermissionError("Acceso no permitido fuera del directorio base.")
        return target_path

    def list_contents(self, subpath: str = ""):
        folder = self._get_safe_path(subpath)
        items = []
        for entry in folder.iterdir():
            items.append({
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size": entry.stat().st_size if entry.is_file() else None,
                "rel_path": str(entry.relative_to(self.base_dir)).replace("\\", "/")
            })
        return sorted(items, key=lambda x: (not x["is_dir"], x["name"].lower()))

    def create_folder(self, subpath: str, folder_name: str):
        folder_name = secure_filename(folder_name)
        if not folder_name:
            raise ValueError("Nombre de carpeta inválido")
        target_folder = self._get_safe_path(subpath) / folder_name
        target_folder.mkdir(exist_ok=False)

    def save_file(self, subpath: str, file_storage):
        filename = secure_filename(file_storage.filename)
        if not filename:
            raise ValueError("Nombre de archivo inválido")
        target_path = self._get_safe_path(subpath) / filename
        file_storage.save(target_path)

    def save_relative_file(self, subpath: str, rel_path: str, file_storage):
        parts = [secure_filename(p) for p in rel_path.replace("\\", "/").split("/") if p]
        if not parts:
            return
        
        target_dir = self._get_safe_path(subpath)
        for d in parts[:-1]:
            target_dir = target_dir / d
            target_dir.mkdir(parents=True, exist_ok=True)
            
        file_dest = target_dir / parts[-1]
        file_storage.save(file_dest)

    def read_file(self, subpath: str):
        target_path = self._get_safe_path(subpath)
        if not target_path.is_file():
            raise FileNotFoundError("El archivo no existe")
        
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"type": "text", "content": content, "filename": target_path.name}
        except UnicodeDecodeError:
            return {"type": "binary", "filename": target_path.name}