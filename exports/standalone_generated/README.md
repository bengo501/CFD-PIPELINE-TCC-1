# 📤 Exportações dos Scripts Standalone

Esta pasta contém arquivos gerados pelos scripts que funcionam independentemente do Blender (modo headless).

## 📁 Conteúdo

### 🏗️ **Arquivos .blend**
- **Descrição**: Modelos 3D gerados pelo script `leito_standalone.py`
- **Características**:
  - Gerados em modo headless (sem interface gráfica)
  - Configuração completa de física
  - Materiais e texturas aplicados
  - Cena configurada para renderização

### 📊 **Arquivos de Dados**
- **Descrição**: Dados de simulação e configuração
- **Tipos**:
  - Parâmetros de geração
  - Resultados de simulação
  - Configurações de física
  - Logs de execução

## 🚀 Como Usar

### Abrir Arquivos .blend:
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

### Para Exportar:
1. Abra o arquivo no Blender
2. Vá em `File > Export`
3. Escolha o formato desejado:
   - **Wavefront (.obj)**: Para uso em outros softwares 3D
   - **FBX**: Para uso em engines de jogos
   - **STL**: Para impressão 3D
   - **GLTF**: Para web e aplicações móveis

## 📋 Tipos de Arquivos

### Modelos 3D:
- **.blend**: Arquivo nativo do Blender
- **.obj**: Modelo Wavefront (compatível com muitos softwares)
- **.fbx**: Formato Autodesk (usado em engines de jogos)
- **.stl**: Para impressão 3D
- **.gltf**: Para web e aplicações móveis

### Materiais:
- **.mtl**: Arquivo de materiais Wavefront
- **.png/.jpg**: Texturas e mapas
- **.hdr**: Mapas de ambiente

### Dados:
- **.json**: Parâmetros de configuração
- **.txt**: Logs de execução
- **.csv**: Dados de simulação

## 🔧 Configurações Incluídas

### Física:
- ✅ Rigid Body para partículas
- ✅ Colisão configurada
- ✅ Massa e atrito definidos
- ✅ Restituição configurada
- ✅ Gravidade aplicada

### Materiais:
- ✅ Cores diferenciadas
- ✅ Principled BSDF
- ✅ Configuração de metais
- ✅ Transparência (se aplicável)
- ✅ Texturas (se aplicável)

### Cena:
- ✅ Iluminação configurada
- ✅ Câmera posicionada
- ✅ Renderização Cycles
- ✅ Configuração de amostras
- ✅ Configuração de resolução

## 📝 Notas

- Os arquivos são gerados automaticamente pelos scripts standalone
- Compatíveis com Blender 2.80+
- Configurações de física prontas para simulação
- Materiais otimizados para visualização
- Cena configurada para renderização

## 🔄 Regeneração

Para regenerar os arquivos:
```bash
# Gerar com parâmetros padrão
python scripts/standalone_scripts/leito_standalone.py

# Gerar com parâmetros personalizados
python scripts/standalone_scripts/leito_standalone.py --altura 0.15 --diametro 0.03 --num-particulas 50

# Gerar múltiplos modelos
python scripts/standalone_scripts/exemplo_uso_standalone.py
```

## 🎯 Casos de Uso

### Desenvolvimento:
- Prototipagem rápida de designs
- Teste de parâmetros
- Validação de configurações

### Pesquisa:
- Estudos paramétricos
- Análise de sensibilidade
- Geração de datasets

### Produção:
- Geração em lote de modelos
- Automação de processos
- Integração com pipelines

## 📊 Estatísticas

### Arquivos Gerados:
- **Modelos 3D**: Vários formatos disponíveis
- **Configurações**: Parâmetros e logs
- **Materiais**: Texturas e mapas
- **Dados**: Resultados de simulação

### Compatibilidade:
- **Blender**: 2.80+
- **Softwares 3D**: Maya, 3ds Max, Cinema 4D
- **Engines**: Unity, Unreal Engine
- **Web**: Three.js, Babylon.js
