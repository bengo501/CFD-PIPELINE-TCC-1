#!/bin/bash

# Script de Automação para Linux/macOS
# Configuração automática do projeto TCC

echo "========================================"
echo "    CONFIGURADOR AUTOMATICO - TCC"
echo "========================================"
echo

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_status() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

echo "[1/5] Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python não encontrado!"
    echo "Instale o Python 3.6+ e tente novamente"
    exit 1
fi

print_status "Python encontrado: $($PYTHON_CMD --version)"

echo
echo "[2/5] Verificando Blender..."
if command -v blender &> /dev/null; then
    print_status "Blender encontrado"
    BLENDER_OK=true
else
    print_warning "Blender não encontrado no PATH"
    echo
    echo "[2.1/5] Configurando Blender automaticamente..."
    $PYTHON_CMD scripts/setup_blender_path.py
    if [ $? -eq 0 ]; then
        print_status "Blender configurado"
        BLENDER_OK=true
    else
        print_error "Falha na configuração do Blender"
        echo "Instale o Blender manualmente e tente novamente"
        exit 1
    fi
fi

echo
echo "[3/5] Criando diretórios..."
mkdir -p models exports temp
print_status "Diretórios criados"

echo
echo "[4/5] Executando setup do projeto..."
$PYTHON_CMD scripts/setup_project.py --no-auto-install
if [ $? -ne 0 ]; then
    print_error "Falha no setup do projeto"
    exit 1
fi

echo
echo "[5/5] Testando instalação..."
$PYTHON_CMD scripts/teste_blender.py
if [ $? -eq 0 ]; then
    print_status "Todos os testes passaram"
else
    print_warning "Alguns testes falharam"
fi

echo
echo "========================================"
echo "    CONFIGURACAO CONCLUIDA!"
echo "========================================"
echo
echo "Próximos passos:"
echo "1. Teste: blender --version"
echo "2. Gere um leito: $PYTHON_CMD scripts/leito_standalone.py"
echo "3. Veja exemplos: $PYTHON_CMD scripts/exemplo_uso_standalone.py"
echo
echo "Para usar Docker:"
echo "1. Construir: docker-compose build"
echo "2. Executar: docker-compose up tcc-blender"
echo
