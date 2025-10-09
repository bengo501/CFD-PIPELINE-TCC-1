#!/usr/bin/env python3
# script para inicializar banco de dados

import sys
from pathlib import Path

# adicionar parent directory ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import DatabaseConnection


def main():
    """criar tabelas no banco de dados"""
    print("="*60)
    print(" inicializando banco de dados postgresql")
    print("="*60)
    print()
    
    # verificar conexao
    print("1. verificando conexao...")
    if not DatabaseConnection.check_connection():
        print()
        print("[ERRO] nao foi possivel conectar ao banco")
        print()
        print("verifique:")
        print("  - postgresql esta rodando")
        print("  - DATABASE_URL no arquivo .env esta correto")
        print("  - usuario e senha estao corretos")
        print()
        sys.exit(1)
    
    print("   [OK] conectado ao banco de dados")
    print()
    
    # criar tabelas
    print("2. criando tabelas...")
    try:
        DatabaseConnection.create_tables()
        print()
        print("[OK] tabelas criadas com sucesso!")
        print()
        print("tabelas criadas:")
        print("  - beds (leitos empacotados)")
        print("  - simulations (simulacoes cfd)")
        print("  - results (resultados e metricas)")
        print()
        print("proximos passos:")
        print("  1. iniciar api: uvicorn app.main:app --reload")
        print("  2. testar endpoints: http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print()
        print(f"[ERRO] falha ao criar tabelas: {e}")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()

