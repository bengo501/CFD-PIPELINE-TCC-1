---
name: criar visualização de casos cfd existentes
tags:
  - frontend
  - cfd
  - file-management
created: 2025-10-12
assigned: 
sprint: mes 4 sem 1-2
atividades-tcc: a11
story-points: 5
---

# criar visualização de casos cfd existentes

interface para listar, gerenciar e executar casos cfd já criados

## tarefas
- [x] backend: routes_casos.py
- [x] endpoint get /api/casos/list
- [x] endpoint get /api/casos/{nome}/detalhes
- [x] endpoint delete /api/casos/{nome}
- [x] função analisar_caso() - extrair info
- [x] função determinar_status_caso()
- [x] frontend: casoscfd.jsx
- [x] grid de cards com casos
- [x] status badges (configured/meshed/running/completed)
- [x] modal de detalhes completos
- [x] comandos wsl prontos

## resultado
usuário vê todos casos, sabe status, tem comandos prontos para executar

