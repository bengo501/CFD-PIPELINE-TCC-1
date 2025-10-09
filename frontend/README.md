# frontend cfd pipeline - react

interface web para gerenciar pipeline de simulações cfd.

---

## 🚀 início rápido

### 1. instalar dependências

```bash
cd frontend
npm install
```

### 2. iniciar desenvolvimento

```bash
npm run dev
```

acesse: http://localhost:3000

---

## 📦 o que foi implementado

### telas principais

1. **criar leito** ✨
   - formulário com 10+ parâmetros
   - validação de entrada
   - compilação automática
   - geração de modelo 3d

2. **jobs** 📊
   - lista de todos os jobs
   - monitoramento em tempo real
   - barra de progresso
   - detalhes completos

3. **resultados** 📁
   - lista de modelos 3d
   - lista de simulações
   - download de arquivos
   - visualização (placeholder)

---

## 🎨 componentes

```
src/
├── App.jsx                  # componente principal
├── services/
│   └── api.js              # cliente http (axios)
└── components/
    ├── BedForm.jsx         # formulário de parâmetros
    ├── JobStatus.jsx       # monitoramento de jobs
    ├── ResultsList.jsx     # lista de resultados
    └── ModelViewer.jsx     # visualização 3d (placeholder)
```

---

## 🔧 funcionalidades

### criar leito

**parâmetros configuráveis:**
- diâmetro do leito (0.01-1.0 m)
- altura do leito (0.01-2.0 m)
- espessura da parede
- quantidade de partículas (10-10000)
- tipo de partícula (esfera/cubo)
- diâmetro da partícula
- método de empacotamento
- gravidade, fricção, substeps

**fluxo:**
1. usuário preenche formulário
2. click em "gerar leito"
3. frontend → POST /api/bed/compile
4. backend compila .bed
5. frontend → POST /api/model/generate
6. job assíncrono iniciado
7. redireciona para aba "jobs"

---

### monitorar jobs

**features:**
- atualização automática a cada 2s
- lista de todos os jobs
- filtro por status/tipo
- barra de progresso (0-100%)
- detalhes completos:
  - id do job
  - tipo (compilação/modelo/simulação)
  - status (queued/running/completed/failed)
  - timestamps
  - arquivos gerados
  - mensagens de erro
  - metadata

**status possíveis:**
- ⏳ queued - na fila
- 🔄 running - em execução
- ✅ completed - concluído
- ❌ failed - falhou

---

### visualizar resultados

**modelos 3d:**
- lista de arquivos .blend gerados
- informações (nome, tamanho, data)
- botão de download
- visualização (placeholder - futuro: three.js)

**simulações:**
- lista de casos openfoam
- informações completas
- acesso aos resultados

---

## 🎯 integração com backend

### endpoints utilizados

```javascript
// compilar .bed
POST /api/bed/compile
  → { bed_file, json_file }

// gerar modelo
POST /api/model/generate
  → { job_id, status }

// status de job
GET /api/job/{job_id}
  → { status, progress, output_files }

// listar jobs
GET /api/jobs
  → [ { job_id, status, ... } ]

// listar arquivos
GET /api/files/{type}
  → { files: [...] }

// status sistema
GET /api/status
  → { api, services, jobs }
```

---

## 🎨 design

### cores

```css
primary: #2563eb (azul)
success: #10b981 (verde)
warning: #f59e0b (amarelo)
error: #ef4444 (vermelho)
```

### ícones

- ✨ criar leito
- 📊 jobs
- 📁 resultados
- 🔬 título
- ⏳ aguardando
- 🔄 executando
- ✅ concluído
- ❌ falhou

---

## 📱 responsivo

interface adaptável para:
- desktop (1200px+)
- tablet (768px-1199px)
- mobile (< 768px)

---

## 🔮 próximas features

### curto prazo

- [ ] visualização 3d real (three.js)
- [ ] gráficos de resultados (recharts/plotly)
- [ ] websockets (progresso em tempo real)
- [ ] modo escuro

### médio prazo

- [ ] editar parâmetros de jobs existentes
- [ ] comparar múltiplos modelos
- [ ] histórico de execuções
- [ ] exportar relatórios

### longo prazo

- [ ] autenticação de usuários
- [ ] compartilhamento de projetos
- [ ] templates de leitos
- [ ] inteligência para sugerir parâmetros

---

## 🐛 troubleshooting

### erro: "network error"

verificar se backend está rodando:
```bash
# em outra janela
cd backend
python -m backend.app.main
```

### erro: "cors"

backend já está configurado para aceitar `localhost:3000` e `localhost:5173`

### port 3000 em uso

alterar em `vite.config.js`:
```javascript
server: {
  port: 3001
}
```

---

## 🔧 desenvolvimento

### adicionar novo componente

```bash
# criar arquivo
touch src/components/NovoComponente.jsx

# importar em App.jsx
import NovoComponente from './components/NovoComponente'
```

### adicionar nova rota api

```javascript
// src/services/api.js
export const novaFuncao = async (params) => {
  const response = await api.post('/api/nova-rota', params);
  return response.data;
};
```

---

## 📦 build para produção

```bash
npm run build
```

gera em `dist/`:
- html, css, js minificados
- assets otimizados
- pronto para deploy

---

## 🐳 docker (futuro)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]
```

---

**interface web funcional e pronta para uso! 🎉**

