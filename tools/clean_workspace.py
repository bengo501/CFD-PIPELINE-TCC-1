import shutil
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]


def remover_diretorio(caminho: Path) -> None:
    if caminho.exists():
        print(f"removendo diretorio: {caminho}")
        shutil.rmtree(caminho, ignore_errors=True)


def remover_arquivos_glob(padrao: str) -> None:
    for caminho in RAIZ.rglob(padrao):
        if caminho.is_file():
            print(f"removendo arquivo: {caminho}")
            try:
                caminho.unlink()
            except OSError:
                pass


def limpar_basico() -> None:
    print("limpando artefatos temporarios e caches...")

    # caches python
    for dirpath in RAIZ.rglob("__pycache__"):
        remover_diretorio(dirpath)
    remover_arquivos_glob("*.pyc")

    # pytest / cobertura
    remover_diretorio(RAIZ / ".pytest_cache")
    remover_diretorio(RAIZ / "coverage")
    remover_diretorio(RAIZ / "htmlcov")

    # node_modules do frontend
    remover_diretorio(RAIZ / "frontend" / "node_modules")

    # arquivos de log soltos
    remover_arquivos_glob("*.log")

    # saidas de testes e2e
    e2e_dir = RAIZ / "scripts" / "tests" / "e2e"
    for sub in ("outputs", "results", "logs"):
        for caminho in e2e_dir.rglob(sub):
            if caminho.is_dir():
                remover_diretorio(caminho)


def limpar_generated() -> None:
    alvo = RAIZ / "generated"
    if alvo.exists():
        print("atencao: isto vai apagar TODOS os casos cfd, modelos 3d e configs geradas em 'generated/'.")
        resp = input("digite 'SIM' para confirmar: ").strip()
        if resp == "SIM":
            remover_diretorio(alvo)
        else:
            print("limpeza de 'generated/' cancelada.")


if __name__ == "__main__":
    print(f"raiz do projeto: {RAIZ}")
    limpar_basico()

    print()
    opcional = input("tambem deseja limpar a pasta 'generated/' (resultados de simulacoes)? [s/N]: ").strip().lower()
    if opcional == "s":
        limpar_generated()

    print("limpeza concluida.")

