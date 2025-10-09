#!/usr/bin/env python3
# teste rapido de conexao com banco de dados

import sys
from pathlib import Path

# adicionar app ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import DatabaseConnection


def main():
    """testar conexao e criar tabelas"""
    print("="*60)
    print(" teste de conexao postgresql")
    print("="*60)
    print()
    
    # teste 1: conexao
    print("1. testando conexao...")
    try:
        if DatabaseConnection.check_connection():
            print("   [OK] conectado ao postgresql!")
        else:
            print("   [ERRO] nao foi possivel conectar")
            print()
            print("verifique:")
            print("  - postgresql esta rodando")
            print("  - arquivo .env existe e esta correto")
            print("  - usuario e senha estao corretos")
            print()
            sys.exit(1)
    except Exception as e:
        print(f"   [ERRO] excecao: {e}")
        print()
        print("dica: instale postgresql primeiro")
        print("veja: backend/GUIA_SETUP_WINDOWS.md")
        print()
        sys.exit(1)
    
    print()
    
    # teste 2: criar tabelas
    print("2. criando tabelas...")
    try:
        DatabaseConnection.create_tables()
        print()
        print("[OK] banco de dados pronto!")
        print()
        print("tabelas criadas:")
        print("  - beds (leitos empacotados)")
        print("  - simulations (simulacoes cfd)")
        print("  - results (resultados e metricas)")
        print()
        print("proximos passos:")
        print("  1. cd backend")
        print("  2. uvicorn app.main:app --reload")
        print("  3. abrir http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print(f"   [ERRO] falha ao criar tabelas: {e}")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()

