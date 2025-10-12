# guia: formatos de exportação

## visão geral

o sistema agora suporta múltiplos formatos de exportação para máxima compatibilidade com diferentes ferramentas e casos de uso.

## formatos disponíveis

### 1. blend (blender nativo)
**extensão:** `.blend`

**descrição:**
- formato nativo do blender
- preserva 100% das informações (geometria, materiais, física, animações)
- arquivo binário compactado
- requer blender para visualizar

**casos de uso:**
- edição posterior no blender
- preservar animação de empacotamento
- trabalho iterativo no modelo
- backup completo do projeto

**como usar:**
```bash
blender --python leito_extracao.py -- --params params.json --output modelo.blend --formats blend
```

**vantagens:**
- formato completo
- suporta todos recursos do blender
- boa compressão

**desvantagens:**
- requer blender instalado
- não compatível com outras ferramentas

---

### 2. gltf (gl transmission format)
**extensão:** `.gltf` + `.bin` + texturas

**descrição:**
- formato padrão para web e three.js
- arquivo texto (json) + binário
- otimizado para transmissão
- padrão khronos group

**casos de uso:**
- visualização web (three.js)
- realidade aumentada/virtual
- aplicações web 3d
- portabilidade entre engines

**como usar:**
```bash
blender --python leito_extracao.py -- --params params.json --output modelo.blend --formats gltf
```

**configurações aplicadas:**
- `export_format='GLTF_SEPARATE'` - múltiplos arquivos
- `export_apply=True` - aplicar transformações
- `export_yup=True` - y up (padrão web)
- `export_lights=True` - exportar iluminação
- `export_extras=True` - metadados

**vantagens:**
- padrão web moderno
- suporta materiais pbr
- boa documentação
- amplamente suportado

**desvantagens:**
- múltiplos arquivos (.gltf + .bin)
- requer servidor para texturas

---

### 3. glb (binary gltf)
**extensão:** `.glb`

**descrição:**
- versão binária compacta do gltf
- arquivo único autocontido
- mesmo formato, empacotamento diferente
- ideal para web

**casos de uso:**
- visualização web (preferencial)
- aplicativos mobile
- download único
- distribuição simplificada

**como usar:**
```bash
blender --python leito_extracao.py -- --params params.json --output modelo.blend --formats glb
```

**configurações aplicadas:**
- `export_format='GLB'` - arquivo único binário
- `export_apply=True` - aplicar transformações
- `export_yup=True` - y up (padrão web)
- `export_lights=True` - exportar iluminação
- `export_extras=True` - metadados

**vantagens:**
- arquivo único
- compacto
- fácil distribuição
- usado pelo viewer do projeto

**desvantagens:**
- binário (não editável como texto)
- maior que gltf separado se houver cache

---

### 4. obj (wavefront object)
**extensão:** `.obj` + `.mtl`

**descrição:**
- formato universal clássico
- texto simples legível
- suporte amplo em todas ferramentas cad/3d
- padrão de facto da indústria

**casos de uso:**
- importação em outras ferramentas (maya, 3ds max, etc)
- cad (solidworks, fusion 360)
- impressão 3d (com conversão)
- arquivamento de longo prazo

**como usar:**
```bash
blender --python leito_extracao.py -- --params params.json --output modelo.blend --formats obj
```

**configurações aplicadas:**
- `export_selected_objects=False` - exportar tudo
- `apply_modifiers=True` - aplicar modificadores
- `export_normals=True` - incluir normais
- `export_uv=True` - incluir coordenadas uv
- `export_materials=True` - exportar materiais (.mtl)

**vantagens:**
- universalmente suportado
- formato texto (editável)
- simples e estável
- boa documentação

**desvantagens:**
- não suporta animações
- materiais limitados
- arquivos grandes

---

### 5. fbx (filmbox)
**extensão:** `.fbx`

**descrição:**
- formato autodesk para interchange
- binário otimizado
- suporte para animações e rig
- usado em game engines

**casos de uso:**
- unity, unreal engine
- game development
- motion capture
- animações complexas

**como usar:**
```bash
blender --python leito_extracao.py -- --params params.json --output modelo.blend --formats fbx
```

**configurações aplicadas:**
- `use_selection=False` - exportar tudo
- `apply_scale_options='FBX_SCALE_ALL'` - escala uniforme
- `axis_forward='-Z'` - eixo z para frente
- `axis_up='Y'` - eixo y para cima
- `apply_unit_scale=True` - aplicar escala de unidade
- `mesh_smooth_type='FACE'` - suavização por face

**vantagens:**
- suporte a animações
- usado em game engines
- materiais avançados
- rig e skinning

