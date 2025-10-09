---
name: implementar banco de dados postgresql
tags:
  - backend
  - database
  - postgresql
created: 2025-10-09
assigned: 
sprint: sprint 2
story-points: 8
---

# implementar banco de dados postgresql

adicionar persistência de dados com postgresql.

## tarefas

### configuração
- [ ] instalar postgresql
- [ ] criar database `cfd_pipeline`
- [ ] configurar sqlalchemy
- [ ] configurar alembic (migrations)

### schema do banco
- [ ] tabela `users` (usuários)
- [ ] tabela `projects` (projetos)
- [ ] tabela `beds` (leitos criados)
- [ ] tabela `simulations` (simulações)
- [ ] tabela `jobs` (tarefas assíncronas)
- [ ] tabela `results` (resultados)
- [ ] relacionamentos (foreign keys)

### models sqlalchemy
- [ ] criar `backend/app/models/database.py`
- [ ] model User
- [ ] model Project
- [ ] model Bed
- [ ] model Simulation
- [ ] model Job
- [ ] model Result

### migrations
- [ ] setup alembic
- [ ] migration inicial
- [ ] scripts de seed (dados teste)

### integração com api
- [ ] salvar jobs no banco
- [ ] salvar parâmetros de leitos
- [ ] salvar resultados de simulações
- [ ] queries otimizadas
- [ ] índices apropriados

### queries úteis
- [ ] listar jobs por usuário
- [ ] histórico de simulações
- [ ] estatísticas de uso
- [ ] busca por parâmetros

## estrutura de arquivos

```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py      # conexão
│   │   ├── user.py
│   │   ├── bed.py
│   │   ├── simulation.py
│   │   └── job.py
│   └── db/
│       ├── migrations/       # alembic
│       └── seeds/            # dados iniciais
└── alembic.ini
```

## exemplo de model

```python
from sqlalchemy import Column, Integer, String, DateTime, JSON
from .database import Base

class Bed(Base):
    __tablename__ = "beds"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    parameters = Column(JSON)
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
```

## prioridade
média - importante para produção

## estimativa
2-3 dias (8 story points)

## critérios de aceitação
- [ ] postgresql instalado e configurado
- [ ] 6 tabelas criadas
- [ ] migrations funcionando
- [ ] models sqlalchemy criados
- [ ] integração com api
- [ ] jobs salvos no banco
- [ ] queries otimizadas
- [ ] documentação completa

