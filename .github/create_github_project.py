#!/usr/bin/env python3
# script para criar github project automaticamente via api graphql
import subprocess
import json
import sys
from pathlib import Path

class GitHubProjectCreator:
    """cria e configura github project v2 via api graphql"""
    
    def __init__(self):
        self.owner_login = None
        self.project_id = None
        self.field_ids = {}
        
    def run_gh_command(self, args, parse_json=False):
        """executa comando gh cli"""
        try:
            result = subprocess.run(
                ['gh'] + args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"[erro] comando falhou: {' '.join(args)}")
                print(f"stderr: {result.stderr}")
                return None
            
            if parse_json and result.stdout.strip():
                return json.loads(result.stdout)
            
            return result.stdout.strip()
            
        except Exception as e:
            print(f"[erro] exceção ao executar comando: {e}")
            return None
    
    def get_owner_login(self):
        """pega username do github autenticado"""
        login = self.run_gh_command(['api', 'user', '-q', '.login'])
        if login:
            self.owner_login = login
            print(f"[ok] usuario detectado: {self.owner_login}")
            return True
        return False
    
    def create_project(self):
        """cria novo github project v2"""
        print("\n[2/7] criando github project...")
        
        # pegar owner id
        owner_data = self.run_gh_command(['api', 'user'], parse_json=True)
        if not owner_data:
            print("[erro] nao foi possivel pegar dados do usuario")
            return False
        
        owner_id = owner_data['node_id']
        
        # criar projeto usando formato correto
        query = 'mutation($ownerId: ID!) { createProjectV2(input: {ownerId: $ownerId, title: "CFD Pipeline - Scrumban"}) { projectV2 { id number url } } }'
        
        result = self.run_gh_command([
            'api', 'graphql',
            '-f', f'query={query}',
            '-F', f'ownerId={owner_id}'
        ], parse_json=True)
        
        if result and 'data' in result:
            project = result['data']['createProjectV2']['projectV2']
            self.project_id = project['id']
            project_number = project['number']
            project_url = project['url']
            
            print(f"[ok] projeto criado!")
            print(f"    id: {self.project_id}")
            print(f"    numero: {project_number}")
            print(f"    url: {project_url}")
            return True
        
        print("[erro] falha ao criar projeto")
        return False
    
    def add_custom_field(self, name, field_type, options=None):
        """adiciona campo customizado ao projeto"""
        print(f"[info] criando campo '{name}'...")
        
        if field_type == "single_select":
            # campo de selecao unica
            query = '''
            mutation($projectId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
              createProjectV2Field(input: {
                projectId: $projectId,
                dataType: SINGLE_SELECT,
                name: $name,
                singleSelectOptions: $options
              }) {
                projectV2Field {
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options {
                      id
                      name
                    }
                  }
                }
              }
            }
            '''
            
            variables = {
                'projectId': self.project_id,
                'name': name,
                'options': [{'name': opt, 'color': 'GRAY'} for opt in options]
            }
            
        elif field_type == "number":
            # campo numerico
            query = '''
            mutation($projectId: ID!, $name: String!) {
              createProjectV2Field(input: {
                projectId: $projectId,
                dataType: NUMBER,
                name: $name
              }) {
                projectV2Field {
                  ... on ProjectV2Field {
                    id
                    name
                  }
                }
              }
            }
            '''
            
            variables = {
                'projectId': self.project_id,
                'name': name
            }
        
        elif field_type == "iteration":
            # campo de iteracao (sprint)
            query = '''
            mutation($projectId: ID!, $name: String!) {
              createProjectV2Field(input: {
                projectId: $projectId,
                dataType: ITERATION,
                name: $name
              }) {
                projectV2Field {
                  ... on ProjectV2IterationField {
                    id
                    name
                  }
                }
              }
            }
            '''
            
            variables = {
                'projectId': self.project_id,
                'name': name
            }
        
        else:
            print(f"[erro] tipo de campo desconhecido: {field_type}")
            return None
        
        result = self.run_gh_command([
            'api', 'graphql',
            '-f', f'query={query}',
            '-f', f'variables={json.dumps(variables)}'
        ], parse_json=True)
        
        if result and 'data' in result:
            field = result['data']['createProjectV2Field']['projectV2Field']
            field_id = field['id']
            self.field_ids[name] = field_id
            print(f"[ok] campo '{name}' criado: {field_id}")
            return field_id
        
        print(f"[erro] falha ao criar campo '{name}'")
        return None
    
    def configure_fields(self):
        """configura campos customizados"""
        print("\n[3/7] configurando campos customizados...")
        
        # campo priority
        self.add_custom_field(
            'Priority',
            'single_select',
            ['Critical', 'High', 'Medium', 'Low']
        )
        
        # campo story points
        self.add_custom_field('Story Points', 'number')
        
        # campo component
        self.add_custom_field(
            'Component',
            'single_select',
            ['DSL', 'Blender', 'OpenFOAM', 'Automation', 'Tests', 'Docs', 'CI/CD', 'API', 'Frontend']
        )
        
        # campo sprint (iteration)
        self.add_custom_field('Sprint', 'iteration')
        
        return True
    
    def get_repo_issues(self):
        """lista todas as issues do repositorio"""
        print("\n[4/7] buscando issues do repositorio...")
        
        issues = self.run_gh_command([
            'issue', 'list',
            '--limit', '100',
            '--state', 'all',
            '--json', 'number,title,state,labels'
        ], parse_json=True)
        
        if issues:
            print(f"[ok] encontradas {len(issues)} issues")
            return issues
        
        return []
    
    def add_issue_to_project(self, issue_number):
        """adiciona issue ao projeto"""
        query = '''
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {
            projectId: $projectId,
            contentId: $contentId
          }) {
            item {
              id
            }
          }
        }
        '''
        
        # pegar issue node id
        issue_data = self.run_gh_command([
            'api', f'repos/:owner/:repo/issues/{issue_number}'
        ], parse_json=True)
        
        if not issue_data:
            return None
        
        content_id = issue_data['node_id']
        
        variables = {
            'projectId': self.project_id,
            'contentId': content_id
        }
        
        result = self.run_gh_command([
            'api', 'graphql',
            '-f', f'query={query}',
            '-f', f'variables={json.dumps(variables)}'
        ], parse_json=True)
        
        if result and 'data' in result:
            item = result['data']['addProjectV2ItemById']['item']
            return item['id']
        
        return None
    
    def add_all_issues_to_project(self):
        """adiciona todas as issues ao projeto"""
        print("\n[5/7] adicionando issues ao projeto...")
        
        issues = self.get_repo_issues()
        
        added_count = 0
        for issue in issues:
            number = issue['number']
            title = issue['title']
            
            print(f"[info] adicionando issue #{number}: {title[:50]}...")
            
            item_id = self.add_issue_to_project(number)
            
            if item_id:
                print(f"[ok] issue #{number} adicionada")
                added_count += 1
            else:
                print(f"[erro] falha ao adicionar issue #{number}")
        
        print(f"\n[ok] {added_count}/{len(issues)} issues adicionadas")
        return True
    
    def configure_status_for_issues(self):
        """configura status das issues (done/backlog)"""
        print("\n[6/7] configurando status das issues...")
        
        # issues 2-9 devem ir para "Done"
        # issues 10+ devem ir para "Backlog"
        
        # nota: configuracao de status requer API mais complexa
        # por enquanto, sera feito manualmente
        
        print("[info] status sera configurado manualmente via web")
        print("      issues #2-#9 → Done")
        print("      issues #10+ → Backlog")
        
        return True
    
    def print_next_steps(self):
        """imprime proximos passos"""
        print("\n" + "="*70)
        print("  PROJETO CRIADO COM SUCESSO!")
        print("="*70)
        print()
        print("proximos passos (manuais):")
        print()
        print("1. acessar projeto:")
        print(f"   https://github.com/users/{self.owner_login}/projects")
        print()
        print("2. configurar board:")
        print("   - adicionar coluna 'Backlog' (arrastar do menu)")
        print("   - adicionar coluna 'Review' (arrastar do menu)")
        print("   - renomear 'In Progress' para 'In Progress' (se necessario)")
        print("   - ordem final: Backlog → Todo → In Progress → Review → Done")
        print()
        print("3. configurar wip limit:")
        print("   - clicar em '...' na coluna 'In Progress'")
        print("   - 'Set column limit' → 3")
        print()
        print("4. mover issues para status correto:")
        print("   - issues #2-#9 → Done (concluidas)")
        print("   - issue #10 (analise) → Todo")
        print("   - issue #11 (docker) → Todo")
        print("   - issue #12 (ci/cd) → Todo")
        print("   - issues #13-#17 → Backlog")
        print()
        print("5. configurar campos customizados nas issues:")
        print("   - abrir cada issue")
        print("   - preencher: Priority, Story Points, Component, Sprint")
        print()
        print("6. ativar workflows (automacoes):")
        print("   - Settings → Workflows")
        print("   - ativar: 'Item closed', 'Item added'")
        print()
        print("documentacao completa:")
        print("  .github/GITHUB_PROJECTS_SETUP.md")
        print()
    
    def run(self):
        """executa criacao completa do projeto"""
        print("="*70)
        print("  CRIADOR AUTOMATICO DE GITHUB PROJECT")
        print("="*70)
        print()
        
        # passo 1: autenticar
        print("[1/7] verificando autenticacao...")
        if not self.get_owner_login():
            print("[erro] nao foi possivel autenticar")
            print("execute: gh auth login")
            return False
        
        # passo 2: criar projeto
        if not self.create_project():
            return False
        
        # passo 3: configurar campos
        if not self.configure_fields():
            return False
        
        # passo 4-5: adicionar issues
        if not self.add_all_issues_to_project():
            return False
        
        # passo 6: configurar status
        self.configure_status_for_issues()
        
        # passo 7: proximos passos
        self.print_next_steps()
        
        return True

def main():
    """funcao principal"""
    creator = GitHubProjectCreator()
    
    success = creator.run()
    
    if success:
        print("✅ projeto criado com sucesso!")
        sys.exit(0)
    else:
        print("❌ erro ao criar projeto")
        sys.exit(1)

if __name__ == "__main__":
    main()

