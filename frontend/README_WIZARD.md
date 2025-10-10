# wizard web para criação de leitos empacotados

interface web simples que replica a funcionalidade do `bed_wizard.py` em formato web.

## 🎯 funcionalidades

### modos de criação

1. **questionário interativo**
   - formulário web passo a passo
   - validação em tempo real
   - valores padrão para todos os campos
   - ajuda contextual para cada parâmetro

2. **modo blender**
   - foco em geração de modelo 3D
   - sem parâmetros CFD
   - exportação automática em STL + BLEND

3. **modo blender interativo**
   - gera modelo e abre no blender automaticamente
   - ideal para visualização imediata
   - requer blender instalado localmente

## 📋 estrutura do wizard

### etapas do formulário

1. **seleção de modo** (3 opções)
2. **geometria do leito** (6 parâmetros)
   - diâmetro, altura, espessura, folga, material, rugosidade
3. **tampas** (4 parâmetros)
   - tipos superior/inferior, espessuras
4. **partículas** (12 parâmetros)
   - tipo, diâmetro, quantidade, densidade, seed
   - parâmetros físicos avançados (restituição, atrito)
5. **empacotamento** (4 parâmetros)
   - método, gravidade, sub-passos, tempo máximo
6. **exportação** (3 parâmetros)
   - modo parede, modo fluido, verificação manifold
7. **cfd (opcional)** - pode ser pulado em modos blender
8. **confirmação** - resumo e nome do arquivo

### barra de progresso

- visual da etapa atual
- navegação entre etapas
- resumo final antes de gerar

## 🎨 componentes criados

### frontend

```
frontend/src/
├── components/
│   └── BedWizard.jsx          # componente principal do wizard
└── styles/
    └── BedWizard.css          # estilos completos
```

### backend

```
backend/app/api/
└── routes_wizard.py           # endpoint /api/bed/wizard
```

## 🔌 integração com backend

### endpoint principal

```http
POST /api/bed/wizard
```

**request:**
```json
{
  "mode": "interactive",
  "fileName": "meu_leito.bed",
  "params": {
    "bed": {
      "diameter": "0.05",
      "height": "0.1",
      ...
    },
    "lids": { ... },
    "particles": { ... },
    "packing": { ... },
    "export": { ... },
    "cfd": null
  }
}
```

**response:**
```json
{
  "success": true,
  "bed_file": "output/meu_leito.bed",
  "json_file": "output/meu_leito.bed.json",
  "message": "arquivo .bed criado e compilado com sucesso"
}
```

### fluxo de dados

1. usuário preenche formulário web
2. frontend envia POST para `/api/bed/wizard`
3. backend gera arquivo `.bed` a partir dos parâmetros
4. backend compila com ANTLR gerando `.bed.json`
5. se modo blender: chama `/api/model/generate`
6. retorna caminhos dos arquivos gerados

## 🚀 como usar

### 1. iniciar backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. iniciar frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. acessar wizard

abra o navegador em: http://localhost:5173

clique na aba: **🧙 wizard interativo**

### 4. preencher formulário

- escolha o modo de criação
- preencha os parâmetros passo a passo
- revise o resumo
- clique em "gerar arquivo .bed"

### 5. verificar resultado

- arquivo `.bed` criado em `output/`
- arquivo `.bed.json` compilado
- se modo blender: modelo `.blend` gerado

## 📊 validação de dados

### no frontend (javascript)

- tipos de input corretos (number, text, select)
- atributos min/max para campos numéricos
- validação de formulário antes do envio

### no backend (pydantic)

- modelos tipados para cada seção
- validação automática de tipos
- conversão de strings para números quando necessário

## 🎨 interface visual

### design

- cards para seleção de modo
- formulários limpos e organizados
- parâmetros avançados em `<details>`
- barra de progresso visual
- resumo com cards coloridos
- responsivo (mobile-friendly)

### cores

- primária: azul (#2196F3)
- sucesso: verde (#4CAF50)
- secundária: cinza (#f5f5f5)
- gradiente no progresso

### ícones

- 📋 questionário interativo
- 🎨 modo blender
- 🚀 blender interativo
- 🧙 wizard (aba principal)

## 🔄 diferenças do bed_wizard.py

### mantido

✅ mesma estrutura de parâmetros
✅ mesmos valores padrão
✅ mesma validação
✅ mesmo formato de saída (.bed)
✅ mesma compilação (ANTLR)

### adaptado para web

🌐 formulário html em vez de terminal
🌐 navegação por cliques em vez de enter
🌐 validação visual instantânea
🌐 interface gráfica em vez de texto
🌐 não precisa instalar python localmente

### novo

✨ visualização de progresso
✨ resumo visual antes de gerar
✨ integração direta com api
✨ responsivo para mobile
✨ help contextual inline

## 📝 próximos passos

### funcionalidades planejadas

1. **pré-visualização 3D**
   - renderizar geometria antes de gerar
   - usar three.js para preview
   - mostrar estimativa de porosidade

2. **templates prontos**
   - galeria de configurações comuns
   - carregar template e editar
   - salvar configurações favoritas

3. **validação avançada**
   - verificar compatibilidade de parâmetros
   - alertas de configurações suspeitas
   - sugestões inteligentes

4. **histórico**
   - salvar últimas configurações
   - comparar parâmetros
   - clonar configuração anterior

5. **modo especialista**
   - acesso a todos os parâmetros
   - modo simplificado vs completo
   - edição de arquivo .bed direto

## 🐛 troubleshooting

### erro: "backend não responde"

```bash
# verificar se backend está rodando
curl http://localhost:8000/health
```

### erro: "compilação falhou"

- verificar se dsl/compiler/ existe
- verificar se antlr está configurado
- ver logs do backend (terminal)

### modelo não gera

- verificar se blender está no path
- ver logs do terminal do backend
- verificar `output/models/` existe

## 📚 referências

- componente principal: `frontend/src/components/BedWizard.jsx`
- rotas backend: `backend/app/api/routes_wizard.py`
- wizard python original: `dsl/bed_wizard.py`
- documentação api: http://localhost:8000/docs

---

**desenvolvido para o tcc: pipeline cfd de leitos empacotados**

versão: 0.1.0