**desvantagens:**
- formato proprietário
- documentação limitada
- compatibilidade variável

---

### 6. stl (stereolithography)
**extensão:** `.stl`

**descrição:**
- formato para impressão 3d
- apenas geometria (malha triangular)
- sem cores ou materiais
- padrão para manufatura aditiva

**casos de uso:**
- impressão 3d
- manufatura aditiva
- prototipagem rápida
- análise de volume

**como usar:**
```bash
blender --python leito_extracao.py -- --params params.json --output modelo.blend --formats stl
```

**configurações aplicadas:**
- `export_selected_objects=False` - exportar tudo
- `apply_modifiers=True` - aplicar modificadores
- `ascii_format=False` - binário (mais compacto)

**vantagens:**
- padrão para impressão 3d
- simples e robusto
- amplamente suportado
- fácil de verificar

**desvantagens:**
- apenas geometria
- sem cores/materiais
- arquivos grandes (ascii)
- não preserva estrutura

---

## como escolher o formato

### para visualização web
→ **glb** (usado no viewer do projeto)

### para edição no blender
→ **blend**

### para importar em outros programas 3d
→ **obj** (universal) ou **fbx** (se precisar animações)

### para impressão 3d
→ **stl**

### para realidade aumentada/virtual
→ **gltf** ou **glb**

### para game engines
→ **fbx**

---

## uso com múltiplos formatos

você pode exportar vários formatos de uma vez:

```bash
# via comando direto
blender --python leito_extracao.py -- \
  --params params.json \
  --output modelo.blend \
  --formats blend,glb,obj,stl

# via bed_wizard.py
python bed_wizard.py
# escolher formato na seção export

# via wizard web
# selecionar formatos no formulário
```

---

## configuração padrão

se não especificar `--formats`, o padrão é:
```
--formats blend,gltf,glb
```

isso garante:
- arquivo blend para edição
- gltf para compatibilidade
- glb para visualização web

---

## estrutura de saída

após a geração, você terá:

```
output/models/
├── meu_leito.blend       # blender nativo
├── meu_leito.blend1      # backup automático
├── meu_leito.gltf        # gltf texto
├── meu_leito.bin         # gltf binário
├── meu_leito.glb         # gltf compacto
├── meu_leito.obj         # wavefront
├── meu_leito.mtl         # materiais obj
├── meu_leito.fbx         # filmbox
└── meu_leito.stl         # stereolithography
```

---

## tamanhos aproximados

para um leito com 100 partículas:

| formato | tamanho | observações |
|---------|---------|-------------|
| blend   | ~500kb  | comprimido, completo |
| gltf    | ~800kb  | texto + bin |
| glb     | ~600kb  | binário compacto |
| obj     | ~2mb    | texto puro |
| fbx     | ~1mb    | binário |
| stl     | ~3mb    | apenas mesh |

---

## tratamento de erros

o script trata erros individualmente por formato:

```
formatos selecionados: blend, glb, obj, stl
✓ arquivo .blend salvo: output/models/modelo.blend
✓ arquivo .glb exportado: output/models/modelo.glb
✗ erro ao exportar .obj: módulo não encontrado
✓ arquivo .stl exportado: output/models/modelo.stl

exportação concluída! 3/4 formato(s) com sucesso
```

se um formato falhar, os outros continuam normalmente.

---

## compatibilidade

### blender 3.x+
- todos formatos suportados nativamente
- exportadores integrados
- configurações otimizadas

### blender 2.x
- obj, stl: suportado
- gltf/glb: requer addon
- fbx: requer addon

---

## performance

### tempo de exportação (100 partículas)

| formato | tempo |
|---------|-------|
| blend   | ~1s   |
| glb     | ~3s   |
| gltf    | ~3s   |
| obj     | ~5s   |
| fbx     | ~4s   |
| stl     | ~6s   |

**nota:** tempos variam com complexidade do modelo

---

## dicas

### otimização
- use glb ao invés de gltf para web (arquivo único)
- use stl binário ao invés de ascii (10x menor)
- obj é bom para arquivo de longo prazo

### qualidade
- blend preserva 100% da informação
- glb/gltf preservam ~95% (sem física)
- obj/fbx/stl preservam apenas geometria

### compatibilidade
- obj é o mais universal
- glb é o padrão web
- fbx é o padrão game engines
- stl é o padrão impressão 3d

---

## próximos passos

1. testar diferentes formatos
2. verificar compatibilidade com suas ferramentas
3. escolher formatos padrão para seu workflow
4. configurar exportação automática
5. integrar com pipeline cfd

**agora você tem controle total sobre como exportar seus modelos!**

