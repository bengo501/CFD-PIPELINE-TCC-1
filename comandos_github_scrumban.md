# comandos úteis github cli + scrumban

## listar issues
gh issue list
gh issue list --label "priority-high"
gh issue list --milestone "Sprint 1"
gh issue list --state all

## criar issue
gh issue create --title "[FEATURE] título" --body "descrição" --label "type-feature"

## atualizar issue
gh issue edit 123 --add-label "status-in-progress"
gh issue edit 123 --add-assignee @me
gh issue edit 123 --milestone "Sprint 1"

## fechar issue
gh issue close 123

## listar labels
gh label list

## listar milestones
gh api repos/:owner/:repo/milestones

## criar pr
gh pr create --title "feat: descrição" --body "closes #123"

## revisar pr
gh pr review 456 --approve

## merge pr
gh pr merge 456 --squash --delete-branch

## visualizar projeto
gh project list

## executar scripts
python .github/migrate_kanbn_to_github.py          # dry-run
python .github/migrate_kanbn_to_github.py --execute # executar

python scripts/automation/run_tests.py              # testes
python scripts/automation/batch_generate.py         # gerar lotes
python scripts/automation/cleanup.py                # limpar temp

## abrir browser
gh repo view --web
gh issue view 123 --web
gh pr view 456 --web
