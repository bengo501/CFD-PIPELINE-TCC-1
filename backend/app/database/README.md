# banco de dados postgresql - documentacao

## 📊 visao geral

implementacao do banco de dados postgresql para o pipeline cfd usando sqlalchemy orm.

### estrutura

```
database/
├── __init__.py          # inicializacao do modulo
├── connection.py        # gerenciamento de conexao
├── models.py            # modelos orm (tabelas)
├── schemas.py           # schemas pydantic (validacao)
├── crud.py              # operacoes crud
└── README.md            # esta documentacao
```

---

## 🗄️ modelos (tabelas)

### 1. beds (leitos empacotados)

armazena configuracoes de leitos gerados pela dsl.

**campos principais:**
- `id`: identificador unico
- `name`: nome do leito
- `diameter`, `height`, `wall_thickness`: geometria
- `particle_count`, `particle_diameter`: particulas
- `packing_method`: metodo de empacotamento
- `porosity`: porosidade calculada

**arquivos associados:**
- `bed_file_path`: arquivo `.bed`
- `json_file_path`: arquivo `.bed.json`
- `blend_file_path`: arquivo `.blend`
- `stl_file_path`: arquivo `.stl`

**metadados:**
- `created_at`, `updated_at`: timestamps
- `created_by`: usuario que criou
- `parameters_json`: parametros completos em json

### 2. simulations (simulacoes cfd)

armazena simulacoes openfoam executadas.

**campos principais:**
- `id`: identificador unico
- `bed_id`: foreign key para beds
- `name`: nome da simulacao
- `regime`: laminar ou turbulent
- `inlet_velocity`: velocidade de entrada (m/s)
- `fluid_density`, `fluid_viscosity`: propriedades do fluido

**configuracao:**
- `mesh_cells_count`: numero de celulas da malha
- `solver`: solver usado (simpleFoam, etc)
- `max_iterations`: iteracoes maximas
- `convergence_criteria`: criterio de convergencia

**status:**
- `status`: pending, running, completed, failed
- `progress`: 0-100%

**resultados:**
- `pressure_drop`: perda de carga (Pa)
- `average_velocity`: velocidade media (m/s)
- `reynolds_number`: numero de reynolds

**tempos:**
- `started_at`, `completed_at`: timestamps
- `execution_time`: tempo de execucao (segundos)

### 3. results (resultados detalhados)

armazena campos, metricas e pos-processamento.

**campos principais:**
- `id`: identificador unico
- `simulation_id`: foreign key para simulations
- `result_type`: field, metric, validation, visualization
- `name`: nome do campo ou metrica
- `value`: valor escalar
- `unit`: unidade fisica

**dados:**
- `data_json`: dados completos (arrays, vetores)
- `file_path`: arquivo associado
- `file_type`: vtk, csv, png, etc
- `timestep`: para resultados transientes

---

## 🔗 relacionamentos

```
beds (1) ──┬──> (N) simulations
           │
simulations (1) ──> (N) results
```

- um leito pode ter multiplas simulacoes
- uma simulacao pertence a um leito
- uma simulacao pode ter multiplos resultados
- um resultado pertence a uma simulacao

---

## 📝 schemas pydantic

schemas para validacao de entrada/saida:

### beds
- `BedBase`: campos base
- `BedCreate`: criar leito
- `BedUpdate`: atualizar leito
- `BedResponse`: resposta da api

### simulations
- `SimulationBase`: campos base
- `SimulationCreate`: criar simulacao
- `SimulationUpdate`: atualizar simulacao
- `SimulationResponse`: resposta da api

### results
- `ResultBase`: campos base
- `ResultCreate`: criar resultado
- `ResultResponse`: resposta da api

### listagem
- `BedListResponse`: lista paginada de leitos
- `SimulationListResponse`: lista paginada de simulacoes
- `ResultListResponse`: lista paginada de resultados

---

## ⚙️ operacoes crud

### BedCRUD

```python
from app.database import BedCRUD, get_db
from app.database.schemas import BedCreate

# criar leito
bed_data = BedCreate(
    name="leito_01",
    diameter=0.05,
    height=0.1,
    wall_thickness=0.002,
    particle_count=100,
    particle_diameter=0.005,
    particle_kind="sphere",
    packing_method="rigid_body"
)
bed = BedCRUD.create(db, bed_data)

# obter leito
bed = BedCRUD.get(db, bed_id=1)

# listar leitos
beds, total = BedCRUD.get_all(db, skip=0, limit=50)

# atualizar leito
bed = BedCRUD.update(db, bed_id=1, bed_update={"porosity": 0.42})

# deletar leito
BedCRUD.delete(db, bed_id=1)

# buscar leitos
beds, total = BedCRUD.search(db, query="cilindrico")
```

