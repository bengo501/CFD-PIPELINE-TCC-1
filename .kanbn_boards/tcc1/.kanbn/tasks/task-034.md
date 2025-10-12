---
name: integrar simulação cfd openfoam no web
tags:
  - cfd
  - openfoam
  - backend
  - frontend
created: 2025-10-12
assigned: 
sprint: mes 4 sem 1-2
atividades-tcc: a10, a11
story-points: 8
---

# integrar simulação cfd openfoam no web

criar interface web para executar e monitorar simulações cfd

## tarefas
- [x] backend: routes_cfd.py (5 endpoints)
- [x] frontend: cfdsimulation.jsx
- [x] monitoramento em tempo real
- [x] background tasks assíncronas
- [x] auto-refresh a cada 3s
- [x] histórico de simulações
- [x] visualização de status (6 estados)
- [x] integração com setup_openfoam_case.py

## endpoints criados
- POST /api/cfd/create
- GET /api/cfd/status/{id}
- GET /api/cfd/list
- POST /api/cfd/run-from-wizard
- DELETE /api/cfd/{id}

## resultado
simulações cfd executáveis e monitoráveis diretamente da interface web

