# guia de integração postgresql

## visão geral

o backend agora está **totalmente integrado** com postgresql, permitindo:

1. salvar leitos, simulações e resultados no banco
2. consultar, filtrar e buscar dados
3. rastrear histórico completo
4. analisar estatísticas
5. pipeline automático que salva tudo no banco

---

## endpoints implementados

### 📦 crud de leitos (beds)

```
POST   /api/beds                    # criar leito
GET    /api/beds                    # listar leitos (paginado)
GET    /api/beds/{id}               # obter leito específico
PATCH  /api/beds/{id}               # atualizar leito
DELETE /api/beds/{id}               # deletar leito
GET    /api/beds/{id}/simulations   # listar simulações do leito
GET    /api/beds/{id}/summary       # resumo com estatísticas
```

### 🔬 crud de simulações (simulations)

```
POST   /api/simulations             # criar simulação
GET    /api/simulations             # listar simulações (paginado)
GET    /api/simulations/{id}        # obter simulação específica
PATCH  /api/simulations/{id}        # atualizar simulação
DELETE /api/simulations/{id}        # deletar simulação
```

**filtros disponíveis:**
- `?bed_id=1` - filtrar por leito
- `?status=completed` - filtrar por status
- `?page=2&per_page=20` - paginação

### 📊 crud de resultados (results)

```
POST   /api/results                             # criar resultado
POST   /api/results/bulk                        # criar múltiplos resultados
GET    /api/results/simulation/{simulation_id}  # listar resultados
GET    /api/results/{id}                        # obter resultado específico
DELETE /api/results/{id}                        # deletar resultado
```

### 🚀 pipeline integrado (novo!)

```
POST   /api/pipeline/create-bed     # cria leito + modelo + simulação
GET    /api/pipeline/job/{job_id}   # monitora progresso
```

### 📈 estatísticas

```
GET    /api/stats/overview          # estatísticas gerais do sistema
```

---

## exemplos de uso

### 1. criar leito manualmente

```python
import requests

# criar leito
response = requests.post('http://localhost:8000/api/beds', json={
    "name": "leito_cilindrico_teste",
    "description": "leito para validação experimental",
    "diameter": 0.05,
    "height": 0.1,
    "wall_thickness": 0.002,
    "particle_count": 500,
    "particle_diameter": 0.005,
    "particle_kind": "sphere",
    "packing_method": "rigid_body",
    "porosity": 0.42,
    "parameters_json": {
        "diameter": 0.05,
        "height": 0.1
    }
})

bed = response.json()
print(f"leito criado com id: {bed['id']}")
```

### 2. listar leitos com busca

```python
# buscar leitos por nome
response = requests.get(
    'http://localhost:8000/api/beds',
    params={
        'search': 'cilindrico',
        'page': 1,
        'per_page': 10
    }
)

result = response.json()
print(f"encontrados {result['total']} leitos")
for bed in result['items']:
    print(f"  - {bed['name']} (id: {bed['id']})")
```

### 3. criar simulação manualmente

```python
# criar simulação para bed_id=1
response = requests.post('http://localhost:8000/api/simulations', json={
    "bed_id": 1,
    "name": "sim_laminar_v01",
    "description": "simulação laminar, velocidade 0.01 m/s",
    "regime": "laminar",
    "inlet_velocity": 0.01,
    "fluid_density": 1000.0,
    "fluid_viscosity": 0.001,
    "solver": "simpleFoam",
    "max_iterations": 1000,
    "convergence_criteria": 0.0001,
    "case_directory": "output/simulations/leito_teste"
})

simulation = response.json()
print(f"simulação criada com id: {simulation['id']}")
```

### 4. atualizar simulação com resultados

```python
# atualizar simulação após execução
requests.patch(f'http://localhost:8000/api/simulations/{simulation_id}', json={
    "status": "completed",
    "progress": 100,
    "pressure_drop": 1250.5,
    "average_velocity": 0.012,
    "reynolds_number": 3542.8,
    "execution_time": 1847.3
})
```

### 5. criar resultados detalhados

