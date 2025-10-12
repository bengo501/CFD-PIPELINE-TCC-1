# guia: pipeline completo web

## visão geral

interface web que replica o `bed_wizard.py` com execução automatizada end-to-end de todo o pipeline cfd.

---

## o que é o pipeline completo

### conceito

um único clique executa **todo o processo**:
```
parametros → dsl → blender → openfoam → resultados
```

### equivalente ao bed_wizard.py

**python cli:**
```bash
cd dsl
python bed_wizard.py
# escolher modo 4 (blender interativo)
# preencher parametros
# aguardar geração
# modelo abre automaticamente

cd ../scripts/openfoam_scripts
python setup_openfoam_case.py ... --run
# aguardar simulação
# visualizar no paraview
```

**web pipeline:**
```
1. clicar em "pipeline completo"
2. clicar em "iniciar pipeline"
3. aguardar execução automática
4. visualizar resultados
```

**tempo economizado:** ~5-10 minutos de comandos manuais

---

## como usar

### passo 1: acessar

```
1. abrir http://localhost:5173
2. clicar na aba "🚀 pipeline completo"
```

### passo 2: iniciar

```
interface mostra:
┌────────────────────────────────────────┐
│ pipeline completo - leitos empacotados │
├────────────────────────────────────────┤
│                                        │
│  1 → 2 → 3 → 4 → 5                     │
│  │   │   │   │   │                     │
│  .bed json 3d cfd vis                  │
│                                        │
│  [iniciar pipeline completo]           │
│                                        │
└────────────────────────────────────────┘
```

**clicar em:** "iniciar pipeline completo"

### passo 3: aguardar execução

**interface muda para:**

```
┌────────────────────────────────────────┐
│ executando pipeline                    │
├────────────────────────────────────────┤
│                                        │
│  [📝 compilando dsl]    ✅             │
│  [🎨 gerando 3d]        ⏳ ativa       │
│  [⚙️ preparando cfd]    ⏸️ pendente    │
│  [🌊 simulando]         ⏸️ pendente    │
│                                        │
│  progresso: [████████░░░░] 50%        │
│                                        │
│  log de execução:                      │
│  16:30:00 - compilando arquivo .bed... │
│  16:30:02 - ✓ .bed compilado           │
│  16:30:03 - gerando modelo 3d...       │
│  16:30:05 - executando física (20s)... │
│  ...                                   │
└────────────────────────────────────────┘
```

**etapas visuais:**
- ⏸️ **pendente** - ainda não iniciou (cinza, opaco)
- ⏳ **ativa** - executando agora (amarelo, pulsando)
- ✅ **concluída** - finalizado (verde)

### passo 4: conclusão

**ao terminar:**

```
┌────────────────────────────────────────┐
│ ✅ pipeline executado com sucesso!     │
├────────────────────────────────────────┤
│                                        │
│ arquivos gerados:                      │
│                                        │
│ arquivo .bed:                          │
│ output/meu_leito.bed                   │
│                                        │
│ parâmetros json:                       │
│ output/meu_leito.bed.json              │
│                                        │
│ modelo 3d:                             │
│ output/models/meu_leito.blend          │
│ output/models/meu_leito.glb            │
│ output/models/meu_leito.obj            │
│                                        │
│ caso cfd:                              │
│ output/cfd/sim_abc123/                 │
│                                        │
│ próximos passos:                       │
│ ▸ visualizar modelo 3d na aba          │
│ ▸ abrir caso openfoam no wsl           │
│ ▸ executar simulação: ./Allrun         │
│ ▸ visualizar no paraview               │
│                                        │
│ [executar novo pipeline] [voltar]      │
└────────────────────────────────────────┘
```

---

## fluxo detalhado

### etapa 1: compilação dsl (10-25%)

**o que acontece:**
```
1. frontend envia parametros → backend
2. backend gera arquivo .bed
3. backend chama bed_compiler_antlr_standalone.py
4. compilador valida sintaxe
5. compilador gera params.json
6. retorna caminhos dos arquivos
```

**tempo:** ~2-5 segundos

**log:**
```
16:30:00 - compilando arquivo .bed com antlr...
16:30:02 - ✓ arquivo .bed compilado: output/meu_leito.bed
16:30:02 - ✓ arquivo .json gerado: output/meu_leito.bed.json
```

