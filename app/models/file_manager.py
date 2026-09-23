import os
import shutil
from pathlib import Path
from werkzeug.utils import secure_filename

# Lista blanca de extensiones permitidas
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'json',
    'py', 'html', 'css', 'js', 'md', 'doc', 'docx', 'xls', 'xlsx'
}

# Límite global de almacenamiento permitido en uploads (500 MB)
MAX_STORAGE_BYTES = 500 * 1024 * 1024 

class FileManagerModel:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_safe_path(self, subpath: str) -> Path:
        target_path = (self.base_dir / subpath).resolve()
        if not str(target_path).startswith(str(self.base_dir)):
            raise PermissionError("Acceso no permitido fuera del directorio base.")
        return target_path

    def get_total_storage_used(self) -> int:
        """Calcula el peso total acumulado en la carpeta uploads."""
        total = 0
        for entry in self.base_dir.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
        return total

    def is_allowed_file(self, filename: str) -> bool:
        """Verifica si la extensión del archivo está en la lista blanca."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def check_storage_quota(self, incoming_size: int = 0):
        """Verifica si queda espacio en el servidor antes de guardar."""
        current_used = self.get_total_storage_used()
        if current_used + incoming_size > MAX_STORAGE_BYTES:
            max_mb = MAX_STORAGE_BYTES / (1024 * 1024)
            raise OverflowError(f"Se ha alcanzado la cuota máxima de espacio en disco ({max_mb:.0f} MB).")

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
        if not self.is_allowed_file(filename):
            raise ValueError(f"Extensión no permitida para el archivo '{filename}'.")

        self.check_storage_quota()
        target_path = self._get_safe_path(subpath) / filename
        file_storage.save(target_path)

    def save_relative_file(self, subpath: str, rel_path: str, file_storage):
        parts = [secure_filename(p) for p in rel_path.replace("\\", "/").split("/") if p]
        if not parts:
            return
        
        filename = parts[-1]
        if not self.is_allowed_file(filename):
            raise ValueError(f"El archivo '{filename}' tiene una extensión no permitida y fue rechazado.")

        self.check_storage_quota()

        target_dir = self._get_safe_path(subpath)
        for d in parts[:-1]:
            target_dir = target_dir / d
            target_dir.mkdir(parents=True, exist_ok=True)
            
        file_dest = target_dir / filename
        file_storage.save(file_dest)

    def delete_item(self, subpath: str):
        """Elimina un archivo o una carpeta con todo su contenido."""
        if not subpath:
            raise ValueError("No se puede eliminar la carpeta raíz.")
        
        target_path = self._get_safe_path(subpath)
        if not target_path.exists():
            raise FileNotFoundError("El elemento que intenta eliminar no existe.")

        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()

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
