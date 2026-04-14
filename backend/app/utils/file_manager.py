# le e lista ficheiros sob generated para endpoints de inventario
from pathlib import Path
from typing import List
from datetime import datetime

from backend.app.api.models import FileInfo


class FileManager:
    # caminhos relativos ao project_root e pasta generated
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.output_dir = self.project_root / "generated"
        self.dsl_dir = self.project_root / "dsl"

    def list_files(self, directory: str, extensions: List[str]) -> List[FileInfo]:
        # directory e subpasta de generated ou raiz se for ponto
        if directory == ".":
            base_dir = self.output_dir
        else:
            base_dir = self.output_dir / directory

        if not base_dir.exists():
            return []

        files = []

        for file_path in base_dir.rglob("*"):
            if file_path.is_file():
                if extensions and file_path.suffix not in extensions:
                    continue

                stat = file_path.stat()

                files.append(FileInfo(
                    filename=file_path.name,
                    path=str(file_path.relative_to(self.project_root)),
                    size=stat.st_size,
                    created_at=datetime.fromtimestamp(stat.st_ctime),
                    file_type=file_path.suffix[1:]
                ))

        files.sort(key=lambda x: x.created_at, reverse=True)

        return files

    def list_directories(self, directory: str) -> List[FileInfo]:
        # cada entrada e uma pasta size e soma de todos os ficheiros dentro
        base_dir = self.output_dir / directory

        if not base_dir.exists():
            return []

        dirs = []

        for dir_path in base_dir.iterdir():
            if dir_path.is_dir():
                stat = dir_path.stat()

                total_size = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())

                dirs.append(FileInfo(
                    filename=dir_path.name,
                    path=str(dir_path.relative_to(self.project_root)),
                    size=total_size,
                    created_at=datetime.fromtimestamp(stat.st_ctime),
                    file_type="directory"
                ))

        dirs.sort(key=lambda x: x.created_at, reverse=True)

        return dirs

    def get_file_path(self, file_type: str, filename: str) -> Path:
        # mapeia tipo logico para subpasta esperada do pipeline
        type_dirs = {
            "bed": self.output_dir / "configs",
            "json": self.output_dir / "configs",
            "blend": self.output_dir / "3d" / "output",
            "stl": self.output_dir / "cfd",
            "simulation": self.output_dir / "cfd"
        }

        base_dir = type_dirs.get(file_type, self.output_dir)

        return base_dir / filename