### etapa 2: geração 3d (25-50%)

**o que acontece:**
```
1. backend chama blender headless
2. blender cria geometria (cilindro oco + tampas)
3. blender cria partículas
4. blender aplica física (mesh collision)
5. ⭐ blender executa animação (20s de física)
6. ⭐ blender faz bake (fixa posições)
7. blender salva arquivo .blend
8. blender exporta formatos selecionados
```

**tempo:** ~2-5 minutos (depende de partículas)

**log:**
```
16:30:05 - gerando modelo 3d no blender (com física)...
16:30:07 - executando animação de queda das partículas (20s)...
16:31:00 - progresso física: 50%
16:31:30 - ✓ animação de física executada e baked
16:31:35 - ✓ modelo 3d gerado: output/models/meu_leito.blend
16:31:40 -   ✓ exportado: blend
16:31:45 -   ✓ exportado: glb
16:31:50 -   ✓ exportado: obj
```

### etapa 3: preparação cfd (50-75%)

**o que acontece:**
```
1. backend chama setup_openfoam_case.py
2. script exporta stl do blender
3. script cria estrutura do caso openfoam
4. script copia stl para caso
5. script cria dicionários de malha
6. script cria dicionários de controle
7. script cria condições iniciais
8. script cria script Allrun
```

**tempo:** ~30-60 segundos

**log:**
```
16:32:00 - criando caso openfoam...
16:32:05 - exportando stl do blender...
16:32:10 - criando estrutura do caso...
16:32:15 - configurando malha...
16:32:20 - ✓ caso cfd criado: sim_abc123
```

### etapa 4: execução cfd (75-100%)

**o que acontece:**
```
1. backend monitora status da simulação
2. openfoam executa no wsl:
   - blockMesh (malha de fundo)
   - snappyHexMesh (malha refinada)
   - checkMesh (verificação)
   - simpleFoam (solver cfd)
3. polling a cada 3s
4. atualiza progresso
```

**tempo:** ~5-30 minutos (depende do caso)

**log:**
```
16:32:25 - executando simulação cfd...
16:32:30 - isso pode levar vários minutos...
16:35:00 -   preparando → 75%
16:40:00 -   gerando malha → 80%
16:45:00 -   executando → 90%
16:50:00 - ✓ simulação cfd concluída!
```

### etapa 5: conclusão (100%)

**o que acontece:**
```
1. exibe todos arquivos gerados
2. mostra próximos passos
3. disponibiliza ações
```

---

## endpoints utilizados

### 1. compilar dsl
```http
POST /api/bed/wizard
{
  "fileName": "meu_leito.bed",
  "mode": "interactive",
  "params": { ... }
}

→ retorna: bed_file, json_file
```

### 2. gerar modelo 3d
```http
POST /api/integrated/generate-model
{
  "json_file": "output/meu_leito.bed.json",
  "formats": ["blend", "glb", "obj"]
}

→ retorna: model_path, exported_formats
```

### 3. criar e executar cfd
```http
POST /api/cfd/run-from-wizard
{
  "fileName": "meu_leito.bed",
  "runSimulation": true
}

→ retorna: simulation_id, status_url
```

### 4. monitorar status
```http
GET /api/cfd/status/{simulation_id}

→ retorna: status, progress, message
```

---

## comparação: cli vs web

| aspecto | python cli | web pipeline |
|---------|------------|--------------|
| comandos | ~5-8 comandos | 1 clique |
| navegação | trocar diretórios | 1 página |
| monitoramento | terminal logs | interface visual |
| progresso | manual (tail -f) | barra animada |
| erros | stderr | interface clara |
| resultados | terminal | cards visuais |
| próximos passos | memorizar | mostrados |
| experiência | técnica | intuitiva |

**vantagem web:** automação total + feedback visual

---

## logs em tempo real

### tipos de log

**info (azul):**
```
16:30:00 - compilando arquivo .bed com antlr...
16:30:05 - gerando modelo 3d no blender...
```

**success (verde):**
```
16:30:02 - ✓ arquivo .bed compilado
16:31:35 - ✓ modelo 3d gerado
```

**warning (laranja):**
```
16:32:25 - isso pode levar vários minutos...
```

**error (vermelho):**
```
16:35:00 - ✗ erro: arquivo não encontrado
```

