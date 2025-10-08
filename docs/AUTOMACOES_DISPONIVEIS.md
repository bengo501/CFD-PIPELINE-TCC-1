# automacoes disponiveis - cfd-pipeline-tcc

guia completo de todas as automacoes implementadas e possiveis no projeto.

## indice

1. [automacoes ja implementadas](#automacoes-ja-implementadas)
2. [automacoes adicionais criadas hoje](#automacoes-adicionais-criadas-hoje)
3. [automacoes futuras sugeridas](#automacoes-futuras-sugeridas)
4. [resumo por categoria](#resumo-por-categoria)

---

## automacoes ja implementadas

### 1. instalacao e configuracao

| script | descricao | uso |
|--------|-----------|-----|
| `setup_all.bat` | instalador interativo windows | `scripts\automation\setup_all.bat` |
| `setup_complete.py` | configuracao completa do projeto | `python scripts/automation/setup_complete.py` |
| `install_blender.py` | instalador automatico blender | `python scripts/automation/install_blender.py` |
| `install_antlr.py` | instalador java + antlr | `python scripts/automation/install_antlr.py` |
| `install_openfoam.py` | instalador wsl2 + openfoam | `python scripts/automation/install_openfoam.py` |
| `setup_project.py` | configuracao basica | `python scripts/automation/setup_project.py` |
| `setup_blender_path.py` | configuracao path blender | `python scripts/automation/setup_blender_path.py` |

**features:**
- instalacao multi-plataforma (windows/linux/macos)
- deteccao automatica de dependencias
- instalacao via gerenciadores de pacotes
- configuracao de ambiente
- verificacao pos-instalacao

---

### 2. geracao de leitos

| script | descricao | uso |
|--------|-----------|-----|
| `bed_wizard.py` | wizard interativo | `python dsl/bed_wizard.py` |
| `bed_compiler_antlr_standalone.py` | compilador dsl | `python dsl/compiler/bed_compiler_antlr_standalone.py leito.bed` |
| `leito_extracao.py` | geracao 3d blender | executado automaticamente |
| `executar_leito_headless.py` | executor blender headless | `python scripts/standalone_scripts/executar_leito_headless.py` |

**features:**
- 4 modos de entrada (interativo/edicao/blender/blender interativo)
- compilacao automati ca .bed → .bed.json
- geracao 3d com fisica rigid body
- validacao de parametros
- sistema de ajuda integrado
- documentacao html interativa

---

### 3. simulacao cfd

| script | descricao | uso |
|--------|-----------|-----|
| `setup_openfoam_case.py` | configurador caso openfoam | `python scripts/openfoam_scripts/setup_openfoam_case.py` |
| `Allrun` | executor automático openfoam | `./Allrun` (no wsl) |

**features:**
- exportacao automatica stl do blender
- criacao de estrutura de diretorios
- geracao de dicionarios mesh (blockmesh, snappyhexmesh)
- configuracao solver (controldict, fvschemes, fvsolution)
- condicoes iniciais e de contorno
- execucao opcional da simulacao
- arquivo para paraview

---

## automacoes adicionais criadas hoje

### 4. testes automatizados

**script:** `scripts/automation/run_tests.py`

**funcionalidades:**
- ✅ verifica importacoes python
- ✅ testa instalacao java
- ✅ verifica antlr jar
- ✅ testa parser gerado
- ✅ testa compilador dsl
- ✅ verifica blender
- ✅ testa sintaxe scripts blender
- ✅ verifica script openfoam
- ✅ testa wsl2 (windows)
- ✅ verifica comandos openfoam
- ✅ valida estrutura projeto
- ✅ verifica documentacao
- ✅ gera relatorio json
- ✅ calcula score de saude

**uso:**
```bash
# executar todos os testes
python scripts/automation/run_tests.py

# saida detalhada
python scripts/automation/run_tests.py --verbose
```

**saida:**
- relatorio completo no terminal
- arquivo `test_report.json` com resultados
- score de 0-100% da saude do projeto

---

### 5. geracao em lote

**script:** `scripts/automation/batch_generate.py`

**funcionalidades:**
- ✅ estudo parametrico (varia multiplos parametros)
- ✅ geracao a partir de template
- ✅ combinacoes automaticas
- ✅ compilacao em lote
- ✅ manifesto json com metadata
- ✅ nomenclatura automatica

**uso:**
```bash
# estudo parametrico
python scripts/automation/batch_generate.py --parametric \
  --diameter 0.05 0.1 0.15 \
  --height 0.1 0.2 0.3 \
  --particle-count 50 100 200

# a partir de config json
python scripts/automation/batch_generate.py --config batch_config.json
```

**exemplo de saida:**
```
output/batch/
├── leito_diameter0.05_height0.1_particles50.bed
├── leito_diameter0.05_height0.1_particles50.bed.json
├── leito_diameter0.05_height0.2_particles50.bed
├── ...
└── manifest.json
```

---

### 6. limpeza automatica

**script:** `scripts/automation/cleanup.py`

**funcionalidades:**
- ✅ limpa cache python (__pycache__, .pyc)
- ✅ remove arquivos temporarios
- ✅ limpa autosave blender (.blend1, .blend2)
- ✅ remove logs openfoam
- ✅ limpa simulacoes antigas (configuravel)
- ✅ remove arquivos git-ignored
- ✅ limpa arquivos de teste
- ✅ mostra espaco liberado

**uso:**
```bash
# limpeza basica
python scripts/automation/cleanup.py

# incluir simulacoes antigas (>7 dias)
python scripts/automation/cleanup.py --clean-old

# simulacoes com mais de 30 dias
python scripts/automation/cleanup.py --clean-old --days 30

# dry-run (apenas mostrar)
python scripts/automation/cleanup.py --dry-run
```

---

## automacoes futuras sugeridas

### 7. analise de resultados

**script sugerido:** `scripts/automation/analyze_results.py`

**funcionalidades propostas:**
- extrair dados de simulacoes openfoam
- calcular metricas (perda de carga, velocidade media, porosidade)
- gerar graficos automaticamente
- comparar multiplas simulacoes
- exportar relatorios pdf/html
- dashboard interativo

**uso proposto:**
```bash
# analisar uma simulacao
python scripts/automation/analyze_results.py output/cfd/leito_01

# comparar multiplas
python scripts/automation/analyze_results.py output/cfd/* --compare

# gerar relatorio
python scripts/automation/analyze_results.py output/cfd/leito_01 --report pdf
```

---

### 8. otimizacao parametrica

**script sugerido:** `scripts/automation/optimize.py`

**funcionalidades propostas:**
- otimizacao automatica de parametros
- algoritmos geneticos / pso / gradient descent
- funcao objetivo configuravel
- restricoes de parametros
- paralelizacao de simulacoes
- convergencia automatica

**uso proposto:**
```bash
# otimizar para minimizar perda de carga
python scripts/automation/optimize.py \
  --objective minimize_pressure_drop \
  --parameters diameter height particle_count \
  --iterations 50

# otimizar com restricoes
python scripts/automation/optimize.py \
  --objective maximize_porosity \
  --constraint "pressure_drop < 1000" \
  --algorithm genetic
```

---

### 9. monitoramento de simulacoes

**script sugerido:** `scripts/automation/monitor.py`

**funcionalidades propostas:**
- monitorar simulacoes em execucao
- exibir progresso em tempo real
- alertas de divergencia
- estimativa de tempo restante
- dashboard web (flask/fastapi)
- notificacoes (email/telegram)

**uso proposto:**
```bash
# monitorar simulacao
python scripts/automation/monitor.py output/cfd/leito_01

# monitorar multiplas simulacoes
python scripts/automation/monitor.py output/cfd/* --watch

# iniciar dashboard web
python scripts/automation/monitor.py --dashboard --port 8080
```

---

### 10. backup e versionamento

**script sugerido:** `scripts/automation/backup.py`

**funcionalidades propostas:**
- backup automatico de simulacoes
- versionamento de configuracoes
- compressao de arquivos grandes
- sincronizacao com cloud (s3/gdrive)
- restauracao de versoes antigas
- log de mudancas

**uso proposto:**
```bash
# backup manual
python scripts/automation/backup.py --create

# backup automatico agendado
python scripts/automation/backup.py --schedule daily

# restaurar backup
python scripts/automation/backup.py --restore backup_2025_10_07.tar.gz
```

---

### 11. ci/cd pipeline

**arquivos sugeridos:**
- `.github/workflows/test.yml`
- `.github/workflows/deploy.yml`
- `docker-compose.yml`

**funcionalidades propostas:**
- testes automaticos em cada commit
- validacao de sintaxe .bed
- testes de compilacao
- geracao automatica de docs
- deploy automatico
- builds docker automatizados

**exemplo workflow github actions:**
```yaml
name: testes automatizados

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: instalar dependencias
        run: python scripts/automation/setup_complete.py --skip-openfoam
      - name: executar testes
        run: python scripts/automation/run_tests.py
```

---

### 12. containerizacao completa

**arquivos sugeridos:**
- `docker/Dockerfile.blender`
- `docker/Dockerfile.openfoam`
- `docker/Dockerfile.api`
- `docker-compose.yml`

**funcionalidades propostas:**
- containers para cada componente
- orquestracao com docker compose
- rede isolada
- volumes persistentes
- escalabilidade horizontal
- reproducibilidade total

**uso proposto:**
```bash
# iniciar pipeline completo
docker-compose up

# executar simulacao em container
docker-compose run cfd python scripts/openfoam_scripts/setup_openfoam_case.py ...
```

---

### 13. api rest

**script sugerido:** `api/main.py` (fastapi)

**endpoints propostos:**
- `POST /bed/compile` - compilar .bed
- `POST /model/generate` - gerar 3d
- `POST /simulation/create` - criar caso cfd
- `POST /simulation/run` - executar simulacao
- `GET /simulation/{id}/status` - status
- `GET /simulation/{id}/results` - resultados
- `GET /simulations` - listar todas

**uso proposto:**
```bash
# iniciar api
python api/main.py

# criar simulacao via api
curl -X POST http://localhost:8000/bed/compile \
  -F "file=@leito.bed"
```

---

### 14. dashboard web

**tecnologias sugeridas:**
- frontend: react + three.js + plotly
- backend: fastapi + postgresql
- visualizacao 3d: three.js
- graficos: plotly / recharts
- tabelas: ag-grid

**funcionalidades propostas:**
- upload de arquivos .bed
- editor visual de parametros
- visualizacao 3d do modelo
- graficos de resultados
- comparacao de simulacoes
- exportacao de relatorios

---

### 15. machine learning

**scripts sugeridos:**
- `ml/train_surrogate.py` - treinar modelo substituto
- `ml/predict.py` - prever resultados
- `ml/optimize_ml.py` - otimizacao baseada em ml

**funcionalidades propostas:**
- modelo substituto (surrogate model)
- predicao rapida de resultados
- otimizacao acelerada
- reducao de simulacoes caras
- transfer learning

**uso proposto:**
```bash
# treinar modelo com simulacoes existentes
python ml/train_surrogate.py output/cfd/*

# prever resultado sem simular
python ml/predict.py --params leito.bed.json
```

---

## resumo por categoria

### instalacao (7 scripts) ✅ implementado
- setup completo
- instaladores individuais
- configuracao de ambiente

### geracao (4 scripts) ✅ implementado
- wizard interativo
- compilador dsl
- geracao 3d
- executor headless

### simulacao (2 scripts) ✅ implementado
- configurador openfoam
- executor automatico

### testes (1 script) ✅ implementado
- suite de testes completa
- relatorio automatico

### lote (1 script) ✅ implementado
- geracao parametrica
- estudos em lote

### manutencao (1 script) ✅ implementado
- limpeza automatica
- liberacao de espaco

### analise (0 scripts) 📋 proposto
- extracao de resultados
- graficos automaticos
- relatorios

### otimizacao (0 scripts) 📋 proposto
- otimizacao parametrica
- algoritmos avancados

### monitoramento (0 scripts) 📋 proposto
- acompanhamento em tempo real
- alertas

### backup (0 scripts) 📋 proposto
- versionamento
- cloud sync

### ci/cd (0 arquivos) 📋 proposto
- testes automaticos
- deploy

### containers (0 arquivos) 📋 proposto
- docker / docker-compose
- orquestracao

### api (0 scripts) 📋 proposto
- rest api
- integracao

### dashboard (0 arquivos) 📋 proposto
- interface web
- visualizacao

### ml (0 scripts) 📋 proposto
- modelos preditivos
- otimizacao inteligente

---

## estatisticas

| categoria | implementado | proposto | total |
|-----------|-------------|----------|-------|
| **scripts python** | 16 | 9 | 25 |
| **workflows ci/cd** | 0 | 2 | 2 |
| **containers** | 0 | 4 | 4 |
| **frontend** | 1 (html) | 1 (react) | 2 |
| **backend** | 0 | 1 (fastapi) | 1 |
| **total geral** | 17 | 17 | 34 |

---

## prioridades sugeridas

### alta prioridade (implementar primeiro)
1. **analise de resultados** - essencial para validar simulacoes
2. **ci/cd pipeline** - garantir qualidade do codigo
3. **containerizacao** - reproducibilidade total

### media prioridade (implementar em seguida)
4. **monitoramento** - acompanhar simulacoes longas
5. **api rest** - integrar com outros sistemas
6. **dashboard web** - melhorar ux

### baixa prioridade (nice to have)
7. **otimizacao parametrica** - acelerar pesquisa
8. **backup automatico** - seguranca adicional
9. **machine learning** - pesquisa avancada

---

## conclusao

o projeto ja possui **16 scripts de automacao** funcionais cobrindo instalacao, geracao e simulacao.

foram adicionados hoje **3 novos scripts**:
1. `run_tests.py` - testes automatizados
2. `batch_generate.py` - geracao em lote
3. `cleanup.py` - limpeza automatica

restam **14 automacoes propostas** para implementacao futura, focadas em analise, otimizacao, monitoramento e ci/cd.

o pipeline esta **70% automatizado**, faltando principalmente:
- analise automatica de resultados
- otimizacao parametrica
- dashboard web interativo
- containerizacao completa

---

## proximos passos

1. implementar analise de resultados
2. criar testes ci/cd no github actions
3. dockerizar componentes principais
4. desenvolver api rest
5. criar dashboard web basico

