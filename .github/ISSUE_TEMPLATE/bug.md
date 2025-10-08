---
name: bug report
about: reportar um problema
title: '[BUG] '
labels: bug, needs-triage
assignees: ''
---

## 🐛 descrição do bug

[descrição clara e concisa do bug]

## 🔄 passos para reproduzir

1. executar `[comando ou ação]`
2. observar `[comportamento]`
3. ver erro `[mensagem de erro]`

**exemplo:**
```bash
cd dsl
python bed_wizard.py
# escolher modo 1
# erro: KeyError 'diameter'
```

## ✅ comportamento esperado

[descreva o que deveria acontecer]

## ❌ comportamento atual

[descreva o que está acontecendo]

## 📸 screenshots/logs

[se aplicável, adicione screenshots ou logs]

```
[cole aqui logs de erro]
```

## 🖥️ ambiente

**sistema operacional:**
- [ ] windows 10/11
- [ ] linux (distro: )
- [ ] macos (versão: )

**versões:**
- python: [ex: 3.11]
- blender: [ex: 4.0.2]
- openfoam: [ex: 11]
- wsl: [se windows]

**configuração:**
```bash
python --version
# cole saída aqui
```

## 📊 severidade

- [ ] 🔴 crítica (bloqueia uso completo)
- [ ] 🟡 alta (funcionalidade importante quebrada)
- [ ] 🟢 média (workaround possível)
- [ ] ⚪ baixa (cosmético/edge case)

## 🔍 investigação

**já tentou:**
- [ ] limpar cache python
- [ ] reinstalar dependências
- [ ] verificar logs
- [ ] testar em ambiente limpo

**possível causa:**
[se tiver alguma hipótese]

## 🔗 issues relacionadas

- #XX (similar)
- #YY (pode ser duplicata)

## 📝 contexto adicional

[adicione qualquer outra informação relevante]

---

<!--
etiquetas sugeridas:
- priority-critical/high/medium/low
- component-dsl/blender/openfoam/etc
- needs-investigation
- good-first-issue (se for simples)
-->

