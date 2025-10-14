# guias de uso

documentação prática e guias passo a passo para usar o projeto cfd pipeline.

---

## 📚 conteúdo

### mvp e desenvolvimento local
- **MVP_LOCAL_ROADMAP.md** - roadmap completo do mvp local
- **MVP_STATUS_ATUAL.md** - status atual da implementação
- **GUIA_MVP_LOCAL.md** - guia passo a passo para executar mvp

### docker e containers
- **DOCKER_COMPOSE_GUIA.md** - guia completo de docker-compose

### bed wizard (dsl)
- **EXEMPLO_USO_AJUDA.md** - exemplos de uso do sistema de ajuda
- **README_BLENDER_MODE.md** - modo blender do wizard
- **README_DOCUMENTACAO.md** - documentação do wizard
- **README_SISTEMA_AJUDA.md** - sistema de ajuda interativa

### frontend
- **README_THREE.md** - integração three.js para visualização 3d
- **README_WIZARD.md** - wizard web (interface react)

---

## 🎯 como usar

### executar mvp local
```bash
# ver guia completo
cat GUIA_MVP_LOCAL.md

# executar
cd ../..
iniciar-mvp.bat
```

### usar bed wizard
```bash
# ver ajuda
cat README_SISTEMA_AJUDA.md

# executar wizard
cd ../../dsl
python bed_wizard.py
```

### configurar docker
```bash
# ver guia
cat DOCKER_COMPOSE_GUIA.md

# executar
cd ../..
docker-compose up -d
```

---

**todos os guias nesta pasta são documentação auxiliar e não são versionados no git.**