### estilo terminal

```css
background: #1e1e1e;
font-family: 'JetBrains Mono', monospace;
color: #ddd;
```

**features:**
- fundo preto (like terminal)
- fonte monospace
- cores por tipo
- scroll automático
- timestamps

---

## validação do pipeline cfd

### verificar se está funcionando

**teste rápido:**

1. **criar leito simples:**
   - usar wizard interativo
   - 50 partículas
   - incluir cfd: sim
   - regime: laminar
   - velocidade: 0.1 m/s

2. **executar pipeline:**
   - clicar "pipeline completo"
   - clicar "iniciar"
   - aguardar

3. **verificar logs:**
   ```
   ✓ arquivo .bed compilado
   ✓ arquivo .json gerado
   ✓ modelo 3d gerado
   ✓ caso cfd criado
   ✓ simulação cfd concluída
   ```

4. **verificar arquivos:**
   - `output/meu_leito.bed` - existe
   - `output/meu_leito.bed.json` - existe
   - `output/models/meu_leito.blend` - existe
   - `output/cfd/sim_XXX/` - existe

5. **abrir no wsl:**
   ```bash
   cd /mnt/c/Users/[seu_usuario]/Downloads/CFD-PIPELINE-TCC-1/output/cfd/sim_XXX
   ls -la
   ```
   
   **deve ter:**
   - `0/` (condições iniciais)
   - `constant/` (geometria, propriedades)
   - `system/` (configuração)
   - `Allrun` (script executável)

6. **executar simulação (se ainda não executou):**
   ```bash
   source /opt/openfoam11/etc/bashrc
   ./Allrun
   ```

7. **visualizar:**
   ```bash
   touch caso.foam
   paraview caso.foam &
   ```

**se tudo funcionar → ✅ pipeline cfd está funcionando!**

---

## troubleshooting

### erro: "backend connection error"

**causa:** backend não está rodando

**solução:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### erro: "compilação falhou"

**causa:** erro na sintaxe .bed ou antlr não configurado

**solução:**
- verificar parâmetros do wizard
- testar compilação manual:
```bash
cd dsl
python compiler/bed_compiler_antlr_standalone.py teste.bed -v
```

### erro: "modelo 3d não gerado"

**causa:** blender não encontrado ou erro na execução

**solução:**
- verificar se blender está instalado
- ver logs do backend (terminal)
- testar blender manual:
```bash
blender --version
```

### erro: "caso cfd não criado"

**causa:** arquivos não encontrados ou wsl não configurado

**solução:**
- verificar se .blend e .json existem
- verificar se wsl2 está instalado
- testar script manual:
```bash
cd scripts/openfoam_scripts
python setup_openfoam_case.py --help
```

### simulação travada em "executando"

**causa:** openfoam demorado ou erro no wsl

**solução:**
- aguardar mais tempo (pode levar 15-30min)
- verificar wsl manualmente:
```bash
wsl
cd /mnt/c/Users/.../output/cfd/sim_XXX
tail -f log.simpleFoam
```

---

## arquitetura do pipeline completo

### componente react

```jsx
PipelineCompleto.jsx
├── estado (etapaAtual, progresso, log)
├── iniciarPipeline()
│   ├── compilarDSL()
│   ├── gerarModelo3D()
│   ├── criarCasoCFD()
│   └── monitorarSimulacao()
├── renderInicio()
├── renderExecutando()
└── renderConcluido()
```

### fluxo de dados

```
┌─────────────┐
│   usuario   │ clica "iniciar"
└──────┬──────┘
       ↓
┌─────────────┐
│  frontend   │ chama endpoints sequencialmente
└──────┬──────┘
       ↓
┌─────────────┐
│   backend   │ orquestra processos
├─────────────┤
│ - routes_wizard.py (compilação)
│ - routes_integrated.py (blender)
│ - routes_cfd.py (openfoam)
└──────┬──────┘
       ↓
┌─────────────┐
│  processos  │ execução real
├─────────────┤
│ - antlr (compilador dsl)
│ - blender headless (física 20s)
│ - setup_openfoam_case.py
│ - wsl/openfoam (simulação)
└──────┬──────┘
       ↓
┌─────────────┐
│  frontend   │ exibe resultados
└─────────────┘
```

---

## tempos estimados

### caso pequeno (50 partículas)

