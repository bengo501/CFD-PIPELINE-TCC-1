# documentação backend

documentação técnica específica do backend fastapi e integração com banco de dados.

---

## 📚 conteúdo

### banco de dados
- **GUIA_INTEGRACAO_BANCO.md** - guia de integração com postgresql
- **RESUMO_INTEGRACAO_POSTGRESQL.md** - resumo da implementação

### setup e configuração
- **GUIA_SETUP_WINDOWS.md** - setup do backend no windows
- **RESUMO_IMPLEMENTACAO.md** - resumo da implementação completa

---

## 🎯 como usar

### configurar banco de dados
```bash
# ver guia
cat GUIA_INTEGRACAO_BANCO.md

# executar
cd ../../backend
python scripts/init_database.py
```

### executar backend
```bash
# ver guia de setup
cat GUIA_SETUP_WINDOWS.md

# executar
cd ../../backend
python -m uvicorn app.main:app --reload
```

---

## 🔧 tecnologias

- **fastapi** - framework web
- **sqlalchemy** - orm
- **postgresql** - banco de dados
- **alembic** - migrations
- **pydantic** - validação

---

**toda documentação nesta pasta é técnica e específica do backend.**
