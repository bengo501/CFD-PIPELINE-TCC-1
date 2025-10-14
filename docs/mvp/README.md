# guia completo: mvp local passo a passo

## visão geral

documentação detalhada para implementar, executar e validar o mvp (minimum viable product) local do projeto cfd pipeline.

---

## 📚 índice de etapas

### [etapa 1: introdução ao mvp](01_INTRODUCAO_MVP.md)
**o que é:** conceitos básicos, arquitetura e visão geral

**conteúdo:**
- o que é o mvp
- arquitetura do sistema
- componentes principais
- fluxo de dados
- diferenças mvp vs produção

**tempo:** 15 minutos de leitura

---

### [etapa 2: verificar pré-requisitos](02_PRE_REQUISITOS.md)
**o que é:** checklist de software necessário

**conteúdo:**
- python 3.11+
- node.js 18+
- postgresql 15+
- blender 4.x (opcional)
- openfoam 11 (opcional)
- dependências python/node

**tempo:** 30-60 minutos

**comandos principais:**
```bash
python --version
node --version
psql --version
```

---

### [etapa 3: configuração do ambiente](03_CONFIGURACAO_AMBIENTE.md)
**o que é:** setup de banco de dados e variáveis

**conteúdo:**
- criar banco de dados
- inicializar tabelas
- configurar .env
- testar conexões
- estrutura de diretórios

**tempo:** 20-30 minutos

**comandos principais:**
```bash
createdb cfd_pipeline
cd backend && python scripts/init_database.py
cp env.example .env
```

---

### [etapa 4: executar backend](04_EXECUTAR_BACKEND.md)
**o que é:** iniciar servidor fastapi

**conteúdo:**
- iniciar uvicorn
- verificar endpoints
- testar api
- acessar swagger ui
- validar integração banco

**tempo:** 15-20 minutos

**comandos principais:**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**urls:**
- api: http://localhost:8000
- docs: http://localhost:8000/docs
- health: http://localhost:8000/health

---

### [etapa 5: executar frontend](05_EXECUTAR_FRONTEND.md)
**o que é:** iniciar aplicação react

**conteúdo:**
- iniciar vite dev server
- verificar interface
- testar navegação
- validar comunicação backend
- verificar estilos

**tempo:** 10-15 minutos

**comandos principais:**
```bash
cd frontend
npm run dev
```

**url:** http://localhost:5173

---

### [etapa 6: testar integração](06_TESTAR_INTEGRACAO.md)
**o que é:** validar integração completa

**conteúdo:**
- criar leito via interface
- listar leitos
- visualização 3d
- gerar modelo blender
- executar simulação cfd
- download de arquivos

**tempo:** 30-45 minutos

**testes:**
- ✅ frontend → backend
- ✅ backend → banco
- ✅ backend → blender
- ✅ backend → openfoam
- ✅ visualização three.js

---

### [etapa 7: validar funcionalidades](07_VALIDAR_FUNCIONALIDADES.md)
**o que é:** checklist final de validação

**conteúdo:**
- funcionalidades core
- funcionalidades auxiliares
- testes de qualidade
- métricas de sucesso
- próximos passos

**tempo:** 20-30 minutos

**critérios:**
- [ ] crud completo
- [ ] geração 3d
- [ ] simulação cfd
- [ ] visualização
- [ ] interface responsiva

---

## 🎯 como usar este guia

### 1. sequencial (recomendado)

seguir etapas em ordem:
```
1 → 2 → 3 → 4 → 5 → 6 → 7
```

**vantagem:**
- aprendizado gradual
- validação contínua
- troubleshooting facilitado

---

### 2. rápido (experiente)

pular para etapas específicas:
```
1 (visão) → 2 (verificar) → 4+5 (executar) → 6 (testar)
```

**vantagem:**
- mais rápido
- foco no essencial
- para quem já conhece stack

---

### 3. troubleshooting

consultar etapa específica quando problema:
```
erro backend → etapa 4
erro frontend → etapa 5
erro integração → etapa 6
```

---

## 📋 checklist rápido

### antes de começar:
- [ ] ler etapa 1 (introdução)
- [ ] verificar etapa 2 (pré-requisitos)
- [ ] configurar etapa 3 (ambiente)

### execução:
- [ ] backend rodando (etapa 4)
- [ ] frontend rodando (etapa 5)
- [ ] integração testada (etapa 6)

### validação:
- [ ] todas funcionalidades ok (etapa 7)
- [ ] sem erros críticos
- [ ] pronto para demonstrar

---

## 🚀 quick start

### setup completo (primeira vez):

