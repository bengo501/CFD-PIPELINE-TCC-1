# configuração e deploy

documentação para configuração de ambiente e deploy na nuvem.

---

## 📚 conteúdo

### deploy na nuvem
- **DEPLOY_NUVEM_GUIA.md** - guia completo de deploy no railway
  - configuração railway
  - docker-compose para produção
  - variáveis de ambiente
  - monitoramento
  - custos estimados

---

## 🎯 como usar

### deploy na nuvem (railway)
```bash
# ver guia completo
cat DEPLOY_NUVEM_GUIA.md

# instalar railway cli
npm install -g @railway/cli

# fazer login
railway login

# deploy
railway up
```

### alternativas de deploy
- **render.com** - plano gratuito
- **fly.io** - créditos gratuitos
- **vercel + railway** - frontend + backend

---

## 🌐 componentes na nuvem

### o que roda na nuvem:
- ✅ frontend (react)
- ✅ backend (fastapi)
- ✅ postgresql (banco)
- ✅ redis (cache)
- ✅ minio (arquivos)
- ✅ blender (geração 3d)
- ✅ openfoam (simulação cfd)

---

**toda documentação nesta pasta é sobre configuração de ambiente e deploy.**
