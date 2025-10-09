# guia de uso - sistema web cfd pipeline

guia completo para usar a interface web do pipeline cfd.

---

## 🚀 início rápido (3 passos)

### 1. iniciar backend

```bash
# terminal 1
cd backend
pip install -r requirements.txt
python -m backend.app.main
```

**saída esperada:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### 2. iniciar frontend

```bash
# terminal 2  
cd frontend
npm install
npm run dev
```

**saída esperada:**
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

---

### 3. acessar interface

abrir navegador em: **http://localhost:3000**

---

## 📖 usando a interface

### tela 1: criar leito ✨

**objetivo:** configurar e gerar um leito empacotado

**passo a passo:**

1. **preencher parâmetros:**

   ```
   geometria do leito:
     diâmetro: 0.05 m (entre 0.01 e 1.0)
     altura: 0.1 m (entre 0.01 e 2.0)
     espessura parede: 0.002 m
   
   partículas:
     quantidade: 100 (entre 10 e 10000)
     tipo: esfera ou cubo
     diâmetro: 0.005 m
   
   empacotamento:
     método: rigid body
     gravidade: -9.81 m/s²
     fricção: 0.5
     substeps: 10
   ```

2. **clicar em "🚀 gerar leito"**

3. **aguardar processamento:**
   - ✅ compilação do arquivo .bed
   - ✅ geração de .bed.json
   - ✅ job de modelo 3d criado

4. **redirecionamento automático** para aba "jobs"

**dicas:**
- valores padrão já são válidos
- use hint (texto cinza) para ver limites
- alterações em tempo real

---

### tela 2: jobs 📊

**objetivo:** monitorar execução dos jobs

**interface dividida em 2:**

#### esquerda: lista de jobs

- todos os jobs criados
- ordenados por data (mais recente primeiro)
- ícones de status:
  - ⏳ queued - aguardando
  - 🔄 running - executando
  - ✅ completed - concluído
  - ❌ failed - falhou
- barra de progresso (0-100%)
- atualização automática a cada 2s

#### direita: detalhes do job selecionado

- id único do job
- tipo (compilação/modelo 3d/simulação)
- status atual
- progresso detalhado
- timestamps (criação, atualização)
- arquivos gerados
- metadata
- mensagens de erro (se houver)

**exemplo de uso:**

```
1. clicar em job na lista esquerda
2. ver detalhes na direita
3. aguardar status mudar para "completed"
4. copiar path do arquivo gerado
5. ir para aba "resultados"
```

---

### tela 3: resultados 📁

**objetivo:** visualizar e baixar arquivos gerados

#### seção 1: modelos 3d

**cards de arquivos .blend:**
- ícone 📦
- nome do arquivo
- tamanho (KB/MB)
- data de criação
- botões:
  - 👁️ visualizar (placeholder)
  - ⬇️ baixar

**ações:**
- **visualizar:** abre modal (futuro: three.js)
- **baixar:** download do arquivo .blend

#### seção 2: simulações

**cards de casos openfoam:**
- ícone 📊
- nome do caso
- tamanho total
- data de criação
- botão:
  - 📈 resultados (futuro)

**workflow típico:**
```
1. ver lista de modelos gerados
2. clicar em "visualizar" (placeholder por enquanto)
3. ou clicar em "baixar" para abrir no blender
4. ver lista de simulações
5. clicar em "resultados" para análise (futuro)
```

---

## 🎯 fluxo completo end-to-end

### caso de uso: criar leito e gerar modelo 3d

```
┌─────────────────────────────────────────────┐
│ 1. CONFIGURAR                               │
│    aba: criar leito                         │
│    ação: preencher formulário               │
│    tempo: 1-2 minutos                       │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│ 2. GERAR                                    │
│    ação: clicar "gerar leito"               │
│    backend: compila .bed → .bed.json        │
│    tempo: 5-10 segundos                     │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│ 3. MONITORAR                                │
│    aba: jobs (redirecionamento automático)  │
│    status: queued → running → completed     │
│    tempo: 30s - 3min (depende do tamanho)   │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│ 4. VISUALIZAR                               │
│    aba: resultados                          │
│    ação: baixar .blend                      │
│    ou: visualizar no browser (futuro)       │
└─────────────────────────────────────────────┘
```

---

## 📊 status do sistema

**header (topo):**
- 🟢 online - sistema funcionando
- 🔴 offline - backend não responde
- contador de jobs em execução

**verificação manual:**

