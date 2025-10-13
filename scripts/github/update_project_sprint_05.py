#!/usr/bin/env python3
"""
atualizar status das issues do sprint 5 no github project
move issues para 'done' no board do project
"""

import subprocess
import json
import sys

REPO = "bengo501/CFD-PIPELINE-TCC-1"
PROJECT_NUMBER = 2  # https://github.com/users/bengo501/projects/2

# issues do sprint 5 (task-032 a task-040)
ISSUES_SPRINT_5 = {
    77: {'task': 'task-032', 'titulo': 'wizard web completo', 'status': 'Done'},
    78: {'task': 'task-033', 'titulo': 'física blender corrigida', 'status': 'Done'},
    79: {'task': 'task-034', 'titulo': 'integração cfd', 'status': 'Done'},
    80: {'task': 'task-035', 'titulo': 'identidade visual', 'status': 'Done'},
    81: {'task': 'task-036', 'titulo': 'i18n pt/en', 'status': 'Done'},
    82: {'task': 'task-037', 'titulo': 'tipografia', 'status': 'Done'},
    83: {'task': 'task-038', 'titulo': 'formatos exportação', 'status': 'Done'},
    84: {'task': 'task-039', 'titulo': 'visualização casos', 'status': 'Done'},
    85: {'task': 'task-040', 'titulo': 'pipeline completo', 'status': 'Done'},
}


def run_gh_command(args):
    """executar comando gh cli"""
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result
    except Exception as e:
        print(f"erro ao executar comando: {e}")
        return None


def obter_project_id():
    """obter id do project via graphql"""
    query = '''
    query {
      user(login: "bengo501") {
        projectV2(number: 2) {
          id
          title
        }
      }
    }
    '''
    
    result = run_gh_command(['api', 'graphql', '-f', f'query={query}'])
    
    if result and result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            project_id = data['data']['user']['projectV2']['id']
            title = data['data']['user']['projectV2']['title']
            print(f"✓ project encontrado: {title}")
            print(f"  id: {project_id}")
            return project_id
        except:
            pass
    
    print("✗ não foi possível obter project id")
    return None


def adicionar_issue_ao_project(project_id, issue_id):
    """adicionar issue ao project"""
    mutation = '''
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
          id
        }
      }
    }
    '''
    
    # obter issue global id
    result = run_gh_command(['api', f'/repos/{REPO}/issues/{issue_id}', '--jq', '.node_id'])
    
    if not result or result.returncode != 0:
        return None
    
    issue_node_id = result.stdout.strip()
    
    # adicionar ao project
    variables = json.dumps({
        'projectId': project_id,
        'contentId': issue_node_id
    })
    
    result = run_gh_command([
        'api', 'graphql',
        '-f', f'query={mutation}',
        '-f', f'variables={variables}'
    ])
    
    if result and result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            return data['data']['addProjectV2ItemById']['item']['id']
        except:
            pass
    
    return None


def main():
    print("="*70)
    print("  atualizar github project - sprint 5")
    print("="*70)
    
    # verificar gh cli
    result = run_gh_command(['--version'])
    if not result or result.returncode != 0:
        print("\n✗ gh cli não encontrado!")
        print("instale: https://cli.github.com/")
        return
    
    print("\n✓ gh cli disponível")
    
    # obter project id
    project_id = obter_project_id()
    
    if not project_id:
        print("\n✗ não foi possível conectar ao project")
        print("\nsolução alternativa:")
        print("  1. acesse: https://github.com/users/bengo501/projects/2")
        print("  2. adicione as issues manualmente")
        print(f"  3. issues do sprint 5: #77-85")
        print("  4. mova para coluna 'done'")
        return
    
    # adicionar issues ao project
    print(f"\nadicionando issues ao project...")
    
    for issue_num, info in ISSUES_SPRINT_5.items():
        print(f"\nprocessando issue #{issue_num} ({info['titulo']})...")
        
        item_id = adicionar_issue_ao_project(project_id, issue_num)
        
        if item_id:
            print(f"  ✓ adicionada ao project")
        else:
            print(f"  ℹ já existe no project ou erro")
    
    print("\n" + "="*70)
    print("  atualização concluída!")
    print("="*70)
    print(f"\nverificar em:")
    print(f"https://github.com/users/bengo501/projects/2")
    print(f"\nprovavelmente as issues já estão no project.")
    print(f"para mover para 'done', arraste manualmente ou:")
    print(f"  - use a interface web do project")
    print(f"  - todas issues #77-85 devem estar em 'done'")


if __name__ == "__main__":
    main()

