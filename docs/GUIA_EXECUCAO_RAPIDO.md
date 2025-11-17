# guia de execução rápida - cfd pipeline

## visão geral

este guia mostra como executar o frontend e backend do projeto cfd-pipeline-tcc com as configurações atualizadas.

## configuração atual

### portas configuradas:

- **backend:** `http://localhost:3000`
- **frontend:** `http://localhost:5173` (vite dev server)

### comunicação:

- frontend → backend: `http://localhost:3000/api/*`
- documentação api: `http://localhost:3000/docs`

## pré-requisitos

### software necessário:

- [X] python 3.9+
- [X] node.js 16+
- [X] blender (para modelagem 3d)
- [X] wsl2 + ubuntu (para simulações openfoam)
- [X] openfoam (instalado no wsl)

## instalação

### 1. clonar repositório

```bash
git clone https://github.com/bengo501/CFD-PIPELINE-TCC-1.git
cd CFD-PIPELINE-TCC-1
```

### 2. instalar dependências backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. instalar dependências frontend

```bash
cd ../frontend
npm install
```

## executar projeto

### opção 1: scripts bat (windows)

#### backend:

```bash
cd backend
EXECUTAR.bat
```

**output esperado:**

```
========================================
  iniciando backend da api
========================================

aguarde o uvicorn iniciar...

apos aparecer "Application startup complete."
o backend estara disponivel em:
  http://localhost:3000
  http://localhost:3000/docs (documentacao)

para parar, pressione CTRL+C

========================================
INFO:     Uvicorn running on http://127.0.0.1:3000
INFO:     Application startup complete.
```

#### frontend:

```bash
cd frontend
EXECUTAR.bat
```

**output esperado:**

```
========================================
  iniciando frontend react + vite
========================================

  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### opção 2: comandos manuais

#### backend:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 3000
```

#### frontend:

```bash
cd frontend
npm run dev
```

## acessar aplicação

### 1. abrir navegador

```
http://localhost:5173
```

### 2. interface disponível

#### navegação sidebar:

- **criar leito** - formulário de parâmetros
- **pipeline completo** - execução end-to-end automatizada
- **simulação cfd** - configuração manual de simulações
- **casos cfd** - visualizar casos existentes
- **jobs** - monitoramento de jobs
- **resultados** - visualizar modelos 3d e resultados

## executar pipeline completo

### passo a passo:

1. **clicar em "pipeline completo"** (sidebar)
2. **clicar em "configurar e iniciar pipeline"**
3. **configurar parâmetros:**

   - geometria do leito
   - partículas
   - simulação cfd
4. **clicar em "executar pipeline completo"**
5. **acompanhar execução:**

   - barra de progresso (0-100%)
   - logs em tempo real
   - etapas visíveis:
     1. compilação .bed → .json
     2. modelagem 3d (blender)
     3. caso openfoam
     4. simulação cfd (wsl)
6. **visualizar resultados:**

   - arquivos gerados
   - caso cfd criado
   - arquivo paraview

## verificar funcionamento

### backend (api):

#### status da api:

```bash
curl http://localhost:3000/api/status
```

**resposta esperada:**

```json
{
  "status": "online",
  "version": "0.1.0",
  "timestamp": "2025-10-21T20:00:00"
}
```

#### documentação interativa:

```
http://localhost:3000/docs
```

### frontend:

#### console do navegador:

- abrir devtools (f12)
- verificar console
- não deve haver erros de cors
- requisições para `http://localhost:3000/api/*` devem retornar 200

## troubleshooting

### erro: "connection refused" no frontend

**causa:** backend não está rodando

**solução:**

```bash
cd backend
EXECUTAR.bat
```

### erro: "cors policy" no navegador

**causa:** backend não configurado para aceitar requisições do frontend

**solução:**

- verificar `backend/app/main.py`
- confirmar que `allow_origins` inclui `http://localhost:5173`
- já está configurado corretamente no projeto

### frontend não carrega componentes

**causa:** node_modules não instalados

**solução:**

```bash
cd frontend
npm install
```

### backend não encontra módulos

**causa:** requirements não instalados

**solução:**

```bash
cd backend
pip install -r requirements.txt
```

## endpoints principais

### backend api (`http://localhost:3000/api`):

| endpoint                      | método | descrição                |
| ----------------------------- | ------- | -------------------------- |
| `/status`                   | get     | status do sistema          |
| `/bed/wizard`               | post    | compilar arquivo .bed      |
| `/pipeline/full-simulation` | post    | executar pipeline completo |
| `/pipeline/job/{job_id}`    | get     | monitorar job              |
| `/casos/list`               | get     | listar casos cfd           |
| `/model/generate`           | post    | gerar modelo 3d            |

## próximos passos

1. **executar um caso de teste:**

   - usar pipeline completo
   - configurar parâmetros simples:
     - diâmetro: 0.05m
     - altura: 0.1m
     - 100 partículas
   - aguardar execução (~10-20 min)
2. **visualizar resultados:**

   - abrir paraview
   - carregar `generated/cfd/seu_caso/caso.foam`
   - visualizar campos de velocidade e pressão
3. **explorar interface:**

   - testar diferentes configurações
   - monitorar jobs em tempo real
   - visualizar modelos 3d

**guia pipeline completo cli:** `docs/GUIA_PIPELINE_COMPLETO_CLI.md`

**guia mvp local:** `docs/mvp/README.md`

**api documentation:** `http://localhost:3000/docs`

**redoc:** `http://localhost:3000/redoc`

## checklist de verificação

- [ ] backend rodando em `http://localhost:3000`
- [ ] frontend rodando em `http://localhost:5173`
- [ ] frontend carrega sem erros no console
- [ ] requisições api retornam 200
- [ ] documentação api acessível
- [ ] pipeline completo disponível na interface
- [ ] blender instalado e no path
- [ ] wsl2 + ubuntu configurado
- [ ] openfoam instalado no wsl