### SimulationCRUD

```python
from app.database import SimulationCRUD
from app.database.schemas import SimulationCreate

# criar simulacao
sim_data = SimulationCreate(
    bed_id=1,
    name="sim_laminar_01",
    regime="laminar",
    inlet_velocity=0.1,
    fluid_density=1.2,
    fluid_viscosity=1.8e-5
)
simulation = SimulationCRUD.create(db, sim_data)

# listar por leito
sims, total = SimulationCRUD.get_by_bed(db, bed_id=1)

# listar por status
sims, total = SimulationCRUD.get_by_status(db, status="completed")

# atualizar status
SimulationCRUD.update(db, sim_id=1, {"status": "running", "progress": 50})
```

### ResultCRUD

```python
from app.database import ResultCRUD
from app.database.schemas import ResultCreate

# criar resultado
result_data = ResultCreate(
    simulation_id=1,
    result_type="metric",
    name="pressure_drop",
    value=1250.5,
    unit="Pa"
)
result = ResultCRUD.create(db, result_data)

# criar multiplos resultados
results = ResultCRUD.create_bulk(db, [result1, result2, result3])

# listar resultados de simulacao
results = ResultCRUD.get_by_simulation(db, simulation_id=1)

# listar por tipo
metrics = ResultCRUD.get_by_simulation(db, simulation_id=1, result_type="metric")
```

---

## 🚀 setup inicial

### 1. instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. configurar banco de dados

copiar arquivo de exemplo:
```bash
cp env.example .env
```

editar `.env`:
```
DATABASE_URL=postgresql://cfd_user:cfd_password@localhost:5432/cfd_pipeline
```

### 3. iniciar postgresql

**docker compose (recomendado):**
```bash
docker-compose up -d postgres
```

**manual:**
```bash
# criar usuario e banco
sudo -u postgres psql

CREATE USER cfd_user WITH PASSWORD 'cfd_password';
CREATE DATABASE cfd_pipeline OWNER cfd_user;
GRANT ALL PRIVILEGES ON DATABASE cfd_pipeline TO cfd_user;
```

### 4. criar tabelas

```bash
python scripts/init_database.py
```

### 5. verificar

```python
from app.database import DatabaseConnection

# verificar conexao
if DatabaseConnection.check_connection():
    print("conectado!")

# criar tabelas
DatabaseConnection.create_tables()
```

---

## 🔌 integracao com fastapi

### dependency injection

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db, BedCRUD

@app.get("/beds/{bed_id}")
def get_bed(bed_id: int, db: Session = Depends(get_db)):
    bed = BedCRUD.get(db, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="bed not found")
    return bed
```

### exemplo completo

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, BedCRUD, schemas

app = FastAPI()

@app.post("/beds/", response_model=schemas.BedResponse)
def create_bed(bed: schemas.BedCreate, db: Session = Depends(get_db)):
    return BedCRUD.create(db, bed)

@app.get("/beds/", response_model=schemas.BedListResponse)
def list_beds(page: int = 1, per_page: int = 50, db: Session = Depends(get_db)):
    skip = (page - 1) * per_page
    beds, total = BedCRUD.get_all(db, skip=skip, limit=per_page)
    pages = math.ceil(total / per_page)
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
        "items": beds
    }

@app.get("/beds/{bed_id}", response_model=schemas.BedResponse)
def get_bed(bed_id: int, db: Session = Depends(get_db)):
    bed = BedCRUD.get(db, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="bed not found")
    return bed
```

---

## 📊 indices e performance

indices criados automaticamente:

```python
# indices primarios
beds.id
simulations.id
results.id

# indices foreign keys
simulations.bed_id
results.simulation_id

# indices de busca
beds.name
simulations.name

# indices compostos
(simulations.bed_id, simulations.status)
(results.simulation_id, results.result_type)
```

---

## 🔄 migrations (futuro)

para gerenciar mudancas de schema, usar alembic:

```bash
# inicializar alembic
alembic init alembic

# criar migration
alembic revision --autogenerate -m "add column"

# aplicar migrations
alembic upgrade head

# reverter migration
alembic downgrade -1
```

---

## 📚 referencias

- sqlalchemy: https://docs.sqlalchemy.org/
- pydantic: https://docs.pydantic.dev/
- postgresql: https://www.postgresql.org/docs/
- alembic: https://alembic.sqlalchemy.org/

---

**ultima atualizacao:** 9 outubro 2025

