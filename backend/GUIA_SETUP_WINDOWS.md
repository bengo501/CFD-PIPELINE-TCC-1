# guia de setup do banco de dados no windows

## 🔧 problema identificado

docker daemon não está rodando no windows.

---

## 🚀 opções de instalação

### opção 1: postgresql nativo windows (recomendado)

#### passo 1: baixar postgresql

1. acesse: https://www.postgresql.org/download/windows/
2. baixe o instalador (versão 14 ou superior)
3. execute o instalador

#### passo 2: instalar postgresql

durante a instalação:
- **senha do superuser (postgres):** defina uma senha (ex: postgres123)
- **porta:** 5432 (padrão)
- **locale:** Portuguese, Brazil
- **componentes:** selecione todos

#### passo 3: criar usuário e banco

abra "SQL Shell (psql)" do menu iniciar:

```sql
-- conectar (use senha definida na instalação)
-- Server: localhost
-- Database: postgres
-- Port: 5432
-- Username: postgres
-- Password: [sua senha]

-- criar usuário
CREATE USER cfd_user WITH PASSWORD 'cfd_password';

-- criar banco de dados
CREATE DATABASE cfd_pipeline OWNER cfd_user;

-- conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE cfd_pipeline TO cfd_user;

-- verificar
\l
\q
```

#### passo 4: atualizar .env

edite `backend/.env`:

```env
DATABASE_URL=postgresql://cfd_user:cfd_password@localhost:5432/cfd_pipeline
```

#### passo 5: criar tabelas

no powershell (dentro da pasta backend):

```powershell
# voltar para a raiz do projeto
cd C:\Users\joxto\Downloads\CFD-PIPELINE-TCC-1

# executar script de inicialização
python backend\scripts\init_database.py
```

---

### opção 2: docker desktop (se preferir docker)

#### passo 1: instalar docker desktop

1. baixe: https://www.docker.com/products/docker-desktop/
2. instale e reinicie o computador
3. abra docker desktop e aguarde inicializar
4. verifique se está rodando (ícone na bandeja)

#### passo 2: iniciar postgresql

```powershell
# voltar para a raiz
cd C:\Users\joxto\Downloads\CFD-PIPELINE-TCC-1

# iniciar postgres
docker-compose up -d postgres

# verificar se está rodando
docker ps
```

#### passo 3: criar tabelas

```powershell
python backend\scripts\init_database.py
```

---

### opção 3: postgresql via wsl2 (avançado)

se você já usa wsl2 para openfoam:

```bash
# no wsl2
sudo apt update
sudo apt install postgresql postgresql-contrib

# iniciar serviço
sudo service postgresql start

# criar usuário e banco
sudo -u postgres psql
CREATE USER cfd_user WITH PASSWORD 'cfd_password';
CREATE DATABASE cfd_pipeline OWNER cfd_user;
\q
```

atualizar `.env`:
```env
DATABASE_URL=postgresql://cfd_user:cfd_password@localhost:5432/cfd_pipeline
```

---

## ✅ verificar instalação

### teste rápido python

crie arquivo `backend/test_db.py`:

```python
from app.database import DatabaseConnection

print("testando conexão...")

if DatabaseConnection.check_connection():
    print("✓ conectado ao postgresql!")
    
    print("\ncriando tabelas...")
    DatabaseConnection.create_tables()
    print("✓ tabelas criadas!")
else:
    print("✗ falha na conexão")
    print("\nverifique:")
    print("- postgresql está rodando")
    print("- .env está configurado corretamente")
    print("- usuário e senha estão corretos")
```

executar:

```powershell
# da raiz do projeto
cd C:\Users\joxto\Downloads\CFD-PIPELINE-TCC-1
python backend\test_db.py
```

---

## 🔍 troubleshooting

### erro: "could not connect"

**causa:** postgresql não está rodando

**solução:**
```powershell
# verificar se está rodando
# windows: services.msc → PostgreSQL
# ou
pg_isready -h localhost -p 5432
```

### erro: "password authentication failed"

**causa:** senha incorreta no .env

**solução:**
- verificar senha no arquivo `.env`
- resetar senha do usuário se necessário

### erro: "psycopg2 not installed"

**causa:** biblioteca não instalada

**solução:**
```powershell
pip install psycopg2-binary
```

### erro: "database does not exist"

**causa:** banco não foi criado

**solução:**
```powershell
# conectar ao psql e criar banco
# SQL Shell (psql)
CREATE DATABASE cfd_pipeline OWNER cfd_user;
```

---

## 📝 comandos úteis postgresql

### conectar ao banco

```powershell
# via psql (instalar postgresql tools)
psql -U cfd_user -d cfd_pipeline -h localhost

# listar bancos
\l

# listar tabelas
\dt

# descrever tabela
\d beds

# sair
\q
```

### backup e restore

```powershell
# backup
pg_dump -U cfd_user -h localhost cfd_pipeline > backup.sql

# restore
psql -U cfd_user -h localhost cfd_pipeline < backup.sql
```

### resetar banco (cuidado!)

```powershell
# conectar como postgres
psql -U postgres -h localhost

# dropar e recriar
DROP DATABASE cfd_pipeline;
CREATE DATABASE cfd_pipeline OWNER cfd_user;
\q

# recriar tabelas
python backend\scripts\init_database.py
```

---

## 🎯 próximo passo: após setup bem-sucedido

1. **testar conexão:**
   ```powershell
   python backend\test_db.py
   ```

2. **iniciar api:**
   ```powershell
   cd backend
   uvicorn app.main:app --reload
   ```

3. **acessar swagger:**
   http://localhost:8000/docs

4. **testar endpoints:**
   - criar leito via api
   - criar simulação
   - visualizar dados

---

## 📚 recursos adicionais

- **postgresql windows:** https://www.postgresql.org/docs/current/install-windows.html
- **docker desktop:** https://docs.docker.com/desktop/install/windows-install/
- **sqlalchemy:** https://docs.sqlalchemy.org/
- **psycopg2:** https://www.psycopg.org/docs/

---

**recomendação:** use opção 1 (postgresql nativo) por ser mais simples no windows!

