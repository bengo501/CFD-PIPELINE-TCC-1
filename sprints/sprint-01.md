# sprint 1 - [nome do sprint]

**período:** 09/10/2025 - 09/10/2025  
**duração:** 2 semanas (10 dias úteis)  
**time:** [nomes dos desenvolvedores]

---

## 🎯 objetivo da sprint

[descrever objetivo principal da sprint em 1-2 frases]

**exemplo:**
> implementar análise automática de resultados cfd e configurar pipeline ci/cd para garantir qualidade do código.

---

## 📋 backlog da sprint

### tarefas selecionadas

| tarefa | descrição | story points | prioridade | responsável |
|--------|-----------|--------------|------------|-------------|
| #18 | backend fastapi | 13 | alta | @dev1 |
| #19 | frontend react | 13 | alta | @dev1 |
| #101 | análise de resultados | 8 | média | @dev1 |

**total story points:** 34 pts

### capacidade do time

- **desenvolvedores:** 2
- **dias úteis:** 10
- **horas/dia:** 6
- **total disponível:** 120 horas
- **estimativa sprint:** ~84 horas (21 pts × 4h/pt)
- **viável?** ✅ sim (70% capacidade)

### priorização

1. 🔴 alta: #101, #105 (crítico para pipeline)
2. 🟡 média: #104 (melhoria infraestrutura)
3. 🟢 baixa: (nenhuma nesta sprint)

---

## ✅ critérios de sucesso

### definição de "pronto" (dod)

- [ ] código implementado e funcionando
- [ ] testes unitários criados (cobertura >80%)
- [ ] documentação atualizada
- [ ] code review aprovado
- [ ] merged na branch main
- [ ] demo funcionando

### critérios específicos desta sprint

1. análise de resultados extrai métricas corretas (perda de carga, velocidade)
2. ci/cd executa testes automaticamente em cada push
3. docker containers funcionam em qualquer ambiente

---

## 📅 daily standups

### formato
- **horário:** 9h30
- **duração:** 15 minutos
- **formato:** de pé
- **perguntas:**
  1. o que fiz ontem?
  2. o que farei hoje?
  3. há algum bloqueio?

### dia 1 (dd/mm)
**@dev1:** 
- fez: [tarefa]
- fará: [tarefa]
- bloqueios: nenhum

**@dev2:**
- fez: [tarefa]
- fará: [tarefa]
- bloqueios: [se houver]

### dia 2 (dd/mm)
...

### dia 3 (dd/mm)
...

---

## 📊 métricas da sprint

### velocity

```
story points planejados: 21
story points concluídos: XX
velocity: XX pts
```

### burndown

| dia | ideal | real | tarefas concluídas |
|-----|-------|------|--------------------|
| 0   | 21    | 21   | -                  |
| 1   | 19    | 21   | -                  |
| 2   | 17    | 18   | -                  |
| 3   | 15    | 15   | #105               |
| ... | ...   | ...  | ...                |
| 10  | 0     | 0    | #101, #104         |

### cycle time

| tarefa | início | fim | cycle time |
|--------|--------|-----|------------|
| #101   | dia 1  | dia 8 | 8 dias   |
| #105   | dia 1  | dia 3 | 3 dias   |
| #104   | dia 4  | dia 10 | 7 dias  |

**cycle time médio:** 6 dias

---

## 🎬 sprint review

**data:** 09/10/2025  
**participantes:** time + stakeholders

### entregáveis

- ✅ #101: análise de resultados - **aceito**
  - demo: extração automática de métricas
  - feedback: excelente, adicionar mais gráficos
  
- ✅ #105: ci/cd pipeline - **aceito**
  - demo: testes rodando no github actions
  - feedback: perfeito, adicionar deploy automático
  
- ⏸️ #104: docker - **parcialmente aceito**
  - demo: containers funcionando localmente
  - feedback: falta documentação

### feedback dos stakeholders

- [anotar feedback recebido]
- [pontos positivos]
- [pontos de melhoria]

### métricas finais

- **velocity alcançado:** XX pts
- **taxa de conclusão:** XX%
- **bugs encontrados:** X
- **dívida técnica:** [se houver]

---

## 🔄 retrospectiva

**data:** 09/10/2025  
**participantes:** apenas time

### start (começar a fazer)

- [ ] usar conventional commits sempre
- [ ] adicionar testes antes de implementar (tdd)
- [ ] fazer pair programming em tarefas complexas

### stop (parar de fazer)

- [ ] deixar prs abertos por mais de 1 dia
- [ ] commits grandes demais
- [ ] pular code review

### continue (continuar fazendo)

- [ ] daily standups pontuais às 9h30
- [ ] documentação inline excelente
- [ ] comunicação assíncrona eficiente

### action items

- [ ] @dev1: configurar pre-commit hooks
- [ ] @dev2: criar template de pr
- [ ] @time: definir convenção de nomes de branches

---

## 📌 impedimentos e resoluções

### impedimentos encontrados

| dia | impedimento | impacto | resolução | status |
|-----|-------------|---------|-----------|--------|
| 3   | wsl não funcionando | alto | reinstalar wsl2 | ✅ resolvido |
| 5   | falta acesso repo | médio | solicitar ao admin | ✅ resolvido |

---

## 📝 notas adicionais

[espaço livre para anotações durante a sprint]

---

## 🔜 próxima sprint

### candidatos para sprint 1+1

- #102: api rest (8 pts)
- #103: dashboard web (13 pts)
- #106: postgresql (5 pts)

### preparação necessária

- [ ] revisar prioridades com po
- [ ] refinar user stories
- [ ] estimar novas tarefas