```python
# salvar métricas
requests.post('http://localhost:8000/api/results', json={
    "simulation_id": 1,
    "result_type": "metric",
    "name": "pressure_drop",
    "value": 1250.5,
    "unit": "Pa"
})

# salvar perfil de velocidade
requests.post('http://localhost:8000/api/results', json={
    "simulation_id": 1,
    "result_type": "field",
    "name": "velocity_profile_z",
    "data_json": {
        "z": [0.0, 0.02, 0.04, 0.06, 0.08, 0.1],
        "velocity": [0.0, 0.08, 0.12, 0.12, 0.10, 0.05]
    },
    "unit": "m/s"
})

# salvar comparação com ergun
requests.post('http://localhost:8000/api/results', json={
    "simulation_id": 1,
    "result_type": "validation",
    "name": "ergun_comparison",
    "value": 0.95,  # r² correlation
    "data_json": {
        "experimental": [1200, 1350, 1500],
        "simulated": [1180, 1320, 1520],
        "deviation_percent": 3.2
    }
})
```

### 6. consultar histórico de um leito

```python
# obter resumo com estatísticas
response = requests.get('http://localhost:8000/api/beds/1/summary')
summary = response.json()

print(f"leito: {summary['bed']['name']}")
print(f"total simulações: {summary['simulations_count']}")
print(f"por status: {summary['simulations_by_status']}")
print(f"pressão média: {summary['average_metrics']['pressure_drop']:.2f} Pa")
```

### 7. usar pipeline integrado (recomendado!)

```python
# criar tudo de uma vez: leito + modelo 3d + simulação
response = requests.post('http://localhost:8000/api/pipeline/create-bed', json={
    "parameters": {
        "diameter": 0.05,
        "height": 0.1,
        "particle_count": 500,
        "particle_diameter": 0.005,
        "particle_type": "sphere",
        "packing_method": "rigid_body",
        "cfd_regime": "laminar",
        "inlet_velocity": 0.01
    },
    "generate_model": True,
    "run_simulation": True
})

job_id = response.json()['job_id']

# monitorar progresso
import time
while True:
    status = requests.get(f'http://localhost:8000/api/pipeline/job/{job_id}')
    job = status.json()
    
    print(f"status: {job['status']}, progresso: {job['progress']}%")
    
    if job['status'] in ['completed', 'failed']:
        break
    
    time.sleep(2)

# ao completar, tudo está salvo no banco!
if job['status'] == 'completed':
    bed_id = job['metadata']['bed_id']
    simulation_id = job['metadata']['simulation_id']
    
    print(f"leito salvo: id={bed_id}")
    print(f"simulação salva: id={simulation_id}")
```

### 8. estatísticas gerais

```python
response = requests.get('http://localhost:8000/api/stats/overview')
stats = response.json()

print(f"total leitos: {stats['total_beds']}")
print(f"total simulações: {stats['total_simulations']}")
print(f"total resultados: {stats['total_results']}")
print(f"simulações por status: {stats['simulations_by_status']}")
```

---

## modificações nos serviços

### bed_service.py

agora aceita parâmetros opcionais:

```python
await bed_service.compile_bed(
    parameters=params,
    save_to_db=True,      # salvar no banco
    db_session=db         # sessão do banco
)
```

retorna `bed_id` se `save_to_db=True`

### blender_service.py

agora aceita bed_id opcional:

```python
await blender_service.generate_model(
    job_id=job_id,
    json_file="...",
    open_blender=False,
    jobs_store=jobs,
    bed_id=1,             # atualiza bed com blend_file_path
    db_session=db
)
```

atualiza `blend_file_path` no bed automaticamente

### openfoam_service.py

agora aceita bed_id opcional:

```python
await openfoam_service.create_case(
    job_id=job_id,
    json_file="...",
    blend_file="...",
    run_simulation=False,
    jobs_store=jobs,
    bed_id=1,             # cria simulação no banco
    db_session=db
)
```

cria registro de simulação automaticamente

---

## benefícios

### antes (sem banco)

