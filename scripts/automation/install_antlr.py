#!/usr/bin/env python3
# script de instalacao automatica do antlr e java
import os
import sys
import subprocess
import platform
import urllib.request
from pathlib import Path

class ANTLRInstaller:
    """classe para instalar antlr e suas dependencias"""
    
    def __init__(self):
        self.system = platform.system()
        self.antlr_version = "4.13.1"
        self.java_version = "17"
        self.project_root = Path(__file__).parent.parent.parent
        self.dsl_dir = self.project_root / "dsl"
        
    def check_java(self):
        """verifica se java esta instalado"""
        print("\n[1/5] verificando java...")
        
        java_paths = []
        
        if self.system == "Windows":
            # caminhos comuns do java no windows
            java_paths = [
                r"C:\Program Files\Microsoft\jdk-17.0.16.8-hotspot\bin\java.exe",
                r"C:\Program Files\Java\jdk-17\bin\java.exe",
                r"C:\Program Files\Java\jre-17\bin\java.exe",
                r"C:\Program Files (x86)\Java\jdk-17\bin\java.exe",
            ]
        
        # tentar comando java no path
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version_line = result.stderr.split('\n')[0]
                print(f"[ok] {version_line}")
                return True
                
        except FileNotFoundError:
            pass
        
        # tentar caminhos especificos
        for java_path in java_paths:
            if os.path.exists(java_path):
                print(f"[ok] java encontrado em {java_path}")
                return True
        
        print("[aviso] java nao encontrado")
        return False
    
    def install_java_windows(self):
        """instala java no windows usando winget"""
        print("\n[2/5] instalando java no windows...")
        
        try:
            # tentar instalar com winget
            result = subprocess.run(
                ["winget", "install", "Microsoft.OpenJDK.17"],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                print("[ok] java instalado via winget")
                return True
            else:
                print("[aviso] falha ao instalar via winget")
                return False
                
        except FileNotFoundError:
            print("[aviso] winget nao encontrado")
            return False
        except Exception as e:
            print(f"[erro] erro na instalacao: {e}")
            return False
    
    def install_java_linux(self):
        """instala java no linux"""
        print("\n[2/5] instalando java no linux...")
        
        package_managers = [
            (["sudo", "apt", "install", "-y", f"openjdk-{self.java_version}-jdk"], "apt"),
            (["sudo", "dnf", "install", "-y", f"java-{self.java_version}-openjdk"], "dnf"),
            (["sudo", "yum", "install", "-y", f"java-{self.java_version}-openjdk"], "yum"),
            (["sudo", "pacman", "-S", "--noconfirm", f"jdk{self.java_version}-openjdk"], "pacman"),
        ]
        
        for cmd, manager in package_managers:
            try:
                print(f"  tentando com {manager}...")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    print(f"[ok] java instalado via {manager}")
                    return True
                    
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"  erro com {manager}: {e}")
                continue
        
        print("[erro] nenhum gerenciador de pacotes funcionou")
        return False
    
    def install_java_macos(self):
        """instala java no macos"""
        print("\n[2/5] instalando java no macos...")
        
        try:
            result = subprocess.run(
                ["brew", "install", f"openjdk@{self.java_version}"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("[ok] java instalado via homebrew")
                return True
            else:
                print("[aviso] falha ao instalar via homebrew")
                return False
                
        except FileNotFoundError:
            print("[aviso] homebrew nao encontrado")
            return False
        except Exception as e:
            print(f"[erro] erro na instalacao: {e}")
            return False
    
    def download_antlr(self):
        """baixa o arquivo jar do antlr"""
        print(f"\n[3/5] baixando antlr {self.antlr_version}...")
        
        antlr_jar = self.dsl_dir / f"antlr-{self.antlr_version}-complete.jar"
        
        # verificar se ja existe
        if antlr_jar.exists():
            print(f"[ok] antlr ja existe: {antlr_jar}")
            return True
        
        # criar diretorio dsl se nao existir
        self.dsl_dir.mkdir(parents=True, exist_ok=True)
        
        # url de download
        url = f"https://www.antlr.org/download/antlr-{self.antlr_version}-complete.jar"
        
        try:
            print(f"  baixando de: {url}")
            urllib.request.urlretrieve(url, antlr_jar)
            
            if antlr_jar.exists():
                size_mb = antlr_jar.stat().st_size / (1024 * 1024)
                print(f"[ok] antlr baixado: {size_mb:.2f} mb")
                return True
            else:
                print("[erro] arquivo nao foi criado")
                return False
                
        except Exception as e:
            print(f"[erro] falha no download: {e}")
            return False
    
    def generate_parser(self):
        """gera parser a partir da gramatica"""
        print("\n[4/5] gerando parser a partir da gramatica...")
        
        grammar_file = self.dsl_dir / "grammar" / "Bed.g4"
        output_dir = self.dsl_dir / "generated"
        antlr_jar = self.dsl_dir / f"antlr-{self.antlr_version}-complete.jar"
        
        # verificar se gramatica existe
        if not grammar_file.exists():
            print(f"[erro] gramatica nao encontrada: {grammar_file}")
            return False
        
        # criar diretorio de saida
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # encontrar java
        java_cmd = "java"
        
        if self.system == "Windows":
            java_paths = [
                r"C:\Program Files\Microsoft\jdk-17.0.16.8-hotspot\bin\java.exe",
                r"C:\Program Files\Java\jdk-17\bin\java.exe",
            ]
            
            for path in java_paths:
                if os.path.exists(path):
                    java_cmd = path
                    break
        
        # executar antlr
        cmd = [
            java_cmd,
            "-jar", str(antlr_jar),
            "-Dlanguage=Python3",
            "-o", str(output_dir),
            str(grammar_file)
        ]
        
        try:
            print(f"  gerando parser...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("[ok] parser gerado com sucesso")
                
                # listar arquivos gerados
                generated_files = list(output_dir.glob("*.py"))
                print(f"  arquivos gerados: {len(generated_files)}")
                for f in generated_files:
                    print(f"    - {f.name}")
                
                return True
            else:
                print(f"[erro] falha ao gerar parser:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"[erro] erro ao executar antlr: {e}")
            return False
    
    def test_parser(self):
        """testa o parser gerado"""
        print("\n[5/5] testando parser...")
        
        # verificar se arquivos foram gerados
        output_dir = self.dsl_dir / "generated"
        required_files = [
            "BedLexer.py",
            "BedParser.py",
            "BedListener.py"
        ]
        
        all_exist = True
        for filename in required_files:
            filepath = output_dir / filename
            if filepath.exists():
                print(f"[ok] {filename} encontrado")
            else:
                print(f"[erro] {filename} nao encontrado")
                all_exist = False
        
        return all_exist
    
    def create_alias(self):
        """cria alias para antlr"""
        print("\n[extra] criando alias antlr...")
        
        antlr_jar = self.dsl_dir / f"antlr-{self.antlr_version}-complete.jar"
        
        if self.system == "Windows":
            # criar arquivo bat
            bat_content = f'@echo off\njava -jar "{antlr_jar}" %*'
            bat_file = self.dsl_dir / "antlr.bat"
            
            with open(bat_file, 'w') as f:
                f.write(bat_content)
            
            print(f"[ok] alias criado: {bat_file}")
            print(f"  use: {bat_file} [opcoes]")
            
        else:
            # criar script shell
            sh_content = f'#!/bin/bash\njava -jar "{antlr_jar}" "$@"'
            sh_file = self.dsl_dir / "antlr.sh"
            
            with open(sh_file, 'w') as f:
                f.write(sh_content)
            
            os.chmod(sh_file, 0o755)
            
            print(f"[ok] alias criado: {sh_file}")
            print(f"  use: {sh_file} [opcoes]")
    
    def install(self):
        """executa instalacao completa"""
        print("="*60)
        print("  instalador automatico antlr + java")
        print("="*60)
        print(f"sistema: {self.system}")
        print(f"antlr version: {self.antlr_version}")
        print(f"java version: {self.java_version}")
        
        # verificar java
        java_ok = self.check_java()
        
        if not java_ok:
            print("\n[atencao] java nao encontrado, instalando...")
            
            if self.system == "Windows":
                if not self.install_java_windows():
                    print("[erro] falha ao instalar java")
                    print("instale manualmente de: https://adoptium.net/")
                    return False
                    
            elif self.system == "Linux":
                if not self.install_java_linux():
                    print("[erro] falha ao instalar java")
                    return False
                    
            elif self.system == "Darwin":
                if not self.install_java_macos():
                    print("[erro] falha ao instalar java")
                    return False
            
            # verificar novamente
            if not self.check_java():
                print("[erro] java ainda nao encontrado apos instalacao")
                return False
        
        # baixar antlr
        if not self.download_antlr():
            print("[erro] falha ao baixar antlr")
            return False
        
        # gerar parser
        if not self.generate_parser():
            print("[erro] falha ao gerar parser")
            return False
        
        # testar parser
        if not self.test_parser():
            print("[aviso] alguns arquivos nao foram gerados")
        
        # criar alias
        self.create_alias()
        
        print("\n" + "="*60)
        print("  instalacao concluida!")
        print("="*60)
        
        return True
    
    def print_next_steps(self):
        """imprime proximos passos"""
        print("\nproximos passos:")
        print("1. testar compilador: python dsl/compiler/bed_compiler_antlr_standalone.py dsl/examples/leito.bed")
        print("2. usar wizard: python dsl/bed_wizard.py")
        print("3. modificar gramatica: editar dsl/grammar/Bed.g4")
        print("4. regerar parser: python scripts/automation/install_antlr.py")

def main():
    """funcao principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='instalador automatico antlr')
    parser.add_argument('--antlr-version', type=str, default='4.13.1',
                       help='versao do antlr (padrao: 4.13.1)')
    parser.add_argument('--java-version', type=str, default='17',
                       help='versao do java (padrao: 17)')
    
    args = parser.parse_args()
    
    # criar instalador
    installer = ANTLRInstaller()
    installer.antlr_version = args.antlr_version
    installer.java_version = args.java_version
    
    # executar instalacao
    success = installer.install()
    
    if success:
        print("\n[sucesso] antlr instalado e pronto para usar!")
        installer.print_next_steps()
    else:
        print("\n[erro] instalacao falhou")
        print("verifique os logs acima para detalhes")
        sys.exit(1)

if __name__ == "__main__":
    main()

