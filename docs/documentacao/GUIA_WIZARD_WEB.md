# guia rápido: wizard web

interface web para criar arquivos `.bed` de forma intuitiva, sem precisar usar o terminal.

## 🚀 início rápido (5 passos)

### 1. iniciar backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

ou no windows powershell:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

aguarde mensagem: `Application startup complete.`

### 2. iniciar frontend (nova janela/terminal)

```bash
cd frontend
npm install  # apenas na primeira vez
npm run dev
```

aguarde mensagem: `Local: http://localhost:5173/`

### 3. abrir no navegador

acesse: **http://localhost:5173**

### 4. usar wizard

1. clique na aba **🧙 wizard interativo**
2. escolha o modo:
   - **📋 questionário interativo** - criar leito completo
   - **🎨 modo blender** - apenas modelo 3D
   - **🚀 blender interativo** - modelo 3D + abre no blender
3. preencha os parâmetros (use enter para aceitar padrões)
4. revise o resumo
5. clique em **gerar arquivo .bed**

### 5. ver resultado

arquivos gerados em:
- `output/meu_leito.bed` - arquivo de entrada
- `output/meu_leito.bed.json` - parâmetros compilados
- `output/models/meu_leito.blend` - modelo 3D (se modo blender)

## 📋 exemplo de uso: criar leito simples

### opção 1: valores padrão (mais rápido)

1. abrir wizard
2. escolher "📋 questionário interativo"
3. **pressionar próximo** em todas as etapas (usa padrões)
4. digitar nome do arquivo: `teste.bed`
5. clicar "gerar arquivo .bed"

resultado: leito de 5cm × 10cm com 100 partículas esféricas de 5mm

### opção 2: personalizar

exemplo: leito industrial grande

**geometria:**
- diâmetro: `0.2` (20cm)
- altura: `0.5` (50cm)
- parede: `0.005` (5mm)

**partículas:**
- tipo: `esfera`
- diâmetro: `0.01` (1cm)
- quantidade: `500`
- densidade: `2500` (vidro)

**empacotamento:**
- gravidade: `-9.81` (terra)
- tempo máximo: `10` segundos

**exportação:**
- modo parede: `surface`
- verificar manifold: ✅ marcado

**nome:** `leito_industrial.bed`

## 🎯 modos explicados

### 📋 questionário interativo

**quando usar:**
- criar leito completo com simulação CFD
- estudos científicos
- precisa de todos os parâmetros

**inclui:**
- geometria + partículas + empacotamento + CFD
- exportação STL + JSON
- todas as opções disponíveis

**tempo:** ~3 minutos (com padrões) a ~10 minutos (personalizado)

---

### 🎨 modo blender

**quando usar:**
- apenas visualizar geometria
- não precisa simular CFD
- gerar modelos 3D rápido

**inclui:**
- geometria + partículas + empacotamento
- exportação STL + BLEND
- **não inclui** parâmetros CFD

**tempo:** ~2 minutos

**resultado:**
- arquivo `.blend` pronto
- pode abrir manualmente no blender depois

---

### 🚀 blender interativo

**quando usar:**
- ver modelo imediatamente
- ajustar visualmente
- prototipagem rápida

**inclui:**
- tudo do "modo blender"
- **abre blender automaticamente** com o modelo carregado

**requisitos:**
- blender instalado
- blender no PATH do sistema

**tempo:** ~2 minutos + tempo de abertura do blender

**resultado:**
- blender abre com modelo pronto
- pode rotacionar, zoom, editar

## 🎨 interface visual

### etapas do wizard

```
[============================] 100%
passo 7 de 7: confirmação
```

### seleção de modo

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  📋             │  │  🎨             │  │  🚀             │
│  questionário   │  │  modo           │  │  blender        │
│  interativo     │  │  blender        │  │  interativo     │
│                 │  │                 │  │                 │
│  responda       │  │  geração        │  │  gera e abre    │
│  perguntas      │  │  de modelo      │  │  automático     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### formulário (exemplo: geometria)

