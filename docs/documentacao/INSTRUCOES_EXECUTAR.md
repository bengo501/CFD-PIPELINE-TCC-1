# instruções para executar o wizard web

## ✅ status atual

- ✅ **backend:** rodando em http://localhost:8000
- ⏳ **frontend:** precisa iniciar

## 🚀 como executar

### opção 1: usar terminais separados (recomendado)

#### terminal 1 (backend) - já está rodando!

```bash
cd C:\Users\joxto\Downloads\CFD-PIPELINE-TCC-1\backend
python -m uvicorn app.main:app --reload --port 8000
```

✅ **já está funcionando!** pode ver em: http://localhost:8000/docs

#### terminal 2 (frontend) - abrir novo terminal

```bash
cd C:\Users\joxto\Downloads\CFD-PIPELINE-TCC-1\frontend
npm run dev
```

aguarde aparecer: `Local: http://localhost:5173/`

### opção 2: usar vscode integrated terminal

1. abrir terminal integrado (ctrl + `)
2. clicar no botão `+` para criar novo terminal
3. no novo terminal, executar:

```bash
cd frontend
npm run dev
```

## 🌐 acessar aplicação

após os dois servidores estarem rodando:

1. abrir navegador
2. ir para: **http://localhost:5173**
3. clicar na aba: **🧙 wizard interativo**

## 📋 verificar se está funcionando

### verificar backend

```bash
curl http://localhost:8000/
```

deve retornar:
```json
{"message":"cfd pipeline api","version":"0.1.0","docs":"/docs","status":"running"}
```

### verificar frontend

abrir navegador em: http://localhost:5173

deve ver a interface do cfd pipeline

## 🐛 troubleshooting

### erro: "npm not found"

```bash
# instalar node.js de: https://nodejs.org/
# ou via winget:
winget install OpenJS.NodeJS
```

### erro: dependências faltando

```bash
cd frontend
npm install
```

### porta 8000 ou 5173 ocupada

```bash
# backend em outra porta:
cd backend
python -m uvicorn app.main:app --reload --port 8001

# frontend em outra porta:
cd frontend
npm run dev -- --port 3000
```

### erro: "module 'app' not found"

certifique-se de estar no diretório `backend/` ao executar uvicorn

## 🎯 testar wizard

### teste rápido

1. acessar http://localhost:5173
2. clicar "🧙 wizard interativo"
3. escolher "📋 questionário interativo"
4. clicar "próximo →" em todas as etapas (usa valores padrão)
5. digitar nome: `teste.bed`
6. clicar "gerar arquivo .bed"

**resultado esperado:**
- mensagem de sucesso
- arquivo criado em `output/teste.bed`
- json em `output/teste.bed.json`

### teste completo

1. escolher "🎨 modo blender"
2. personalizar parâmetros:
   - diâmetro: 0.1
   - altura: 0.2
   - partículas: 200
3. gerar arquivo
4. verificar modelo 3D gerado

## 📊 endpoints disponíveis

### backend api docs

http://localhost:8000/docs - documentação interativa swagger

principais endpoints:
- `GET /` - status da api
- `GET /health` - health check
- `POST /api/bed/wizard` - criar leito via wizard
- `POST /api/model/generate` - gerar modelo 3D
- `GET /api/bed/wizard/help/{section}` - ajuda sobre parâmetros

## 📝 próximos passos

após testar o wizard:

1. **criar leito personalizado**
   - experimentar diferentes parâmetros
   - testar os 3 modos

2. **gerar modelo 3D**
   - usar modo blender
   - verificar arquivo `.blend` em `output/models/`

3. **simular CFD** (futuro)
   - incluir parâmetros cfd
   - rodar simulação openfoam

## 🔗 documentação

- guia prático: `GUIA_WIZARD_WEB.md`
- doc técnica: `frontend/README_WIZARD.md`
- resumo: `RESUMO_WIZARD_WEB.md`

---

**precisa de ajuda?**

abra issue no github ou consulte a documentação completa!