```
usuário cria leito
↓
arquivos .bed, .bed.json gerados
↓
modelo .blend gerado
↓
caso openfoam criado
↓
arquivos espalhados, sem rastreabilidade
❌ não sabe quais simulações já rodou
❌ não consegue comparar resultados
❌ não tem histórico
```

### agora (com banco)

```
usuário cria leito
↓
arquivos gerados E salvo no banco (bed_id=1)
↓
modelo gerado E atualizado no banco (blend_file_path)
↓
caso criado E simulação registrada (simulation_id=5)
↓
resultados salvos (metrics, fields, validations)
✅ sabe exatamente o que foi feito
✅ pode comparar simulações facilmente
✅ histórico completo rastreável
✅ estatísticas e análises
```

---

## queries úteis (sql direto)

### buscar leitos com maior número de simulações

```sql
SELECT 
    b.id, 
    b.name, 
    COUNT(s.id) as sim_count
FROM beds b
LEFT JOIN simulations s ON b.id = s.bed_id
GROUP BY b.id, b.name
ORDER BY sim_count DESC
LIMIT 10;
```

### comparar perda de carga entre configurações

```sql
SELECT 
    b.name,
    b.particle_count,
    AVG(s.pressure_drop) as avg_pressure_drop
FROM beds b
JOIN simulations s ON b.id = s.bed_id
WHERE s.status = 'completed'
GROUP BY b.name, b.particle_count
ORDER BY avg_pressure_drop;
```

### encontrar melhores configurações (menor perda de carga)

```sql
SELECT 
    b.name,
    s.inlet_velocity,
    s.pressure_drop,
    s.reynolds_number
FROM simulations s
JOIN beds b ON s.bed_id = b.id
WHERE s.status = 'completed'
  AND s.pressure_drop IS NOT NULL
ORDER BY s.pressure_drop ASC
LIMIT 10;
```

---

## próximos passos

### 1. pós-processamento automático

criar serviço que:
- lê resultados openfoam (pressure, velocity)
- calcula métricas (perda de carga, velocidade média)
- salva em `results` table

### 2. validação automática

comparar resultados com:
- equação de ergun
- dados experimentais
- salvar em `results` com `result_type='validation'`

### 3. dashboard com métricas

frontend react que mostra:
- gráficos de perda de carga vs velocidade
- comparação entre configurações
- validação com modelos teóricos
- histórico temporal

### 4. migrar jobs para postgresql

em vez de `jobs_store: dict`, salvar jobs no banco:
- persistência após restart
- monitoramento distribuído
- histórico de execuções

---

## troubleshooting

### erro: "database connection refused"

certifique-se que postgresql está rodando:

```bash
# windows (powershell)
Get-Service -Name postgresql*

# se não estiver rodando:
Start-Service postgresql-x64-16
```

### erro: "tables do not exist"

execute o script de inicialização:

```bash
cd backend
python scripts/init_database.py
```

### erro: "bed_id not found"

certifique-se de criar o bed primeiro:

```python
# 1. criar bed
bed_response = requests.post('/api/beds', json={...})
bed_id = bed_response.json()['id']

# 2. usar bed_id
requests.post('/api/simulations', json={
    "bed_id": bed_id,  # usar id do bed criado
    ...
})
```

---

## resumo

**novo workflow recomendado:**

```python
# opção 1: pipeline automático (mais fácil)
response = requests.post('/api/pipeline/create-bed', json={
    "parameters": {...},
    "generate_model": True,
    "run_simulation": True
})

# opção 2: passo a passo com controle fino
bed = requests.post('/api/beds', json={...})
simulation = requests.post('/api/simulations', json={...})
results = requests.post('/api/results/bulk', json=[...])
```

**consultas:**

```python
# listar tudo
beds = requests.get('/api/beds').json()
simulations = requests.get('/api/simulations').json()

# filtrar
my_beds = requests.get('/api/beds', params={'search': 'cilindrico'}).json()
completed_sims = requests.get('/api/simulations', params={'status': 'completed'}).json()

# análises
summary = requests.get(f'/api/beds/{bed_id}/summary').json()
stats = requests.get('/api/stats/overview').json()
```

**tudo está salvo, rastreável e consultável!** 🚀