```
geometria do leito
─────────────────────────────────────

diâmetro (m)              altura (m)
[0.05            ]        [0.1              ]
ex: 0.05m = 5cm           ex: 0.1m = 10cm

espessura (m)             folga superior (m)
[0.002           ]        [0.01             ]
ex: 0.002m = 2mm          espaço livre acima


[← voltar]                         [próximo →]
```

### confirmação final

```
confirmação dos parâmetros
───────────────────────────────────

┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ geometria  │  │ partículas │  │ empacotamento│  │ exportação │
│────────────│  │────────────│  │──────────────│  │────────────│
│ leito:     │  │ 100 sphere │  │ rigid_body   │  │ stl_binary │
│ 0.05×0.1m  │  │ ø 0.005m   │  │ -9.81 m/s²   │  │ blend      │
│ steel      │  │ 2500 kg/m³ │  │              │  │ surface    │
└────────────┘  └────────────┘  └──────────────┘  └────────────┘

nome do arquivo
[meu_leito.bed              ]

                       [gerar arquivo .bed]
```

## ⚙️ parametros importantes

### geometria mínima

- diâmetro ≥ 0.01m (1cm)
- altura ≥ 0.01m (1cm)
- espessura ≥ 0.0001m (0.1mm)

### partículas típicas

| material | densidade (kg/m³) |
|----------|-------------------|
| vidro    | 2500              |
| aço      | 7850              |
| plástico | 1200              |
| alumínio | 2700              |
| cerâmica | 3500              |

### quantidade recomendada

| uso           | quantidade | tempo geração |
|---------------|------------|---------------|
| teste rápido  | 50-100     | ~30 segundos  |
| visualização  | 200-500    | ~2 minutos    |
| simulação     | 500-1000   | ~5 minutos    |
| alta precisão | 1000-5000  | ~15 minutos   |

## 🐛 problemas comuns

### ❌ backend não responde

**sintoma:** "erro de conexão com o backend"

**solução:**
```bash
# verificar se backend está rodando
curl http://localhost:8000/health

# se não estiver, iniciar:
cd backend
uvicorn app.main:app --reload --port 8000
```

---

### ❌ frontend não abre

**sintoma:** "This site can't be reached"

**solução:**
```bash
# verificar porta 5173
cd frontend
npm run dev

# se porta ocupada, usar outra:
npm run dev -- --port 3000
```

---

### ❌ compilação falhou

**sintoma:** "erro na compilação"

**causas possíveis:**
1. antlr não instalado
2. arquivo `.bed` inválido
3. faltam dependências python

**solução:**
```bash
# instalar antlr
cd dsl
python setup_antlr.py

# verificar dependências
pip install -r requirements.txt
```

---

### ❌ blender não abre (modo interativo)

**sintoma:** modelo gerado mas blender não abre

**solução:**
```bash
# windows: adicionar blender ao PATH
# ou instalar via winget:
winget install BlenderFoundation.Blender

# verificar se está no PATH:
blender --version
```

---

### ❌ modelo não gerado

**sintoma:** arquivo `.bed` criado mas `.blend` não

**verificar:**
1. blender instalado?
2. logs do backend (ver terminal)
3. diretório `output/models/` existe?

**criar diretório:**
```bash
mkdir -p output/models
```

## 📊 comparação: wizard cli vs web

| característica       | wizard cli (python) | wizard web (react) |
|---------------------|---------------------|---------------------|
| instalação          | ✅ python local     | ❌ só navegador     |
| interface           | terminal/texto      | gráfica/visual      |
| facilidade          | média               | fácil               |
| validação           | após digitação      | tempo real          |
| preview             | não                 | resumo visual       |
| multiplataforma     | sim                 | sim                 |
| offline             | sim                 | não (precisa backend)|
| ajuda inline        | `?`                 | tooltips/cards      |
| modo favorito       | não                 | planejado           |
| histórico           | não                 | planejado           |

