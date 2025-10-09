# guia para criar milestones (sprints) manualmente no github

## 🎯 objetivo

criar 8 milestones representando os sprints do projeto e associar as issues correspondentes.

---

## 📋 milestones a criar

### sprint 1 - fundação ✅ concluído

**título:** `Sprint 1 - Fundação`  
**descrição:** `DSL .bed, compilador ANTLR, bed wizard, kanban/scrumban`  
**due date:** `2025-09-22`  
**status:** fechado (concluído)

**issues associadas:**
- #1 - implementar dsl (.bed) com antlr
- #2 - bed wizard interativo
- #7 - configurar kanban/scrumban
- #8 - integrar github projects

---

### sprint 2 - modelagem ✅ concluído

**título:** `Sprint 2 - Modelagem`  
**descrição:** `Blender headless, OpenFOAM automatizado, testes E2E, documentação`  
**due date:** `2025-10-07`  
**status:** fechado (concluído)

**issues associadas:**
- #3 - integrar blender headless
- #4 - setup openfoam automatizado
- #5 - testes e2e automatizados
- #6 - documentar pipeline completo

---

### sprint 3 - web e api ✅ concluído

**título:** `Sprint 3 - Web e API`  
**descrição:** `FastAPI backend, React frontend, integração full-stack`  
**due date:** `2025-10-09`  
**status:** fechado (concluído)

**issues associadas:**
- #18 - backend fastapi com api rest
- #19 - frontend react com interface web

---

### sprint 4 - documentação ✅ concluído

**título:** `Sprint 4 - Documentação`  
**descrição:** `Bibliografia completa (46 refs), referencial teórico, documentação técnica`  
**due date:** `2025-10-09`  
**status:** fechado (concluído)

**issues associadas:**
- (nenhuma issue específica, foi sprint de documentação)

---

### sprint 5 - correções ⏳ ativo

**título:** `Sprint 5 - Correções`  
**descrição:** `Corrigir bugs críticos, validação, pipeline OpenFOAM completo`  
**due date:** `2025-10-17`  
**status:** aberto (ativo)

**issues associadas:**
- #20 - documentação completa openfoam (3 pts)
- #21 - corrigir física blender (8 pts) 🔴 bug crítico
- #22 - pipeline openfoam completo (8 pts)
- #25 - pós-processamento cfd (5 pts)

**total:** 24 story points

---

### sprint 6 - persistência 📅 planejado

**título:** `Sprint 6 - Persistência`  
**descrição:** `PostgreSQL, MinIO artefatos, visualização 3D (Three.js)`  
**due date:** `2025-11-01`  
**status:** aberto (planejado)

**issues associadas:**
- #23 - implementar postgresql (8 pts)
- #26 - integrar minio artefatos (5 pts)
- #27 - threejs visualização 3d (8 pts)

**total:** 21 story points

---

### sprint 7 - validação científica 📅 planejado

**título:** `Sprint 7 - Validação Científica`  
**descrição:** `Validação com equação de Ergun, estudo de malha GCI`  
**due date:** `2025-11-15`  
**status:** aberto (planejado)

**issues associadas:**
- #28 - validação com equação de ergun (13 pts)
- #29 - estudo de malha gci (8 pts)

**total:** 21 story points

---

### sprint 8 - finalização tcc1 📅 planejado

**título:** `Sprint 8 - Finalização TCC1`  
**descrição:** `Proposta TCC1, apresentação, documentação final`  
**due date:** `2025-11-30`  
**status:** aberto (planejado)

**issues associadas:**
- #30 - escrever proposta tcc1 (8 pts)
- #31 - preparar apresentação tcc1 (3 pts)

**total:** 11 story points

---

## 🖱️ passo a passo para criar

### 1. acessar milestones

1. vá para: https://github.com/bengo501/CFD-PIPELINE-TCC-1
2. clique em **"Issues"** no topo
3. clique em **"Milestones"** (ao lado de Labels)
4. clique em **"New milestone"**

### 2. criar milestone

para cada sprint acima:

1. **title:** copie o título exato (ex: "Sprint 1 - Fundação")
2. **due date:** selecione a data (formato: MM/DD/YYYY)
3. **description:** copie a descrição
4. clique em **"Create milestone"**

### 3. associar issues ao milestone

#### opção a: via interface web

1. abra a issue (ex: #1)
2. na barra lateral direita, clique em **"Milestone"**
3. selecione o milestone (ex: "Sprint 1 - Fundação")
4. repita para todas as issues

#### opção b: via api (automatizado)

execute o script:
```powershell
powershell -ExecutionPolicy Bypass -File .github\associar_issues_milestones.ps1
```

### 4. fechar milestones concluídos

para sprints 1-4 (concluídos):

1. vá para: https://github.com/bengo501/CFD-PIPELINE-TCC-1/milestones
2. clique no milestone
3. clique em **"Close milestone"**

---

## ✅ checklist de verificação

após criar todos milestones:

- [ ] 8 milestones criados
- [ ] todos com título correto
- [ ] todos com descrição clara
- [ ] todos com due date definida
- [ ] issues associadas corretamente
- [ ] sprints 1-4 fechados (concluídos)
- [ ] sprint 5 aberto (ativo)
- [ ] sprints 6-8 abertos (planejados)

### verificar associações

```powershell
# listar issues do sprint 5
gh issue list --milestone "Sprint 5 - Correções"

# ou via web
# https://github.com/bengo501/CFD-PIPELINE-TCC-1/milestone/5
```

---

## 📊 resultado esperado

### visão de milestones

```
Sprint 1 - Fundação          ████████████████████  100% (4/4)  ✅ Fechado
Sprint 2 - Modelagem         ████████████████████  100% (4/4)  ✅ Fechado
Sprint 3 - Web e API         ████████████████████  100% (2/2)  ✅ Fechado
Sprint 4 - Documentação      ████████████████████  100%        ✅ Fechado
Sprint 5 - Correções         ░░░░░░░░░░░░░░░░░░░░    0% (0/4)  🟢 Aberto
Sprint 6 - Persistência      ░░░░░░░░░░░░░░░░░░░░    0% (0/3)  📅 Planejado
Sprint 7 - Validação         ░░░░░░░░░░░░░░░░░░░░    0% (0/2)  📅 Planejado
Sprint 8 - Finalização       ░░░░░░░░░░░░░░░░░░░░    0% (0/2)  📅 Planejado
```

### progresso geral

- **concluído:** 92 story points (54.4%)
- **em andamento:** 24 story points (sprint 5)
- **pendente:** 53 story points (sprints 6-8)
- **total:** 169 story points (tcc1)

---

## 🔧 troubleshooting

### erro: "milestone já existe"

- ótimo! pule para associar issues

### erro: "não consigo criar milestone"

- verifique permissões do repositório
- deve ter acesso de "write" ou superior

### erro: "issue não aparece no milestone"

- verifique se a issue está associada corretamente
- atualize a página
- pode demorar alguns segundos

---

## 📚 referências

- **documentação local:**
  - `sprints/sprint-01-fundacao.md`
  - `sprints/sprint-02-modelagem.md`
  - `sprints/sprint-03-web-api.md`
  - `sprints/sprint-04-documentacao.md`
  - `.github/milestones_sprints.md`

- **github:**
  - https://github.com/bengo501/CFD-PIPELINE-TCC-1/milestones
  - https://github.com/bengo501/CFD-PIPELINE-TCC-1/issues

---

**após criar todos milestones, você terá uma visão completa e organizada do projeto! 🎯**

