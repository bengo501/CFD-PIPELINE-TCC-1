#!/usr/bin/env python3
# script de instalacao automatica do blender
import os
import sys
import subprocess # para executar comandos do sistema
import platform # para verificar o sistema operacional
import urllib.request
import zipfile # para extrair arquivos ZIP
import tarfile # para extrair arquivos TAR
from pathlib import Path

class BlenderInstaller: 
    # classe para instalar o blender
    def __init__(self):
        self.system = platform.system()
        self.architecture = platform.machine()
        self.blender_version = "4.0.2"  # versao padrao do blender
        self.install_dir = self.get_install_directory()
    
    def get_install_directory(self):
        #retorna o diretorio de instalacao baseado no sistema
        if self.system == "Windows":
            return r"C:\Program Files\Blender Foundation"
        elif self.system == "Linux":
            return "/opt/blender"
        elif self.system == "Darwin":  # macOS
            return "/Applications"
        else:
            return "/usr/local/blender"
    
    def get_download_url(self):
        #retorna a URL de download do Blender
        base_url = "https://download.blender.org/release/Blender"
        
        if self.system == "Windows":
            if self.architecture == "AMD64":
                return f"{base_url}{self.blender_version}/blender-{self.blender_version}-windows-x64.zip"
            else:
                return f"{base_url}{self.blender_version}/blender-{self.blender_version}-windows-x86.zip"
        
        elif self.system == "Linux":
            if self.architecture == "x86_64":
                return f"{base_url}{self.blender_version}/blender-{self.blender_version}-linux-x64.tar.xz"
            else:
                return f"{base_url}{self.blender_version}/blender-{self.blender_version}-linux-x86.tar.xz"
        
        elif self.system == "Darwin":  # macOS
            if self.architecture == "arm64":
                return f"{base_url}{self.blender_version}/blender-{self.blender_version}-macos-arm64.dmg"
            else:
                return f"{base_url}{self.blender_version}/blender-{self.blender_version}-macos-x64.dmg"
        
        return None
    
    def download_file(self, url, filename):
        #baixa um arquivo da URL especificada
        print(f" Baixando Blender de: {url}")
        
        try:
            urllib.request.urlretrieve(url, filename)
            print(f"   Download concluído: {filename}")
            return True
        except Exception as e:
            print(f"   Erro no download: {e}")
            return False
    
    def extract_windows(self, filename):
        #extrai arquivo ZIP no Windows
        try:
            print("   Extraindo arquivo...")
            
            # Criar diretório de instalação
            os.makedirs(self.install_dir, exist_ok=True)
            
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(self.install_dir)
            
            print("   Extração concluída")
            return True
        except Exception as e:
            print(f"   Erro na extração: {e}")
            return False
    
    def extract_linux(self, filename):
        #extrai arquivo TAR no Linux
        try:
            print("   Extraindo arquivo...")
            
            # Criar diretório de instalação
            os.makedirs(self.install_dir, exist_ok=True)
            
            with tarfile.open(filename, 'r:xz') as tar_ref:
                tar_ref.extractall(self.install_dir)
            
            print("   Extração concluída")
            return True
        except Exception as e:
            print(f"   Erro na extração: {e}")
            return False
    
    def install_windows(self):
        #instala Blender no Windows
        url = self.get_download_url()
        if not url:
            print("   URL de download não suportada")
            return False
        
        filename = f"blender-{self.blender_version}-windows.zip"
        
        # Download
        if not self.download_file(url, filename):
            return False
        
        # Extração
        if not self.extract_windows(filename):
            return False
        
        # Limpar arquivo temporário
        os.remove(filename)
        
        print(f"   Blender instalado em: {self.install_dir}")
        return True
    
    def install_linux(self):
        #instala Blender no Linux
        url = self.get_download_url()
        if not url:
            print("   URL de download não suportada")
            return False
        
        filename = f"blender-{self.blender_version}-linux.tar.xz"
        
        # Download
        if not self.download_file(url, filename):
            return False
        
        # Extração
        if not self.extract_linux(filename):
            return False
        
        # Criar symlink
        try:
            blender_dir = None
            for item in os.listdir(self.install_dir):
                if item.startswith("blender-"):
                    blender_dir = os.path.join(self.install_dir, item)
                    break
            
            if blender_dir:
                symlink_path = "/usr/local/bin/blender"
                blender_exe = os.path.join(blender_dir, "blender")
                
                if os.path.exists(symlink_path):
                    os.remove(symlink_path)
                
                os.symlink(blender_exe, symlink_path)
                print(f"   Symlink criado: {symlink_path}")
        except Exception as e:
            print(f"  Aviso: Não foi possível criar symlink: {e}")

        # Limpar arquivo temporário
        os.remove(filename)
        
        print(f"   Blender instalado em: {self.install_dir}")
        return True
    
    def install_macos(self):
        #instala Blender no macOS
        print(" Instalação no macOS requer download manual")
        print(" Baixe o DMG de: https://www.blender.org/download/")
        return False
    
    def install_system_package(self):
        #instala Blender usando gerenciador de pacotes do sistema
        try:
            if self.system == "Linux":
                # Tentar diferentes gerenciadores de pacotes
                package_managers = [
                    ("apt", "blender"),
                    ("dnf", "blender"),
                    ("yum", "blender"),
                    ("pacman", "blender"),
                    ("zypper", "blender"),
                ]
                
                for manager, package in package_managers:
                    try:
                        print(f"   Tentando instalar com {manager}...")
                        result = subprocess.run([manager, "install", "-y", package], 
                                              capture_output=True, text=True, timeout=300)
                        if result.returncode == 0:
                            print(f"   Blender instalado com {manager}")
                            return True
                    except FileNotFoundError:
                        continue
                
                print("   Nenhum gerenciador de pacotes encontrado")
                return False
            
            elif self.system == "Darwin":  # macOS
                try:
                    print("   Tentando instalar com Homebrew...")
                    result = subprocess.run(["brew", "install", "blender"], 
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        print("   Blender instalado com Homebrew")
                        return True
                except FileNotFoundError:
                    print("   Homebrew não encontrado")
                    return False
            
            return False
            
        except Exception as e:
            print(f"   Erro na instalação do sistema: {e}")
            return False
    
    def verify_installation(self):
        #verifica se a instalação foi bem-sucedida
        try:
            result = subprocess.run(['blender', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("   Verificação: Blender está funcionando!")
                print(f" Versão: {result.stdout.split()[1]}")
                return True
            else:
                print("   Verificação falhou")
                return False
        except Exception as e:
            print(f"   Erro na verificação: {e}")
            return False
    
    def install(self, use_system_package=True):
        #instala o Blender
        print(" Iniciando instalação automática do Blender...")
        print(f"  Sistema: {self.system}")
        print(f"  Arquitetura: {self.architecture}")
        print(f"   Versão: {self.blender_version}")
        
        # Verificar se já está instalado
        try:
            result = subprocess.run(['blender', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   Blender já está instalado!")
                return True
        except:
            pass
        
        # Tentar instalação do sistema primeiro
        if use_system_package:
            print("   Tentando instalação via gerenciador de pacotes...")
            if self.install_system_package():
                return True
        
        # Instalação manual baseada no sistema
        if self.system == "Windows":
            return self.install_windows()
        elif self.system == "Linux":
            return self.install_linux()
        elif self.system == "Darwin":
            return self.install_macos()
        else:
            print(f"   Sistema não suportado: {self.system}")
            return False

def main():
    #funcao principal
    import argparse
    
    parser = argparse.ArgumentParser(description='Instalador Automático do Blender')
    parser.add_argument('--version', type=str, default='4.0.2', 
                       help='Versão do Blender para instalar')
    parser.add_argument('--no-system-package', action='store_true',
                       help='Não usar gerenciador de pacotes do sistema')
    parser.add_argument('--install-dir', type=str,
                       help='Diretório de instalação personalizado')
    
    args = parser.parse_args()
    
    # Criar instalador
    installer = BlenderInstaller()
    installer.blender_version = args.version
    
    if args.install_dir:
        installer.install_dir = args.install_dir
    
    # Executar instalação
    success = installer.install(use_system_package=not args.no_system_package)
    
    if success:
        print("\n Instalação concluída com sucesso!")
        
        # Verificar instalação
        print("\n    Verificando instalação...")
        installer.verify_installation()

        print("\n Próximos passos:")
        print("1. Execute: python scripts/setup_blender_path.py")
        print("2. Teste: blender --version")
        print("3. Use: python scripts/leito_standalone.py")
        
    else:
        print("\n   Instalação falhou!")
        print(" Tente instalar manualmente ou verifique os logs")
        sys.exit(1)

if __name__ == "__main__":
    main()
