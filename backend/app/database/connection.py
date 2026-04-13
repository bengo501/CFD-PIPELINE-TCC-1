# gerenciamento de conexao com postgresql
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

# carregar variaveis de ambiente
load_dotenv()

# configuracao do banco de dados
# padrao de desenvolvimento: sqlite local (dispensa driver postgres)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./cfd_pipeline.db"
)

# criar engine do sqlalchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # verificar conexao antes de usar
    pool_size=10,        # tamanho do pool
    max_overflow=20,     # conexoes extras permitidas
    echo=False           # nao mostrar queries sql (usar True para debug)
)

# criar session maker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# base para models
Base = declarative_base()


class DatabaseConnection:
    """gerenciador de conexao com banco de dados"""
    
    @staticmethod
    def get_session() -> Session:
        """
        obter sessao do banco de dados
        
        retorna:
            Session: sessao do sqlalchemy
        """
        return SessionLocal()
    
    @staticmethod
    def create_tables():
        """
        criar todas as tabelas no banco de dados
        
        nota:
            em producao, usar alembic para migrations
        """
        Base.metadata.create_all(bind=engine)
        DatabaseConnection._ensure_sqlite_app_settings_options()
        print("[OK] tabelas criadas no banco de dados")

    @staticmethod
    def _ensure_sqlite_app_settings_options():
        """adiciona coluna options_json em bases sqlite antigas sem migration formal."""
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
        """
        remover todas as tabelas (cuidado!)
        
        nota:
            usar apenas em desenvolvimento
        """
        Base.metadata.drop_all(bind=engine)
        print("[OK] tabelas removidas do banco de dados")
    
    @staticmethod
    def check_connection() -> bool:
        """
        verificar se conexao com banco funciona
        
        retorna:
            bool: True se conectado, False caso contrario
        """
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"[ERRO] falha na conexao: {e}")
            return False


def get_db() -> Generator[Session, None, None]:
    """
    dependency para obter sessao do banco de dados
    
    uso em fastapi:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    
    yields:
        Session: sessao do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

