#!/usr/bin/env python3
# script mestre para setup completo do github project
import subprocess
import sys
from pathlib import Path

def run_script(script_name, description):
    """executa script python e retorna sucesso"""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / script_name)],
            timeout=300  # 5 minutos
        )
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"[erro] timeout ao executar {script_name}")
        return False
    except Exception as e:
        print(f"[erro] excecao ao executar {script_name}: {e}")
        return False

def main():
    """funcao principal"""
    print("="*70)
    print("  SETUP COMPLETO GITHUB PROJECT + SCRUMBAN")
    print("="*70)
    print()
    print("este script vai:")
    print("  1. criar github project v2")
    print("  2. adicionar campos customizados")
    print("  3. adicionar todas as issues")
    print("  4. preencher campos automaticamente")
    print()
    
    input("pressione enter para continuar...")
    
    # passo 1: criar projeto
    if not run_script('create_github_project.py', 'ETAPA 1: CRIAR PROJETO'):
        print("\n❌ erro ao criar projeto")
        print("verifique se:")
        print("  - gh cli esta instalado e autenticado")
        print("  - voce tem permissao para criar projects")
        sys.exit(1)
    
    print("\n✅ projeto criado com sucesso!")
    
    # passo 2: aguardar configuracao manual
    print("\n" + "="*70)
    print("  CONFIGURACAO MANUAL NECESSARIA")
    print("="*70)
    print()
    print("antes de continuar, acesse o projeto e:")
    print("  1. adicionar colunas: Backlog, Review")
    print("  2. configurar wip limit (In Progress: max 3)")
    print("  3. configurar campo Sprint (iterations)")
    print("     - duration: 2 weeks")
    print("     - adicionar: Sprint 1, Sprint 2")
    print()
    
    response = input("configuracao manual concluida? (s/n) [s]: ")
    if response.lower() == 'n':
        print("\npor favor, complete a configuracao manual e execute:")
        print("  python .github/populate_project_fields.py")
        sys.exit(0)
    
    # passo 3: preencher campos
    if not run_script('populate_project_fields.py', 'ETAPA 2: PREENCHER CAMPOS'):
        print("\n❌ erro ao preencher campos")
        print("voce pode tentar novamente executando:")
        print("  python .github/populate_project_fields.py")
        sys.exit(1)
    
    print("\n✅ campos preenchidos com sucesso!")
    
    # sucesso!
    print("\n" + "="*70)
    print("  SETUP COMPLETO!")
    print("="*70)
    print()
    print("seu github project esta pronto:")
    print("  - projeto criado")
    print("  - campos customizados configurados")
    print("  - issues adicionadas")
    print("  - metadados preenchidos")
    print()
    print("proximos passos:")
    print("  1. revisar projeto no github")
    print("  2. editar sprints/sprint-01.md")
    print("  3. iniciar daily standups")
    print("  4. comecar a trabalhar!")
    print()
    print("documentacao:")
    print("  - .github/GITHUB_PROJECTS_SETUP.md")
    print("  - README_SETUP_SCRUMBAN.md")
    print("  - GUIA_RAPIDO_COMANDOS.md")
    print()

if __name__ == "__main__":
    main()

