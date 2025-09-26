#!/usr/bin/env python3
"""
script direto para executar leito_extracao.py no blender headless
versao simplificada sem verificacoes extensas
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """executar leito_extracao.py no blender headless"""
    
    print("executando leito_extracao.py no blender headless...")
    
    # caminhos
    script_dir = Path(__file__).parent
    projeto_dir = script_dir.parent.parent
    leito_script = projeto_dir / "scripts" / "blender_scripts" / "leito_extracao.py"
    
    # verificar se script existe
    if not leito_script.exists():
        print(f"erro: script nao encontrado: {leito_script}")
        return
    
    # comando blender
    comando = [
        "blender",
        "--background",
        "--python", str(leito_script)
    ]
    
    print(f"executando: {' '.join(comando)}")
    
    try:
        # executar
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=300)
        
        if resultado.returncode == 0:
            print("sucesso!")
            print("saida:", resultado.stdout)
        else:
            print("erro!")
            print("erro:", resultado.stderr)
            
    except subprocess.TimeoutExpired:
        print("timeout")
    except FileNotFoundError:
        print("blender nao encontrado no path")
        print("instale o blender ou adicione ao path")

if __name__ == "__main__":
    main()