| etapa | tempo |
|-------|-------|
| compilação dsl | ~2s |
| geração 3d | ~1-2min |
| preparação cfd | ~30s |
| execução cfd | ~5-10min |
| **total** | **~7-13min** |

### caso médio (100 partículas)

| etapa | tempo |
|-------|-------|
| compilação dsl | ~2s |
| geração 3d | ~3-5min |
| preparação cfd | ~1min |
| execução cfd | ~10-20min |
| **total** | **~14-26min** |

### caso grande (500+ partículas)

| etapa | tempo |
|-------|-------|
| compilação dsl | ~3s |
| geração 3d | ~15-30min |
| preparação cfd | ~2-3min |
| execução cfd | ~30-60min |
| **total** | **~47-93min** |

---

## monitoramento

### barra de progresso

```
progresso: [████████████░░░░░░] 65%
```

**mapeamento:**
- 0-10%: iniciando
- 10-25%: compilando dsl
- 25-50%: gerando 3d (física + bake)
- 50-75%: preparando cfd
- 75-100%: executando simulação
- 100%: concluído

### polling

```javascript
// verificar status a cada 3 segundos
setInterval(async () => {
  const status = await fetch('/api/cfd/status/sim_id');
  setProgresso(status.progress);
  adicionarLog(status.message);
}, 3000);
```

---

## personalização

### executar sem cfd

```javascript
// no wizard, desmarcar "incluir cfd"
includeCFD: false

// pipeline pula etapas 3-4
// vai direto para conclusão após blender
```

**resultado:**
- compilação (10-25%)
- geração 3d (25-100%)
- concluído

**tempo:** ~2-5 minutos

### escolher formatos

```javascript
// no passo 5 do wizard
formats: ['blend', 'glb', 'obj', 'stl']

// todos serão exportados
```

**impacto no tempo:**
- +10-30s por formato adicional
- blend + glb: ~1min
- blend + glb + obj + stl: ~2-3min

---

## próximas melhorias

### 1. cancelar execução

```jsx
<button onClick={cancelarPipeline}>
  cancelar pipeline
</button>
```

### 2. pausar/resumir

```jsx
<button onClick={pausarSimulacao}>
  pausar simulação
</button>
```

### 3. editar em tempo real

```jsx
// permitir ajustar parâmetros enquanto executa
// reiniciar do ponto de falha
```

### 4. histórico

```jsx
// salvar execuções anteriores
// comparar resultados
// replay de logs
```

### 5. notificações

```jsx
// notificar quando concluir
// usar Notification API
if (Notification.permission === "granted") {
  new Notification("Pipeline concluído!");
}
```

---

## dicas

### 1. começar pequeno
- 50 partículas
- tempo 10-15s
- testar pipeline completo
- depois aumentar

### 2. usar abas individuais
- testar cada etapa separada
- garantir que funciona
- depois usar pipeline completo

### 3. monitorar wsl
- abrir wsl em paralelo
- ver logs openfoam em tempo real
- detectar problemas cedo

### 4. salvar configurações
- exportar .bed de configurações que funcionam
- reusar para casos similares

---

## resumo

### o que o pipeline completo faz

✅ **automatiza** todo o processo
✅ **monitora** execução visual
✅ **registra** logs detalhados
✅ **valida** cada etapa
✅ **exibe** resultados claros

### quando usar

**pipeline completo:**
- workflow completo
- automação total
- casos padrão

**abas individuais:**
- debugging
- etapas específicas
- casos especiais

### status do cfd

**o pipeline cfd está funcionando?**

✅ **sim!** desde que:
1. wsl2 instalado
2. openfoam instalado no wsl
3. `setup_openfoam_case.py` configurado
4. caminhos corretos

**como confirmar:**
```bash
# testar manualmente primeiro
cd scripts/openfoam_scripts
python setup_openfoam_case.py \
  ../../dsl/leito.bed.json \
  ../../output/models/leito.blend

# se criar caso com sucesso → está funcionando!
```

---

## conclusão

**pipeline completo web implementado com sucesso!**

agora você tem:
- ✅ interface visual completa
- ✅ execução automatizada
- ✅ monitoramento em tempo real
- ✅ equivalente ao bed_wizard.py
- ✅ experiência superior

**um clique executa tudo!** 🚀

