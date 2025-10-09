---
name: implementar backend fastapi com api rest
tags:
  - backend
  - api
  - fastapi
created: 2025-10-09
assigned: 
sprint: mes 3 sem 3-4
atividades-tcc: a9
story-points: 13
---

# implementar backend fastapi com api rest

criar api rest completa para gerenciar pipeline cfd.

## tarefas
- [x] estrutura fastapi (main.py, routes, models)
- [x] endpoint POST /api/bed/compile
- [x] endpoint POST /api/model/generate
- [x] endpoint POST /api/simulation/create
- [x] sistema de jobs assíncronos
- [x] integração com bed_compiler (subprocess)
- [x] integração com blender headless (subprocess)
- [x] integração com openfoam (subprocess)
- [x] gerenciamento de arquivos (file_manager)
- [x] validação com pydantic (12 modelos)
- [x] documentação swagger automática
- [x] cors configurado
- [x] health checks
- [x] error handling robusto
- [x] README completo

## resultado
- 14 arquivos criados
- ~1600 linhas de código
- 15 endpoints rest funcionais
- 3 serviços integrados
- documentação completa em /docs

## prioridade
alta - essencial para interface web

## estimativa
2-3 dias (13 story points)

## dependências
- depende de: #2 (dsl), #3 (blender), #5 (openfoam)

## critérios de aceitação
- [x] api rest funcionando em localhost:8000
- [x] compilação de .bed via endpoint
- [x] geração 3d assíncrona
- [x] criação de caso openfoam
- [x] rastreamento de jobs
- [x] documentação swagger
- [x] integração com scripts existentes

