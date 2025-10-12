#!/usr/bin/env python3
"""
script para sincronizar sprint 5 com github issues e milestones
"""

import subprocess
import json
from pathlib import Path

# configurações
REPO = "bengo501/CFD-PIPELINE-TCC-1"
MILESTONE_NAME = "sprint 5 - interface completa e cfd"
MILESTONE_DESC = """
sprint focado em completar interface web e integrar simulação cfd

**período:** 12/10/2025 - 19/10/2025

**objetivos:**
- wizard web 100% funcional
- física blender corrigida
- cfd openfoam integrado
- identidade visual aplicada
- sistema bilíngue (pt/en)
"""

# tasks do sprint 5
TASKS = [
    {
        "numero": "032",
        "titulo": "implementar wizard web completo (4 modos)",
        "labels": ["enhancement", "frontend", "wizard"],
        "body": """
## descrição
criar interface web completa para criação de leitos, replicando bed_wizard.py

## funcionalidades implementadas
- ✅ modo questionário interativo
- ✅ modo editor de template inline
- ✅ modo blender (sem cfd)
- ✅ modo blender interativo
- ✅ sistema de ajuda contextual (HelpModal)
- ✅ documentação integrada (DocsModal)
- ✅ preview 3d em tempo real
- ✅ validação robusta

## arquivos criados
- `frontend/src/components/BedWizard.jsx` (767 linhas)
- `frontend/src/components/WizardHelpers.jsx` (207 linhas)
- `frontend/src/styles/BedWizard.css` (609 linhas)
- `backend/app/api/routes_wizard.py` (360 linhas)

## resultado
interface web 100% equivalente ao bed_wizard.py python, com experiência superior
"""
    },
    {
        "numero": "033",
        "titulo": "corrigir física blender (animação + colisões)",
        "labels": ["bugfix", "blender", "physics", "critical"],
        "body": """
## problemas identificados
1. ❌ partículas ficavam suspensas (não caíam)
2. ❌ tampa superior bloqueava entrada
3. ❌ cilindro oco tinha colisão fantasma interna

## soluções implementadas
- ✅ executar animação automaticamente (20s padrão)
- ✅ função `executar_simulacao_fisica()`
- ✅ tampa superior sem colisão (`tem_colisao=False`)
- ✅ cilindro com mesh collision
- ✅ bake automático de física

## resultado
modelos 3d fisicamente corretos, partículas acomodadas, prontos para cfd

## arquivo modificado
- `scripts/blender_scripts/leito_extracao.py` (+150 linhas)
"""
    },
    {
        "numero": "034",
        "titulo": "integrar simulação cfd openfoam no web",
        "labels": ["enhancement", "cfd", "backend", "frontend"],
        "body": """
## descrição
criar interface web para executar e monitorar simulações cfd

## implementação

**backend (5 endpoints):**
- POST /api/cfd/create
- GET /api/cfd/status/{id}
- GET /api/cfd/list
- POST /api/cfd/run-from-wizard
- DELETE /api/cfd/{id}

**frontend:**
- componente cfdsimulation.jsx
- monitoramento em tempo real
- auto-refresh 3s
- histórico de simulações
- status visual (6 estados)

## arquivos criados
- `backend/app/api/routes_cfd.py` (270 linhas)
- `frontend/src/components/CFDSimulation.jsx` (230 linhas)
- `frontend/src/styles/CFDSimulation.css` (350 linhas)

## resultado
simulações cfd executáveis e monitoráveis diretamente da interface web
"""
    },
    {
        "numero": "035",
        "titulo": "aplicar identidade visual (paleta institucional)",
        "labels": ["design", "ui/ux", "branding"],
        "body": """
## paleta de cores implementada

**cores principais:**
- vinho #5F1923 (títulos, botões principais)
- verde #50AF50 (sucesso, destaques)
- amarelo #F0B91E (accents)
- laranja #DC7323 (warnings)
- creme #F5F087 (backgrounds)
- branco #FFFFFF (fundo)

## tarefas
- ✅ criar variáveis css globais
- ✅ atualizar todos componentes
- ✅ verificar acessibilidade wcag aa/aaa
- ✅ documentar paleta completa

## resultado
interface visualmente coesa e profissional, alinhada com identidade institucional
"""
    },
    {
        "numero": "036",
        "titulo": "implementar internacionalização (pt/en)",
        "labels": ["enhancement", "i18n", "accessibility"],
        "body": """
## implementação

**sistema completo:**
- ~100 traduções português/inglês
- contexto global react
- hook uselanguage
- botão toggle com bandeiras 🇧🇷/🇺🇸
- persistência localstorage

## arquivos criados
- `frontend/src/i18n/translations.js` (181 linhas)
- `frontend/src/context/LanguageContext.jsx` (40 linhas)

## cobertura
navegação, wizard, cfd, status, mensagens, tooltips

## resultado
sistema bilíngue completo, experiência internacional
"""
    },
    {
        "numero": "037",
        "titulo": "melhorar tipografia e legibilidade",
        "labels": ["design", "typography", "accessibility"],
        "body": """
## fontes implementadas

**inter:** sans-serif profissional moderna
**jetbrains mono:** monospace para código

## melhorias
- tamanho base: 16px (era 14px)
- h1: 2.5rem (40px)
- h2: 2rem (32px)
- h3: 1.5rem (24px)
- line-height: 1.7
- antialiasing otimizado

## resultado
interface mais legível, profissional e acessível
"""
    },
    {
        "numero": "038",
        "titulo": "implementar seleção de formatos de exportação",
        "labels": ["enhancement", "blender", "export"],
        "body": """
## formatos suportados
blend, gltf, glb, obj, fbx, stl (6 formatos)

## implementação

**backend:**
- parâmetro --formats no script blender
- exportação condicional
- tratamento de erros individual

**frontend:**
- checkboxes visuais
- grid responsivo 2-3 colunas
- contador de selecionados
- recomendação clara

## resultado
usuário escolhe formatos, exportação customizável, tempo otimizado
"""
    },
    {
        "numero": "039",
        "titulo": "criar visualização de casos cfd existentes",
        "labels": ["enhancement", "cfd", "file-management"],
        "body": """
## implementação

**backend:**
- routes_casos.py
- análise automática de casos
- determinação de status
- extração de informações

**frontend:**
- casoscfd.jsx
- grid de cards
- status badges
- modal de detalhes
- comandos wsl prontos

## funcionalidades
- listar todos casos em output/cfd/
- status (configured/meshed/running/completed)
- quantidade de resultados (pastas de tempo)
- logs disponíveis
- deletar casos antigos

## resultado
usuário vê e gerencia todos casos cfd facilmente
"""
    },
    {
        "numero": "040",
        "titulo": "implementar pipeline completo end-to-end",
        "labels": ["enhancement", "automation", "integration"],
        "body": """
## descrição
interface para executar todo o pipeline automaticamente

## fluxo
wizard → dsl → blender → openfoam → resultados

## implementação
- visualização fluxo (5 etapas)
- execução sequencial automatizada
- log em tempo real (estilo terminal)
- barra de progresso animada
- status visual por etapa
- polling de simulação
- exibição de resultados

## arquivos
- `frontend/src/components/PipelineCompleto.jsx` (406 linhas)
- `frontend/src/styles/PipelineCompleto.css` (420 linhas)

## resultado
1 clique executa todo o pipeline, equivalente superior ao bed_wizard.py
"""
    }
]


