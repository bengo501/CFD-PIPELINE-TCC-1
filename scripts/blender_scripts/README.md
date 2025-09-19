# 🎨 Scripts do Blender

Esta pasta contém scripts Python que são executados diretamente dentro do Blender.

## 📁 Arquivos

### 🏗️ **leito_extracao.py**
- **Descrição**: Script principal para criar o leito de extração
- **Funcionalidades**:
  - Cilindro oco com 10 cm de altura e 2,5 cm de diâmetro
  - Tampas superior e inferior separadas
  - 30 esferas pequenas com física de colisão
  - Materiais coloridos
  - Configuração automática da cena

### 📦 **cubo_oco.py**
- **Descrição**: Script para criar um cubo oco com tampa
- **Funcionalidades**:
  - Cubo com bordas ultra-finas
  - Tampa independente
  - Materiais coloridos
  - Operação booleana para criar o vazio

### 🖱️ **leito_interativo.py**
- **Descrição**: Script interativo com interface gráfica
- **Funcionalidades**:
  - Interface Tkinter para configuração de parâmetros
  - Múltiplos tipos de partículas (esferas, cilindros, cubos)
  - Cores personalizáveis
  - Validação automática de parâmetros
  - Integração com Blender via threading

## 🚀 Como Usar

### Execução no Blender:
1. Abra o Blender
2. Vá para a aba "Scripting"
3. Abra o script desejado
4. Execute o script (▶️)

### Para o Leito de Extração:
```python
# Execute o script e pressione Alt+A para simular a física
```

### Para o Cubo Oco:
```python
# Execute o script para criar o cubo oco
```

### Para o Leito Interativo:
```python
# Execute o script e configure os parâmetros na interface
```

## 📋 Requisitos

- **Blender** versão 2.80 ou superior
- **Python** (incluído no Blender)
- **Módulos**: bpy, bmesh, math, random
- **Para leito_interativo**: tkinter (pode não estar disponível no Blender)

## 🔧 Configuração

Todos os scripts incluem:
- ✅ Limpeza automática da cena
- ✅ Configuração de materiais
- ✅ Configuração de física
- ✅ Configuração de iluminação
- ✅ Configuração de câmera

## 📝 Notas

- Todos os scripts estão comentados em português
- Os parâmetros podem ser facilmente modificados no código
- Os scripts são independentes e podem ser executados em qualquer ordem
- O leito_interativo.py pode apresentar problemas se tkinter não estiver disponível