**recomendação:**
- **cli:** automação, scripts, servidores
- **web:** uso diário, aprendizado, visualização

## 📝 próximos passos

após gerar o arquivo `.bed`:

### 1. verificar arquivo gerado

```bash
# ver conteúdo do .bed
cat output/meu_leito.bed

# ver JSON compilado
cat output/meu_leito.bed.json
```

### 2. gerar modelo 3D (se não usou modo blender)

```bash
# via backend api
curl -X POST http://localhost:8000/api/model/generate \
  -H "Content-Type: application/json" \
  -d '{"json_file": "output/meu_leito.bed.json"}'

# ou via cli
cd dsl
python bed_wizard.py  # opção 3: modo blender
```

### 3. simular CFD

```bash
# via backend api
curl -X POST http://localhost:8000/api/simulation/run \
  -H "Content-Type: application/json" \
  -d '{"json_file": "output/meu_leito.bed.json"}'
```

### 4. visualizar resultados

- abrir http://localhost:5173
- clicar aba **📁 resultados**
- ver modelos e simulações geradas

## 🔗 links úteis

- **documentação completa:** `frontend/README_WIZARD.md`
- **api docs:** http://localhost:8000/docs
- **wizard cli original:** `dsl/bed_wizard.py`
- **estrutura projeto:** `README.md` principal

## 🎓 tutorial passo a passo (primeira vez)

### cenário: estudante criando primeiro leito

**contexto:** preciso criar um leito empacotado de esferas de vidro para estudar queda de pressão.

**passo 1: preparar ambiente**
```bash
# terminal 1: backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# terminal 2: frontend
cd frontend
npm install
npm run dev
```

**passo 2: acessar wizard**
- abrir chrome/firefox
- ir para http://localhost:5173
- clicar "🧙 wizard interativo"

**passo 3: escolher modo**
- clicar no card "📋 questionário interativo"
  (preciso simular CFD completo)

**passo 4: geometria do leito**
- diâmetro: `0.05` (coluna de 5cm)
- altura: `0.15` (15cm de altura)
- parede: `0.003` (3mm de vidro)
- folga: `0.02` (2cm acima das esferas)
- material: `glass`
- rugosidade: `0.0` (lisa)
- clicar **próximo →**

**passo 5: tampas**
- superior: `flat` (plana)
- inferior: `flat` (plana)
- espessura superior: `0.005` (5mm)
- espessura inferior: `0.005` (5mm)
- clicar **próximo →**

**passo 6: partículas**
- tipo: `sphere` (esfera)
- diâmetro: `0.004` (4mm)
- quantidade: `300` (boa densidade)
- densidade: `2500` (vidro)
- seed: `42` (reproduzível)
- deixar outros parâmetros padrão
- clicar **próximo →**

**passo 7: empacotamento**
- método: `rigid_body`
- gravidade: `-9.81`
- tempo máximo: `10` (dar tempo para assentar)
- deixar outros padrão
- clicar **próximo →**

**passo 8: exportação**
- modo parede: `surface`
- modo fluido: `none`
- ✅ verificar manifold
- clicar **próximo →**

**passo 9: CFD**
- ✅ marcar "incluir parâmetros CFD"
- clicar **próximo →**

**passo 10: parâmetros CFD**
- regime: `laminar`
- velocidade entrada: `0.05` (5 cm/s)
- densidade fluido: `1.225` (ar)
- viscosidade: `1.8e-5` (ar)
- iterações: `5000`
- convergência: `1e-6`
- clicar **próximo →**

**passo 11: confirmação**
- revisar resumo
- nome: `leito_vidro_ar.bed`
- clicar **gerar arquivo .bed**

**passo 12: aguardar**
- mensagem de sucesso aparece
- arquivos gerados em `output/`

**passo 13: próximos passos**
- ir para aba "📊 jobs" para ver progresso
- ou aba "📁 resultados" para ver modelo

**tempo total:** 5-8 minutos

---

**desenvolvido para o tcc**

última atualização: outubro 2025