def criar_milestone():
    """criar milestone no github"""
    print("criando milestone...")
    
    cmd = [
        "gh", "api",
        f"/repos/{REPO}/milestones",
        "-X", "POST",
        "-f", f"title={MILESTONE_NAME}",
        "-f", f"description={MILESTONE_DESC}",
        "-f", "state=closed",  # já concluído
        "-f", "due_on=2025-10-19T23:59:59Z"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"✓ milestone criada: #{data['number']}")
            return data['number']
        else:
            print(f"erro ao criar milestone: {result.stderr}")
            return None
    except Exception as e:
        print(f"erro: {e}")
        return None


def criar_issues(milestone_number):
    """criar issues para cada task"""
    print(f"\ncriando {len(TASKS)} issues...")
    
    for task in TASKS:
        titulo = f"[task-{task['numero']}] {task['titulo']}"
        labels = ",".join(task['labels'])
        
        cmd = [
            "gh", "issue", "create",
            "--repo", REPO,
            "--title", titulo,
            "--body", task['body'],
            "--label", labels,
            "--milestone", str(milestone_number)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✓ issue criada: {task['titulo']}")
            else:
                print(f"  ✗ erro: {result.stderr}")
        except Exception as e:
            print(f"  ✗ erro: {e}")


def fechar_issues():
    """fechar todas as issues criadas (sprint já concluído)"""
    print("\nfechando issues (sprint concluído)...")
    
    for task in TASKS:
        titulo_busca = f"[task-{task['numero']}]"
        
        # buscar issue
        cmd_busca = [
            "gh", "issue", "list",
            "--repo", REPO,
            "--search", titulo_busca,
            "--json", "number",
            "--limit", "1"
        ]
        
        try:
            result = subprocess.run(cmd_busca, capture_output=True, text=True)
            if result.returncode == 0:
                issues = json.loads(result.stdout)
                if issues:
                    issue_num = issues[0]['number']
                    
                    # fechar issue
                    cmd_fechar = [
                        "gh", "issue", "close", str(issue_num),
                        "--repo", REPO,
                        "--comment", "concluído em 12/10/2025 - sprint 5"
                    ]
                    
                    subprocess.run(cmd_fechar)
                    print(f"  ✓ issue #{issue_num} fechada")
        except Exception as e:
            print(f"  ✗ erro: {e}")


def main():
    """executar sincronização completa"""
    print("="*60)
    print("  sincronização sprint 5 com github")
    print("="*60)
    
    # verificar gh cli
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except:
        print("\nerro: github cli (gh) não encontrado!")
        print("instale: https://cli.github.com/")
        return
    
    # criar milestone
    milestone_num = criar_milestone()
    
    if not milestone_num:
        print("\nerro: não foi possível criar milestone")
        print("continuando com issues...")
        milestone_num = None
    
    # criar issues
    criar_issues(milestone_num)
    
    # fechar issues (sprint já concluído)
    fechar_issues()
    
    print("\n" + "="*60)
    print("  sincronização concluída!")
    print("="*60)
    print(f"\nverificar em:")
    print(f"https://github.com/{REPO}/issues")
    print(f"https://github.com/{REPO}/milestones")


if __name__ == "__main__":
    main()

