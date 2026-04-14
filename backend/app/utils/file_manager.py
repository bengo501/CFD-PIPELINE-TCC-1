# abstrai listagens sobre a pasta generated para os endpoints de inventario
from pathlib import Path
from typing import List
from datetime import datetime

from backend.app.api.models import FileInfo


class FileManager:
    # guarda raiz do repo e caminhos derivados uma vez por instancia
    def __init__(self):
        # sobe quatro niveis de utils ate à pasta do repositorio
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.output_dir = self.project_root / "generated"
        self.dsl_dir = self.project_root / "dsl"

    def list_files(self, directory: str, extensions: List[str]) -> List[FileInfo]:
        # ponto significa usar diretamente generated sem subpasta extra
        if directory == ".":
            base_dir = self.output_dir
        else:
            base_dir = self.output_dir / directory

        if not base_dir.exists():
            return []

        files = []

        # rglob visita arvore completa a partir de base dir
        for file_path in base_dir.rglob("*"):
            if file_path.is_file():
                # filtro por extensao vazio aceita tudo
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

        # mais recente primeiro ajuda o frontend a mostrar topo util
        files.sort(key=lambda x: x.created_at, reverse=True)

        return files

    def list_directories(self, directory: str) -> List[FileInfo]:
        # cada pasta vira um FileInfo sintetico com size somado recursivo
        base_dir = self.output_dir / directory

        if not base_dir.exists():
            return []

        dirs = []

        for dir_path in base_dir.iterdir():
            if dir_path.is_dir():
                stat = dir_path.stat()

                # soma bytes de todos os ficheiros internos recursivamente
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
        # mapeamento alinha com convencoes do pipeline de pastas
        type_dirs = {
            "bed": self.output_dir / "configs",
            "json": self.output_dir / "configs",
            "blend": self.output_dir / "3d" / "output",
            "stl": self.output_dir / "cfd",
            "simulation": self.output_dir / "cfd"
        }

        base_dir = type_dirs.get(file_type, self.output_dir)

        return base_dir / filename
