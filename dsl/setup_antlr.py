#!/usr/bin/env python3
"""
script para configurar antlr e gerar parser da gramatica bed.g4
"""

import subprocess
import sys
from pathlib import Path

def install_antlr():
    """instala antlr4 python runtime"""
    try:
        import antlr4
        print("antlr4-python3-runtime ja instalado")
        return True
    except ImportError:
        print("instalando antlr4-python3-runtime...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "antlr4-python3-runtime"])
            print("antlr4-python3-runtime instalado com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            print(f"erro ao instalar antlr4: {e}")
            return False

def download_antlr_jar():
    """baixa antlr jar se necessario"""
    antlr_jar = Path("antlr-4.13.1-complete.jar")
    
    if antlr_jar.exists():
        print(f"antlr jar ja existe: {antlr_jar}")
        return str(antlr_jar)
    
    print("baixando antlr jar...")
    try:
        import urllib.request
        url = "https://www.antlr.org/download/antlr-4.13.1-complete.jar"
        urllib.request.urlretrieve(url, str(antlr_jar))
        print(f"antlr jar baixado: {antlr_jar}")
        return str(antlr_jar)
    except Exception as e:
        print(f"erro ao baixar antlr jar: {e}")
        print("baixe manualmente de: https://www.antlr.org/download/")
        return None

def generate_parser():
    """gera parser python da gramatica bed.g4"""
    grammar_file = Path("grammar/Bed.g4")
    output_dir = Path("generated")
    
    if not grammar_file.exists():
        print(f"erro: arquivo gramatica nao encontrado: {grammar_file}")
        return False
    
    # criar diretorio de saida
    output_dir.mkdir(exist_ok=True)
    
    # tentar usar antlr jar
    antlr_jar = download_antlr_jar()
    if not antlr_jar:
        print("erro: nao foi possivel obter antlr jar")
        return False
    
    # gerar parser
    try:
        cmd = [
            "java", "-jar", antlr_jar,
            "-Dlanguage=Python3",
            "-o", str(output_dir),
            str(grammar_file)
        ]
        
        print(f"executando: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        print("parser gerado com sucesso!")
        
        # criar __init__.py
        init_file = output_dir / "__init__.py"
        init_file.write_text("# generated antlr parser\n")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"erro ao gerar parser: {e}")
        print("certifique-se de ter java instalado")
        return False
    except FileNotFoundError:
        print("erro: java nao encontrado")
        print("instale java jdk/jre para usar antlr")
        return False

def main():
    """funcao principal"""
    print("=== configuracao antlr para dsl .bed ===")
    
    # instalar runtime python
    if not install_antlr():
        return 1
    
    # gerar parser
    if not generate_parser():
        return 1
    
    print("\n=== configuracao concluida ===")
    print("agora voce pode usar o parser antlr gerado!")
    print("arquivos gerados em: generated/")
    
    return 0

if __name__ == "__main__":
    exit(main())