```bash
# 1. verificar pré-requisitos
python --version  # 3.11+
node --version    # 18+
psql --version    # 15+

# 2. criar banco
createdb -U postgres cfd_pipeline

# 3. instalar dependências
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 4. configurar ambiente
cd ../backend
cp env.example .env
# editar .env com suas configurações

# 5. inicializar banco
python scripts/init_database.py

# 6. executar (2 terminais)
# terminal 1:
cd backend && python -m uvicorn app.main:app --reload

# terminal 2:
cd frontend && npm run dev
```

### executar (após setup):

```bash
# opção 1: script automático
iniciar-mvp.bat  # escolher opção 3

# opção 2: manual (2 terminais)
cd backend && python -m uvicorn app.main:app --reload
cd frontend && npm run dev
```

---

## ⏱️ tempo estimado

### setup inicial (primeira vez):
- leitura documentação: 15-30 min
- verificar pré-requisitos: 30-60 min
- configurar ambiente: 20-30 min
- **total:** ~1h30min - 2h

### executar (após setup):
- iniciar backend: 1 min
- iniciar frontend: 1 min
- **total:** ~2 min

### testes e validação:
- testar integração: 30-45 min
- validar funcionalidades: 20-30 min
- **total:** ~50min - 1h15min

### **tempo total (primeira vez):** 3-4 horas
### **tempo execução (subsequente):** 2 minutos

---

## 🎓 pré-requisitos de conhecimento

### essencial (para usar):
- [ ] usar terminal/cmd
- [ ] editar arquivos texto
- [ ] navegar browser
- [ ] usar postgres básico

### recomendado (para entender):
- [ ] python básico
- [ ] javascript/react básico
- [ ] apis rest conceito
- [ ] sql básico

### opcional (para modificar):
- [ ] fastapi framework
- [ ] react avançado
- [ ] sqlalchemy orm
- [ ] three.js

---

## 🛠️ ferramentas úteis

### durante desenvolvimento:
- **postman/insomnia** - testar api
- **pgadmin** - gerenciar postgres
- **react devtools** - debug react
- **vscode** - editor código

### debug:
- **browser devtools** (f12)
- **curl** - testar endpoints
- **psql** - queries diretas
- **python debugger** (pdb)

---

## 📊 estrutura das etapas

cada etapa contém:

### 1. objetivo
- o que será feito
- por que é importante

### 2. passos
- comandos exatos
- explicações claras
- saídas esperadas

### 3. validações
- checkboxes verificar
- como testar
- o que esperar

### 4. troubleshooting
- problemas comuns
- soluções práticas
- comandos debug

### 5. próximo passo
- link próxima etapa
- pré-requisitos atendidos
- status atual

---

## ✅ resultado final

ao completar todas as etapas, você terá:

### sistema funcionando:
- ✅ backend api rest (fastapi)
- ✅ frontend web (react)
- ✅ banco de dados (postgresql)
- ✅ geração 3d (blender)
- ✅ simulação cfd (openfoam)
- ✅ visualização interativa (three.js)

### funcionalidades:
- ✅ criar leitos via interface
- ✅ gerar modelos 3d
- ✅ executar simulações
- ✅ visualizar resultados
- ✅ download de arquivos
- ✅ documentação api

### qualidade:
- ✅ código organizado
- ✅ documentado
- ✅ testado
- ✅ funcional

---

## 🔄 fluxo de trabalho

### primeira execução:
```
etapa 1 → etapa 2 → etapa 3 → 
etapa 4 → etapa 5 → etapa 6 → etapa 7
```

### execução diária:
```
etapa 4 (backend) → etapa 5 (frontend) → trabalhar
```

### adicionar feature:
```
codificar → testar (etapa 6) → validar (etapa 7)
```

### problemas:
```
identificar → consultar etapa específica → corrigir
```

---

## 📚 documentação relacionada

### outros guias:
- `../guias/` - guias gerais do projeto
- `../backend/` - documentação backend
- `../setup/` - configuração e deploy

### documentação técnica:
- `../../README.md` - readme principal
- `../../backend/README.md` - backend
- `../../frontend/README.md` - frontend

---

## 🎯 suporte

### se encontrar problemas:

1. **consultar troubleshooting** na etapa específica
2. **verificar logs** (backend terminal, browser console)
3. **revisar pré-requisitos** (etapa 2)
4. **verificar configuração** (etapa 3)
5. **consultar documentação** relacionada

### comandos debug úteis:
```bash
# verificar serviços
curl http://localhost:8000/health
curl http://localhost:5173

# verificar banco
psql -U postgres -d cfd_pipeline -c "\dt"

# verificar logs
# ver terminal onde backend/frontend rodam
```

---

## 🚀 começar agora

**pronto para começar?**

1. **ler etapa 1:** [01_INTRODUCAO_MVP.md](01_INTRODUCAO_MVP.md)
2. **ou pular para setup:** [02_PRE_REQUISITOS.md](02_PRE_REQUISITOS.md)
3. **ou quick start:** copiar comandos acima

---

**boa sorte com o mvp! 🎉✨**
