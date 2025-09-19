# 🤖 Scripts de Automação

Esta pasta contém scripts para automatizar a configuração, instalação e setup do projeto.

## 📁 Arquivos

### 🚀 **setup_project.py**
- **Descrição**: Script principal de configuração automática do projeto
- **Funcionalidades**:
  - Verificação de dependências (Python, Blender)
  - Criação automática de diretórios
  - Configuração do Blender no PATH
  - Execução de testes básicos
  - Geração de arquivo de configuração
  - Geração de exemplo de leito

### 🔧 **setup_blender_path.py**
- **Descrição**: Configuração automática do Blender no PATH
- **Funcionalidades**:
  - Detecção automática do Blender
  - Adição ao PATH do sistema/usuário
  - Suporte Windows, Linux, macOS
  - Verificação de instalação
  - Criação de symlinks (Linux/macOS)

### 📦 **install_blender.py**
- **Descrição**: Instalação automática do Blender
- **Funcionalidades**:
  - Download automático do Blender
  - Instalação via gerenciadores de pacotes
  - Extração e configuração
  - Criação de symlinks
  - Verificação de instalação

### 🪟 **setup_windows.bat**
- **Descrição**: Script de setup para Windows
- **Funcionalidades**:
  - Verificação do Python
  - Configuração do Blender
  - Criação de diretórios
  - Execução de testes
  - Interface amigável

### 🐧 **setup_unix.sh**
- **Descrição**: Script de setup para Linux/macOS
- **Funcionalidades**:
  - Detecção automática do Python
  - Configuração do Blender
  - Criação de diretórios
  - Testes automatizados
  - Output colorido

## 🚀 Como Usar

### Setup Completo (Recomendado):
```bash
# Windows
scripts\automation\setup_windows.bat

# Linux/macOS
chmod +x scripts/automation/setup_unix.sh
./scripts/automation/setup_unix.sh

# Python (qualquer sistema)
python scripts/automation/setup_project.py
```

### Configuração Individual:
```bash
# Apenas configurar PATH do Blender
python scripts/automation/setup_blender_path.py

# Apenas instalar Blender
python scripts/automation/install_blender.py

# Setup do projeto sem instalar Blender
python scripts/automation/setup_project.py --no-auto-install
```

### Opções do Setup:
```bash
# Setup sem testes
python scripts/automation/setup_project.py --no-tests

# Setup sem gerar exemplo
python scripts/automation/setup_project.py --no-sample

# Setup forçado
python scripts/automation/setup_project.py --force
```

## 🔧 Funcionalidades

### Detecção Automática:
- ✅ Sistema operacional
- ✅ Versão do Python
- ✅ Instalação do Blender
- ✅ Caminhos de instalação

### Configuração:
- ✅ PATH do sistema/usuário
- ✅ Diretórios do projeto
- ✅ Arquivo de configuração
- ✅ Variáveis de ambiente

### Instalação:
- ✅ Gerenciadores de pacotes (apt, dnf, yum, pacman, brew)
- ✅ Download direto
- ✅ Extração automática
- ✅ Criação de symlinks

### Testes:
- ✅ Verificação do Python
- ✅ Verificação do Blender
- ✅ Teste de scripts
- ✅ Geração de exemplo

## 📋 Requisitos

### Para Windows:
- **Python** 3.6 ou superior
- **Permissões** de administrador (opcional)

### Para Linux/macOS:
- **Python** 3.6 ou superior
- **Permissões** sudo (opcional)
- **Shell** bash ou zsh

### Para Todos:
- **Internet** para download do Blender
- **Espaço em disco** para instalação

## 🎯 Casos de Uso

### Desenvolvimento:
- Setup rápido do ambiente
- Configuração de novos desenvolvedores
- Padronização do ambiente

### CI/CD:
- Automação de build
- Configuração de containers
- Testes automatizados

### Pesquisa:
- Reprodutibilidade de ambiente
- Configuração de servidores
- Distribuição de projetos

## 📁 Estrutura Criada

Após execução, o projeto terá:
```
TCC---1/
├── models/
│   └── blender_generated/     # Modelos gerados pelo Blender
├── exports/
│   └── standalone_generated/  # Exportações dos scripts standalone
├── docs/                      # Documentação
├── temp/                      # Arquivos temporários
└── config.ini                # Arquivo de configuração
```

## 🔍 Solução de Problemas

### Blender não encontrado:
```bash
python scripts/automation/setup_blender_path.py
```

### Permissões no Windows:
```cmd
# Executar como administrador ou usar PATH do usuário
```

### Permissões no Linux:
```bash
sudo python scripts/automation/setup_blender_path.py
```

### Containerização:
```bash
# Usar scripts de automação no Dockerfile
RUN python scripts/automation/setup_project.py --no-auto-install
```

## 📝 Notas

- Os scripts são cross-platform (Windows, Linux, macOS)
- Configuração automática de PATH
- Suporte a múltiplas versões do Blender
- Integração com CI/CD
- Documentação completa incluída
