#!/usr/bin/env python3
"""
script para executar leito_extracao.py no blender de forma headless
executa o script de criacao de leito sem interface grafica
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def encontrar_blender():
    """encontrar instalacao do blender no sistema"""
    # caminhos comuns do blender no windows (versoes mais recentes)
    caminhos_windows = [
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.4\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.3\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 2.93\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 2.92\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 2.91\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 2.90\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 2.83\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 2.82\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 2.81\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 2.80\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender\blender.exe",
        r"C:\Program Files\Blender Foundation\blender.exe",
        r"C:\Program Files\Blender\blender.exe",
        r"C:\Program Files\blender.exe",
        r"C:\blender.exe",
        r"blender.exe"
    ]
    
    # verificar se blender esta no path
    try:
        result = subprocess.run(['blender', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return 'blender'
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # procurar nos caminhos do windows
    for caminho in caminhos_windows:
        if os.path.exists(caminho):
            return caminho
    
    return None

def executar_leito_headless():
    """executar leito_extracao.py no blender de forma headless"""
    
    print("=" * 60)
    print("  EXECUTOR DE LEITO HEADLESS")
    print("=" * 60)
    print()
    
    # encontrar blender
    print("procurando instalacao do blender...")
    blender_path = encontrar_blender()
    
    if not blender_path:
        print("erro: blender nao encontrado!")
        print("instale o blender ou adicione ao path do sistema")
        return False
    
    print(f"blender encontrado: {blender_path}")
    
    # caminhos dos arquivos
    script_dir = Path(__file__).parent
    projeto_dir = script_dir.parent.parent
    leito_script = projeto_dir / "scripts" / "blender_scripts" / "leito_extracao.py"
    
    # verificar se o script existe
    if not leito_script.exists():
        print(f"erro: script nao encontrado: {leito_script}")
        return False
    
    print(f"script encontrado: {leito_script}")
    
    # comando para executar
    comando = [
        blender_path,
        "--background",  # modo headless
        "--python", str(leito_script)  # executar script python
    ]
    
    print()
    print("executando comando:")
    print(" ".join(comando))
    print()
    
    try:
        # executar comando
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=300  # timeout de 5 minutos
        )
        
        # verificar resultado
        if resultado.returncode == 0:
            print("execucao bem-sucedida!")
            print()
            print("saida do blender:")
            print("-" * 40)
            print(resultado.stdout)
            print("-" * 40)
            
            if resultado.stderr:
                print("avisos/erros:")
                print(resultado.stderr)
            
            return True
        else:
            print("erro na execucao!")
            print(f"codigo de retorno: {resultado.returncode}")
            print()
            print("erro:")
            print(resultado.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("timeout: execucao demorou mais que 5 minutos")
        return False
    except Exception as e:
        print(f"erro inesperado: {e}")
        return False

def main():
    """funcao principal"""
    sucesso = executar_leito_headless()
    
    if sucesso:
        print()
        print("leito criado com sucesso!")
        print("o arquivo .blend foi salvo no diretorio atual")
    else:
        print()
        print("falha na criacao do leito")
        print("verifique os erros acima")

if __name__ == "__main__":
    main()
