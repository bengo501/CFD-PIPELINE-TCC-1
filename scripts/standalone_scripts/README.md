# 🚀 Scripts Standalone

Esta pasta contém scripts Python que funcionam independentemente do Blender, usando o modo headless.

## 📁 Arquivos

### 🏗️ **leito_standalone.py**
- **Descrição**: Script principal para gerar leitos de extração fora do Blender
- **Funcionalidades**:
  - Execução em modo headless (sem interface gráfica)
  - Interface de linha de comando (CLI)
  - Geração automática de arquivos .blend
  - Configuração completa de parâmetros
  - Integração com Blender via subprocess

### 📚 **exemplo_uso_standalone.py**
- **Descrição**: Exemplos de uso do script standalone
- **Funcionalidades**:
  - Demonstrações de uso básico
  - Exemplos de parâmetros personalizados
  - Geração de múltiplos leitos
  - Estudos paramétricos
  - Integração como módulo Python

### 🧪 **teste_blender.py**
- **Descrição**: Script de teste para verificar a instalação do Blender
- **Funcionalidades**:
  - Verificação da instalação do Blender
  - Teste de execução em modo headless
  - Criação de arquivo de teste simples
  - Diagnóstico de problemas

## 🚀 Como Usar

### Execução Básica:
```bash
# Gerar leito com parâmetros padrão
python leito_standalone.py

# Gerar leito personalizado
python leito_standalone.py --altura 0.15 --diametro 0.03 --num-particulas 50

# Ver ajuda
python leito_standalone.py --help
```

### Exemplos de Uso:
```bash
# Executar exemplos
python exemplo_uso_standalone.py

# Testar Blender
python teste_blender.py
```

### Como Módulo Python:
```python
from leito_standalone import LeitoStandalone

# Criar gerador
gerador = LeitoStandalone()

# Gerar leito
gerador.gerar_leito(
    altura=0.1,
    diametro=0.025,
    num_particulas=30,
    output_file="meu_leito.blend"
)
```

## 📋 Parâmetros Disponíveis

### Parâmetros do Leito:
- `--altura`: Altura do leito em metros (padrão: 0.1)
- `--diametro`: Diâmetro do leito em metros (padrão: 0.025)
- `--espessura-parede`: Espessura da parede em metros (padrão: 0.002)

### Parâmetros das Partículas:
- `--num-particulas`: Número de partículas (padrão: 30)
- `--tamanho-particula`: Tamanho das partículas em metros (padrão: 0.001)
- `--massa-particula`: Massa das partículas em kg (padrão: 0.1)
- `--tipo-particula`: Tipo de partícula (esferas, cilindros, cubos) (padrão: esferas)

### Aparência:
- `--cor-leito`: Cor do leito (azul, vermelho, verde, amarelo, laranja, roxo) (padrão: azul)
- `--cor-particulas`: Cor das partículas (padrão: verde)

### Saída:
- `--output`: Arquivo de saída (padrão: leito_gerado.blend)

## 🔧 Requisitos

- **Python** 3.6 ou superior
- **Blender** instalado e configurado no PATH
- **Módulos**: argparse, subprocess, tempfile, json, os, sys, math, random

## 📁 Saída

Os arquivos gerados são salvos em:
- **Arquivos .blend**: `models/blender_generated/`
- **Exportações**: `exports/standalone_generated/`

## 🎯 Casos de Uso

### Desenvolvimento:
- Geração rápida de modelos para teste
- Prototipagem de designs
- Validação de parâmetros

### Pesquisa:
- Estudos paramétricos
- Análise de sensibilidade
- Geração de datasets

### Automação:
- Integração em pipelines CI/CD
- Processamento em lote
- Geração automática de modelos

## 📝 Notas

- Os scripts funcionam em modo headless (sem interface gráfica)
- Requer Blender instalado e configurado no PATH
- Arquivos temporários são criados e limpos automaticamente
- Suporte a múltiplos sistemas operacionais (Windows, Linux, macOS)