```bash
# testar backend
curl http://localhost:8000/health

# resposta esperada:
{
  "status": "healthy",
  "services": {
    "bed_compiler": "available",
    "blender": "available",
    "openfoam": "available"
  }
}
```

---

## 🐛 resolução de problemas

### erro: "network error"

**causa:** backend não está rodando

**solução:**
```bash
cd backend
python -m backend.app.main
```

---

### erro: "compilation failed"

**causa:** antlr não configurado

**solução:**
```bash
cd dsl
python setup_antlr.py
```

---

### erro: "blender not found"

**causa:** blender não detectado automaticamente

**solução:** editar `backend/app/services/blender_service.py`
```python
self.blender_exe = r"C:\seu\caminho\para\blender.exe"
```

---

### job fica "queued" eternamente

**causa:** job em execução travou

**solução:** reiniciar backend
```bash
# ctrl+c no terminal do backend
# depois:
python -m backend.app.main
```

---

### modelo não aparece em "resultados"

**verificar:**
1. job completou com sucesso?
2. arquivo existe em `output/models/`?
3. atualizar página (F5)

---

## 💡 dicas e truques

### atalhos de teclado

- `Ctrl + R` - recarregar página
- `F5` - atualizar dados
- `F12` - abrir devtools (ver logs)

### parâmetros recomendados

**teste rápido (< 30s):**
```
diâmetro: 0.05 m
altura: 0.1 m
partículas: 50
```

**produção normal (~2min):**
```
diâmetro: 0.1 m
altura: 0.2 m
partículas: 200
```

**caso pesado (5-10min):**
```
diâmetro: 0.2 m
altura: 0.5 m
partículas: 1000
```

### monitorar logs

**backend:**
```bash
# ver logs em tempo real
python -m backend.app.main | tee backend.log
```

**frontend:**
- abrir devtools (F12)
- aba "console"
- ver requisições em "network"

---

## 📈 próximas features

### em desenvolvimento

- [ ] visualização 3d real (three.js)
- [ ] gráficos de análise (plotly/recharts)
- [ ] websockets (progresso em tempo real)
- [ ] modo escuro

### planejado

- [ ] editar leitos existentes
- [ ] templates de leitos pré-configurados
- [ ] comparação de múltiplos modelos
- [ ] exportar relatórios pdf

---

## 🎓 exemplos práticos

### exemplo 1: leito pequeno com poucas partículas

**uso:** teste rápido, validação

```javascript
parâmetros = {
  diameter: 0.05,      // 5 cm
  height: 0.1,         // 10 cm
  particle_count: 50,  // apenas 50
  particle_diameter: 0.005  // 5 mm
}

tempo estimado: 20-30 segundos
```

---

### exemplo 2: leito médio para estudo

**uso:** simulação típica

```javascript
parâmetros = {
  diameter: 0.1,       // 10 cm
  height: 0.2,         // 20 cm
  particle_count: 200, // 200 partículas
  particle_diameter: 0.008  // 8 mm
}

tempo estimado: 1-2 minutos
```

---

### exemplo 3: leito grande para pesquisa

**uso:** estudo detalhado

```javascript
parâmetros = {
  diameter: 0.3,        // 30 cm
  height: 0.6,          // 60 cm
  particle_count: 1000, // 1000 partículas
  particle_diameter: 0.01  // 1 cm
}

tempo estimado: 5-10 minutos
```

---

## ✅ checklist de uso

### primeira vez

- [ ] instalar dependências backend
- [ ] instalar dependências frontend
- [ ] iniciar backend
- [ ] iniciar frontend
- [ ] acessar http://localhost:3000
- [ ] criar leito de teste
- [ ] verificar job completo
- [ ] baixar arquivo .blend
- [ ] abrir no blender

### uso diário

- [ ] iniciar backend
- [ ] iniciar frontend
- [ ] criar leito
- [ ] monitorar job
- [ ] baixar resultados

---

## 📞 suporte

**documentação:**
- backend: `backend/README.md`
- frontend: `frontend/README.md`
- api: http://localhost:8000/docs

**logs:**
- backend: terminal onde rodou python
- frontend: devtools console (F12)

---

**sistema web está pronto para uso! 🚀**

---

## 📊 resumo técnico

```
stack:
  backend: python 3.11 + fastapi
  frontend: react 18 + vite
  comunicação: rest api + json
  
arquivos:
  backend: 14 arquivos (~1600 linhas)
  frontend: 12 arquivos (~1800 linhas)
  total: ~3400 linhas de código
  
endpoints: 15
componentes react: 4
serviços backend: 3
```

