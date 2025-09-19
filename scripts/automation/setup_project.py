#!/usr/bin/env python3
"""
Script de Automação Completa para Configurar o Projeto
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class ProjectSetup:
    def __init__(self):
        self.system = platform.system()
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
    
    def check_python_version(self):
        """Verifica a versão do Python"""
        print(" Verificando versão do Python...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 6):
            print(f"  Python {version.major}.{version.minor} não é suportado")
            print(" Requer Python 3.6 ou superior")
            return False
        
        print(f"   Python {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_blender_installation(self):
        """Verifica se o Blender está instalado"""
        print("  Verificando instalação do Blender...")
        
        try:
            result = subprocess.run(['blender', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.split()[1]
                print(f"   Blender {version} encontrado")
                return True
        except:
            pass
        
        print("  Blender não encontrado no PATH")
        return False
    
    def install_blender(self):
        """Instala o Blender automaticamente"""
        print(" Instalando Blender...")
        
        try:
            # Importar e executar o instalador
            sys.path.append(str(self.scripts_dir))
            from install_blender import BlenderInstaller
            
            installer = BlenderInstaller()
            success = installer.install()
            
            if success:
                print("   Blender instalado com sucesso")
                return True
            else:
                print("  Falha na instalação do Blender")
                return False
                
        except Exception as e:
            print(f"  Erro na instalação: {e}")
            return False
    
    def setup_blender_path(self):
        """Configura o Blender no PATH"""
        print(" Configurando Blender no PATH...")
        
        try:
            # Importar e executar o setup do PATH
            sys.path.append(str(self.scripts_dir))
            from setup_blender_path import BlenderPathSetup
            
            setup = BlenderPathSetup()
            success = setup.setup()
            
            if success:
                print("   Blender configurado no PATH")
                return True
            else:
                print("  Falha na configuração do PATH")
                return False
                
        except Exception as e:
            print(f"  Erro na configuração: {e}")
            return False
    
    def test_blender_script(self):
        """Testa o script standalone do Blender"""
        print("  Testando script standalone...")
        
        try:
            result = subprocess.run([
                sys.executable, 
                str(self.scripts_dir / "leito_standalone.py"),
                "--help"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("   Script standalone funcionando")
                return True
            else:
                print("  Script standalone com problemas")
                return False
                
        except Exception as e:
            print(f"  Erro no teste: {e}")
            return False
    
    def create_directories(self):
        """Cria diretórios necessários"""
        print(" Criando diretórios do projeto...")
        
        directories = [
            "models",
            "exports", 
            "docs",
            "temp"
        ]
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"   Diretório criado: {dir_name}")
    
    def create_config_file(self):
        """Cria arquivo de configuração"""
        print("  Criando arquivo de configuração...")
        
        config_content = '''# Configuração do Projeto TCC
# Arquivo gerado automaticamente

[BLENDER]
# Caminho do Blender (será detectado automaticamente)
path = auto

[PROJECT]
# Diretórios do projeto
models_dir = models/
exports_dir = exports/
temp_dir = temp/

[DEFAULT_PARAMS]
# Parâmetros padrão para geração de leitos
altura = 0.1
diametro = 0.025
espessura_parede = 0.002
num_particulas = 30
tamanho_particula = 0.001
massa_particula = 0.1
tipo_particula = esferas
cor_leito = azul
cor_particulas = verde
'''
        
        config_file = self.project_root / "config.ini"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print("   Arquivo de configuração criado: config.ini")
    
    def run_tests(self):
        """Executa testes básicos"""
        print("  Executando testes básicos...")
        
        tests = [
            ("Teste do Blender", self.check_blender_installation),
            ("Teste do Script Standalone", self.test_blender_script),
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            print(f"\n  {test_name}...")
            if test_func():
                print(f"   {test_name} passou")
            else:
                print(f"  {test_name} falhou")
                all_passed = False
        
        return all_passed
    
    def generate_sample(self):
        """Gera um exemplo de leito"""
        print(" Gerando exemplo de leito...")
        
        try:
            result = subprocess.run([
                sys.executable,
                str(self.scripts_dir / "leito_standalone.py"),
                "--altura", "0.1",
                "--diametro", "0.025", 
                "--num-particulas", "10",
                "--output", str(self.project_root / "models" / "exemplo.blend")
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("   Exemplo gerado com sucesso")
                return True
            else:
                print("  Falha na geração do exemplo")
                return False
                
        except Exception as e:
            print(f"  Erro na geração: {e}")
            return False
    
    def setup(self, auto_install=True, run_tests=True, generate_sample=True):
        """Configura o projeto completo"""
        print(" Iniciando configuração automática do projeto...")
        print(f"  Sistema: {self.system}")
        print(f" Diretório do projeto: {self.project_root}")
        
        # Verificar Python
        if not self.check_python_version():
            return False
        
        # Criar diretórios
        self.create_directories()
        
        # Verificar Blender
        blender_ok = self.check_blender_installation()
        
        if not blender_ok and auto_install:
            print("\n   Blender não encontrado. Instalando automaticamente...")
            if not self.install_blender():
                print("  Falha na instalação automática do Blender")
                print(" Instale manualmente e execute novamente")
                return False
        
        # Configurar PATH
        if not blender_ok:
            if not self.setup_blender_path():
                print("  Falha na configuração do PATH")
                return False
        
        # Criar arquivo de configuração
        self.create_config_file()
        
        # Executar testes
        if run_tests:
            if not self.run_tests():
                print("  Alguns testes falharam")
                return False
        
        # Gerar exemplo
        if generate_sample:
            self.generate_sample()
        
        print("\n Configuração concluída com sucesso!")
        print("\n Resumo:")
        print("   Python verificado")
        print("   Diretórios criados")
        print("   Blender configurado")
        print("   Scripts testados")
        print("   Arquivo de configuração criado")
        
        print("\n Próximos passos:")
        print("1. Teste: blender --version")
        print("2. Gere um leito: python scripts/leito_standalone.py")
        print("3. Veja exemplos: python scripts/exemplo_uso_standalone.py")
        
        return True

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Configurador Automático do Projeto')
    parser.add_argument('--no-auto-install', action='store_true',
                       help='Não instalar Blender automaticamente')
    parser.add_argument('--no-tests', action='store_true',
                       help='Não executar testes')
    parser.add_argument('--no-sample', action='store_true',
                       help='Não gerar exemplo')
    parser.add_argument('--force', action='store_true',
                       help='Forçar configuração mesmo com erros')
    
    args = parser.parse_args()
    
    # Criar setup
    setup = ProjectSetup()
    
    # Executar configuração
    success = setup.setup(
        auto_install=not args.no_auto_install,
        run_tests=not args.no_tests,
        generate_sample=not args.no_sample
    )
    
    if success:
        print("\n   Projeto configurado com sucesso!")
        print(" Pronto para usar!")
    else:
        print("\n  Configuração falhou!")
        if not args.force:
            sys.exit(1)

if __name__ == "__main__":
    main()
