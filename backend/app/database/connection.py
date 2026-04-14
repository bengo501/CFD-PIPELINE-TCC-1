# motor sql engine sessoes e helper de arranque
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

# carrega ficheiro env se existir
load_dotenv()

# url completa do banco sqlite local por defeito
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./cfd_pipeline.db"
)

# engine e a fabrica de ligacoes ao banco
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # testa ligacao antes de cada uso do pool
    pool_size=10,        # ligacoes mantidas abertas
    max_overflow=20,     # ligacoes extra temporarias
    echo=False           # True imprime sql no log
)

# factory que produz objetos Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# classe base declarative para subclasses em models
Base = declarative_base()


class DatabaseConnection:
    # metodos estaticos para arranque e teste
    @staticmethod
    def get_session() -> Session:
        # devolve uma sessao nova quem chama deve fechar ou usar contexto
        return SessionLocal()

    @staticmethod
    def create_tables():
        # cria todas as tabelas definidas em models que herdam Base
        Base.metadata.create_all(bind=engine)
        # sqlite antigo pode nao ter coluna options_json
        DatabaseConnection._ensure_sqlite_app_settings_options()
        print("[OK] tabelas criadas no banco de dados")

    @staticmethod
    def _ensure_sqlite_app_settings_options():
        # migracao leve so sqlite adiciona coluna se faltar
        url = str(DATABASE_URL or "")
        if not url.startswith("sqlite"):
            return
        from sqlalchemy import inspect, text

        insp = inspect(engine)
        if "app_settings" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("app_settings")}
        if "options_json" in cols:
            return
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE app_settings ADD COLUMN options_json TEXT"))
        print("[OK] coluna app_settings.options_json adicionada (sqlite)")

    @staticmethod
    def drop_tables():
        # apaga todas as tabelas so para dev
        Base.metadata.drop_all(bind=engine)
        print("[OK] tabelas removidas do banco de dados")

    @staticmethod
    def check_connection() -> bool:
        # select simples para ver se o banco responde
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"[ERRO] falha na conexao: {e}")
            return False


def get_db() -> Generator[Session, None, None]:
    # dependencia fastapi abre sessao por pedido e fecha no fim
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
