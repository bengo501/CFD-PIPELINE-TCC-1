# guia para adicionar issues ao github project

## ⚠️ problema: permissões insuficientes

o token gh cli atual não tem permissão para acessar projects (`read:project`, `project`).

---

## 🔧 solução: reauthenticar com scopes corretos

### passo 1: reauthenticar gh cli

```powershell
# fazer logout
gh auth logout

# fazer login com scopes de project
gh auth login --scopes "repo,read:org,read:project,project"
```

**siga as instruções:**
1. escolha: **GitHub.com**
2. protocolo: **HTTPS**
3. autenticação: **Login with a web browser**
4. copie o código e cole no navegador
5. autorize o acesso

### passo 2: verificar permissões

```powershell
gh auth status
```

deve mostrar:
```
- Token scopes: 'project', 'read:org', 'read:project', 'repo'
```

---

## 🚀 adicionar issues ao projeto

### opção a: automático (recomendado)

depois de reauthenticar:

```powershell
# adicionar todas issues ao projeto
powershell -ExecutionPolicy Bypass -File .github\adicionar_ao_projeto.ps1
```

### opção b: manual (via interface web)

se preferir fazer manualmente:

1. **acesse o projeto:**  
   https://github.com/users/bengo501/projects/2

2. **adicionar issues:**
   - clique em "+ Add item"
   - digite "#" para listar issues
   - selecione as issues desejadas
   - repita para todas as 48 issues

3. **organizar por sprint:**
   
   **sprint 1 - fundação (done):**
   - #1, #2, #7, #8
   
   **sprint 2 - modelagem (done):**
   - #3, #4, #5, #6
   
   **sprint 3 - web (done):**
   - #18, #19
   
   **sprint 5 - correções (todo):**
   - #20, #21, #22, #25
   
   **sprint 6 - persistência (todo):**
   - #23, #26, #27
   
   **sprint 7 - validação (todo):**
   - #28, #29
   
   **sprint 8 - tcc1 (todo):**
   - #30, #31

---

## 📋 campos customizados a configurar

### criar campos no projeto

1. **status** (single select)
   - Done
   - In Progress
   - Todo
   - Backlog

2. **priority** (single select)
   - High
   - Medium
   - Low

3. **story points** (number)
   - min: 1
   - max: 21

4. **sprint** (iteration)
   - duration: 2 weeks
   - criar 8 sprints:
     - Sprint 1 - Fundação (15-22/09)
     - Sprint 2 - Modelagem (23/09-07/10)
     - Sprint 3 - Web (08-09/10)
     - Sprint 4 - Docs (09/10)
     - Sprint 5 - Correções (10-17/10)
     - Sprint 6 - Persistência (18/10-01/11)
     - Sprint 7 - Validação (02-15/11)
     - Sprint 8 - TCC1 (16-30/11)

---

## 🎯 preencher dados

### opção a: script automático (após configurar campos)

```powershell
powershell -ExecutionPolicy Bypass -File .github\preencher_campos_projeto.ps1
```

### opção b: preencher manualmente

**issues sprint 1 (done):**
- #1: 13 pts, Done
- #2: 8 pts, Done
- #7: 3 pts, Done
- #8: 3 pts, Done

**issues sprint 2 (done):**
- #3: 13 pts, Done
- #4: 13 pts, Done
- #5: 8 pts, Done
- #6: 5 pts, Done

**issues sprint 3 (done):**
- #18: 13 pts, Done
- #19: 13 pts, Done

**issues sprint 5 (todo):**
- #20: 3 pts, Medium, Todo
- #21: 8 pts, High, Todo (bug)
- #22: 8 pts, High, Todo
- #25: 5 pts, High, Todo

**issues sprint 6 (todo):**
- #23: 8 pts, Medium, Todo
- #26: 5 pts, Medium, Todo
- #27: 8 pts, Medium, Todo

**issues sprint 7 (todo):**
- #28: 13 pts, High, Todo
- #29: 8 pts, High, Todo

**issues sprint 8 (todo):**
- #30: 8 pts, High, Todo
- #31: 3 pts, High, Todo

---

## ✅ verificar resultado

após adicionar e organizar:

1. **acesse:** https://github.com/users/bengo501/projects/2

2. **verifique:**
   - ✅ 48 issues adicionadas
   - ✅ organizadas por status (done/todo)
   - ✅ story points preenchidos
   - ✅ prioridades definidas
   - ✅ sprints associados

3. **visualizações úteis:**
   - **board view:** ver por colunas (todo/in progress/done)
   - **table view:** ver todos dados em tabela
   - **roadmap view:** ver timeline dos sprints

---

## 🔗 links úteis

- **projeto:** https://github.com/users/bengo501/projects/2
- **milestones:** https://github.com/bengo501/CFD-PIPELINE-TCC-1/milestones
- **issues:** https://github.com/bengo501/CFD-PIPELINE-TCC-1/issues

---

## 📚 scripts criados

1. **`.github/adicionar_ao_projeto.ps1`**  
   adiciona todas issues ao projeto via graphql

2. **`.github/preencher_campos_projeto.ps1`**  
   preenche story points, priority, status automaticamente

3. **`.github/setup_milestones_completo.ps1`**  
   cria milestones e associa issues

---

**após seguir este guia, seu projeto estará completamente organizado! 🎉**

