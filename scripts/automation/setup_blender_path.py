#!/usr/bin/env python3
#Script de Automação para Configurar Blender no PATH
import os
import sys
import subprocess # para executar comandos do sistema
import winreg # para manipular o registro do Windows
import platform 
from pathlib import Path 

class BlenderPathSetup: # classe para configurar o Blender no PATH
    def __init__(self):
        self.system = platform.system()
        self.blender_paths = self.get_blender_paths()
    
    def get_blender_paths(self):
        #retorna possiveis caminhos do Blender por sistema operacional
        if self.system == "Windows":
            return [
                r"C:\Program Files\Blender Foundation\Blender 4.0",
                r"C:\Program Files\Blender Foundation\Blender 3.6",
                r"C:\Program Files\Blender Foundation\Blender 3.5",
                r"C:\Program Files\Blender Foundation\Blender 3.4",
                r"C:\Program Files\Blender Foundation\Blender",
                r"C:\Program Files (x86)\Blender Foundation\Blender",
            ]
        elif self.system == "Linux": # linux 
            return [
                "/usr/bin",
                "/usr/local/bin",
                "/opt/blender",
                "/snap/bin",
            ]
        elif self.system == "Darwin":  # macOS
            return [
                "/Applications/Blender.app/Contents/MacOS",
                "/usr/local/bin",
            ]
        else:
            return []
    
    def find_blender_installation(self): 
        #encontra a instalação do Blender
        print(" Procurando instalacao do Blender...")
        
        # Verificar se blender já está no PATH
        try:
            result = subprocess.run(['blender', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("  Blender ja esta no PATH!")
                return True
        except:
            pass # se nao encontrar, passa
        
        # Procurar em caminhos específicos
        for path in self.blender_paths:
            if self.system == "Windows":
                blender_exe = os.path.join(path, "blender.exe")
            else:
                blender_exe = os.path.join(path, "blender")
            
            if os.path.exists(blender_exe):
                print(f"  Blender encontrado em: {path}")
                return path
        
        print("   Blender nao encontrado nos locais padrao")
        return None
    
    def add_to_path_windows(self, blender_path):
        #adiciona Blender ao PATH no Windows
        try:
            print("🔧 Adicionando Blender ao PATH do sistema...")
            
            # Abrir registro do Windows
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                               0, winreg.KEY_READ | winreg.KEY_WRITE)
            
            # Ler PATH atual
            current_path, _ = winreg.QueryValueEx(key, "Path")
            
            # Verificar se já está no PATH
            if blender_path in current_path:
                print("  Blender ja esta no PATH do sistema")
                winreg.CloseKey(key)
                return True
            
            # Adicionar ao PATH
            new_path = current_path + ";" + blender_path
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            
            print(f"  Blender adicionado ao PATH: {blender_path}")
            return True
            
        except Exception as e:
            print(f"   Erro ao modificar PATH do sistema: {e}")
            print("Execute como administrador para modificar o PATH do sistema")
            return False
    
    def add_to_path_user_windows(self, blender_path):
        #adiciona Blender ao PATH do usuário no Windows
        try:
            print(" Adicionando Blender ao PATH do usuario...")
            
            # Abrir registro do usuário
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Environment", 
                               0, winreg.KEY_READ | winreg.KEY_WRITE)
            
            # Ler PATH atual
            try:
                current_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path = ""
            
            # Verificar se já está no PATH
            if blender_path in current_path:
                print("  Blender ja esta no PATH do usuario")
                winreg.CloseKey(key)
                return True
            
            # Adicionar ao PATH
            if current_path:
                new_path = current_path + ";" + blender_path
            else:
                new_path = blender_path
                
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            
            print(f"  Blender adicionado ao PATH do usuário: {blender_path}")
            return True
            
        except Exception as e:
            print(f"   Erro ao modificar PATH do usuário: {e}")
            return False
    
    def add_to_path_linux_mac(self, blender_path):
        #adiciona Blender ao PATH no Linux/macOS
        try:
            print(" Adicionando Blender ao PATH...")
            
            # Determinar arquivo de perfil
            home = os.path.expanduser("~")
            shell = os.environ.get('SHELL', '/bin/bash')
            
            if 'bash' in shell:
                profile_file = os.path.join(home, '.bashrc')
            elif 'zsh' in shell:
                profile_file = os.path.join(home, '.zshrc')
            else:
                profile_file = os.path.join(home, '.profile')
            
            # Ler arquivo de perfil
            try:
                with open(profile_file, 'r') as f:
                    content = f.read()
            except FileNotFoundError:
                content = ""
            
            # Verificar se já está no PATH
            export_line = f'export PATH="{blender_path}:$PATH"'
            if export_line in content:
                print("  Blender ja esta no PATH")
                return True
            
            # Adicionar ao arquivo de perfil
            with open(profile_file, 'a') as f:
                f.write(f'\n# Blender PATH\n{export_line}\n')
            
            print(f"  Blender adicionado ao PATH: {blender_path}")
            print(f"Modificacao salva em: {profile_file}")
            print("Reinicie o terminal ou execute: source " + profile_file)
            return True
            
        except Exception as e:
            print(f"   Erro ao modificar PATH: {e}")
            return False
    
    def setup_environment_variable(self, blender_path):
        #configura variável de ambiente para a sessão atual
        try:
            # Adicionar ao PATH da sessão atual
            current_path = os.environ.get('PATH', '')
            if blender_path not in current_path:
                os.environ['PATH'] = blender_path + os.pathsep + current_path
                print(f"  Blender adicionado ao PATH da sessão atual: {blender_path}")
            else:
                print("  Blender ja esta no PATH da sessao atual")
            return True
        except Exception as e:
            print(f"   Erro ao configurar variável de ambiente: {e}")
            return False
    
    def verify_installation(self):
        #verifica se a instalação está funcionando
        try:
            result = subprocess.run(['blender', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("  Verificacao: Blender esta funcionando!")
                print(f"   Versao: {result.stdout.split()[1]}")
                return True
            else:
                print("   Verificacao falhou")
                return False
        except Exception as e:
            print(f"   Erro na verificacao: {e}")
            return False
    
    def create_symlink_linux_mac(self, blender_path):
        #cria symlink no Linux/macOS
        if self.system not in ["Linux", "Darwin"]:
            return False
            
        try:
            symlink_path = "/usr/local/bin/blender"
            blender_exe = os.path.join(blender_path, "blender")
            
            if os.path.exists(symlink_path):
                os.remove(symlink_path)
            
            os.symlink(blender_exe, symlink_path)
            print(f"  Symlink criado: {symlink_path} -> {blender_exe}")
            return True
        except Exception as e:
            print(f"   Erro ao criar symlink: {e}")
            return False
    
    def setup(self, force=False):
        #configura o Blender no PATH
        print("    Iniciando configuracao automatica do Blender...")
        print(f"     Sistema operacional: {self.system}")
        
        # Encontrar Blender
        blender_path = self.find_blender_installation()
        if not blender_path:
            print("   Blender nao encontrado. Instale o Blender primeiro.")
            return False
        
        if blender_path is True:  # Já está no PATH
            return True
        
        # Configurar PATH baseado no sistema
        success = False
        
        if self.system == "Windows":
            # Tentar PATH do sistema (requer admin)
            if self.add_to_path_windows(blender_path):
                success = True
            else:
                # Tentar PATH do usuário
                if self.add_to_path_user_windows(blender_path):
                    success = True
                else:
                    # Configurar apenas para a sessão atual
                    success = self.setup_environment_variable(blender_path)
        
        elif self.system in ["Linux", "Darwin"]:
            # Tentar criar symlink (requer sudo)
            if self.create_symlink_linux_mac(blender_path):
                success = True
            else:
                # Adicionar ao arquivo de perfil
                if self.add_to_path_linux_mac(blender_path):
                    success = True
                else:
                    # Configurar apenas para a sessão atual
                    success = self.setup_environment_variable(blender_path)
        
        if success:
            print("\n Configuracao concluida!")
            print("Para aplicar as mudanças:")
            if self.system == "Windows":
                print("   - Reinicie o terminal ou o computador")
            else:
                print("   - Execute: source ~/.bashrc (ou ~/.zshrc)")
            
            # Verificar instalação
            print("\n Verificando instalacao...")
            self.verify_installation()
            
            return True
        else:
            print("\n   Configuracao falhou!")
            print("Tente executar como administrador/sudo")
            return False

def main():
    #funcao principal
    setup = BlenderPathSetup()
    
    # Verificar argumentos
    force = "--force" in sys.argv
    
    if force:
        print("Modo forçado ativado")
    
    # Executar configuração
    success = setup.setup(force=force)
    
    if success:
        print("\n  Configuracao concluida com sucesso!")
        print("    Agora você pode usar o comando 'blender' diretamente")
    else:
        print("\n   Configuracao falhou!")
        print("Verifique se o Blender está instalado e tente novamente")
        sys.exit(1)

if __name__ == "__main__":
    main()
