# 🎨 Modelos Gerados pelo Blender

Esta pasta contém arquivos `.blend` gerados pelos scripts que rodam diretamente no Blender.

## 📁 Conteúdo

### 🏗️ **leitoTestPythonScript.blend**
- **Descrição**: Leito de extração gerado pelo script `leito_extracao.py`
- **Características**:
  - Cilindro oco com 10 cm de altura e 2,5 cm de diâmetro
  - Tampas superior e inferior separadas
  - 30 esferas pequenas com física de colisão
  - Materiais coloridos (azul para leito, verde para partículas)
  - Configuração completa de física

### 📦 **CuboOcoTampa.blend**
- **Descrição**: Cubo oco gerado pelo script `cubo_oco.py`
- **Características**:
  - Cubo com bordas ultra-finas
  - Tampa independente
  - Operação booleana para criar o vazio
  - Materiais coloridos

## 🚀 Como Usar

### Abrir no Blender:
1. Abra o Blender
2. Vá em `File > Open`
3. Navegue até esta pasta
4. Selecione o arquivo `.blend` desejado
5. Clique em `Open`

### Para Simular Física:
1. Abra o arquivo do leito de extração
2. Pressione `Alt+A` para iniciar a simulação
3. Use `Space` para pausar/retomar
4. Use `Esc` para parar a simulação

### Para Visualizar:
- **Viewport Shading**: Pressione `Z` para alternar entre modos de visualização
- **Camera**: Use `Numpad 0` para visualizar pela câmera
- **Orbit**: Use `Middle Mouse Button` para orbitar
- **Zoom**: Use `Mouse Wheel` para zoom

## 📋 Informações dos Modelos

### Leito de Extração:
- **Tipo**: Cilindro oco com partículas
- **Dimensões**: 10 cm altura × 2,5 cm diâmetro
- **Partículas**: 30 esferas pequenas
- **Física**: Rigid Body configurado
- **Materiais**: Azul (leito), Verde (partículas)

### Cubo Oco:
- **Tipo**: Cubo com vazio interno
- **Dimensões**: 1m × 1m × 1m
- **Tampa**: Separada e independente
- **Materiais**: Coloridos para visualização

## 🔧 Configurações Incluídas

### Física:
- ✅ Rigid Body para partículas
- ✅ Colisão configurada
- ✅ Massa e atrito definidos
- ✅ Restituição configurada

### Materiais:
- ✅ Cores diferenciadas
- ✅ Principled BSDF
- ✅ Configuração de metais
- ✅ Transparência (se aplicável)

### Cena:
- ✅ Iluminação configurada
- ✅ Câmera posicionada
- ✅ Renderização Cycles
- ✅ Configuração de amostras

## 📝 Notas

- Os arquivos são compatíveis com Blender 2.80+
- Todos os objetos têm nomes descritivos
- As configurações de física estão prontas para simulação
- Os materiais são otimizados para visualização
- A cena está configurada para renderização

## 🔄 Regeneração

Para regenerar os modelos:
1. Execute os scripts correspondentes no Blender
2. Salve os novos arquivos nesta pasta
3. Substitua os arquivos antigos se necessário

### Scripts Correspondentes:
- `leitoTestPythonScript.blend` ← `scripts/blender_scripts/leito_extracao.py`
- `CuboOcoTampa.blend` ← `scripts/blender_scripts/cubo_oco.py`
