# configura sqlalchemy engine session factory e helpers de arranque
# tambem expoe get db como dependencia fastapi
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

# carrega variaveis de um ficheiro env ao lado do projeto se existir
load_dotenv()

# string de ligacao completa prioriza env senao sqlite local no cwd
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./cfd_pipeline.db"
)

# engine mantem pool de ligacoes e traduz orm para sql
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

# session local fabrica objetos session ligados ao engine acima
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# base e a classe mae declarative usada em database models
Base = declarative_base()


class DatabaseConnection:
    # agrupa operacoes estaticas para nao precisar de estado de instancia
    @staticmethod
    def get_session() -> Session:
        # quem recebe deve fechar ou usar with em codigo novo
        return SessionLocal()

    @staticmethod
    def create_tables():
        # create all varre metadata registrada nas classes que herdam base
        Base.metadata.create_all(bind=engine)
        # migracao manual leve para bases sqlite antigas
        DatabaseConnection._ensure_sqlite_app_settings_options()
        print("[OK] tabelas criadas no banco de dados")

    @staticmethod
    def _ensure_sqlite_app_settings_options():
        # so executa em sqlite e so se faltar coluna options json
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
        # destrutivo util apenas em testes locais
        Base.metadata.drop_all(bind=engine)
        print("[OK] tabelas removidas do banco de dados")

    @staticmethod
    def check_connection() -> bool:
        # select 1 e o menor comando para validar sessao e permissoes
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"[ERRO] falha na conexao: {e}")
            return False


def get_db() -> Generator[Session, None, None]:
    # padrao yield garante fecho mesmo se endpoint lancar excecao
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
