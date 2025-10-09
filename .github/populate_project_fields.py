#!/usr/bin/env python3
# script para preencher campos das issues automaticamente
import subprocess
import json
import sys
import re
from pathlib import Path

class ProjectFieldsPopulator:
    """preenche campos customizados das issues no projeto"""
    
    def __init__(self):
        self.project_id = None
        self.field_ids = {}
        self.status_field_id = None
        self.field_options = {}
        
        # mapeamento de issues para metadados
        self.issue_metadata = {
            # issues concluidas (done)
            2: {'priority': 'High', 'story_points': 8, 'component': 'DSL', 'status': 'Done'},
            3: {'priority': 'High', 'story_points': 13, 'component': 'Blender', 'status': 'Done'},
            4: {'priority': 'High', 'story_points': 5, 'component': 'DSL', 'status': 'Done'},
            5: {'priority': 'High', 'story_points': 8, 'component': 'OpenFOAM', 'status': 'Done'},
            6: {'priority': 'High', 'story_points': 8, 'component': 'Automation', 'status': 'Done'},
            7: {'priority': 'High', 'story_points': 8, 'component': 'Tests', 'status': 'Done'},
            8: {'priority': 'High', 'story_points': 5, 'component': 'Tests', 'status': 'Done'},
            9: {'priority': 'High', 'story_points': 8, 'component': 'Docs', 'status': 'Done'},
            
            # issues sprint 1 (todo)
            10: {'priority': 'High', 'story_points': 8, 'component': 'Automation', 'status': 'Todo', 'sprint': 'Sprint 1'},
            11: {'priority': 'High', 'story_points': 8, 'component': 'CI/CD', 'status': 'Todo', 'sprint': 'Sprint 1'},
            12: {'priority': 'High', 'story_points': 5, 'component': 'CI/CD', 'status': 'Todo', 'sprint': 'Sprint 1'},
            
            # issues backlog
            13: {'priority': 'Medium', 'story_points': 8, 'component': 'API', 'status': 'Backlog'},
            14: {'priority': 'Medium', 'story_points': 13, 'component': 'Frontend', 'status': 'Backlog'},
            15: {'priority': 'Medium', 'story_points': 5, 'component': 'Automation', 'status': 'Backlog'},
            16: {'priority': 'Medium', 'story_points': 5, 'component': 'Automation', 'status': 'Backlog'},
            17: {'priority': 'Low', 'story_points': 5, 'component': 'Automation', 'status': 'Backlog'},
        }
    
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
                return None
            
            if parse_json and result.stdout.strip():
                return json.loads(result.stdout)
            
            return result.stdout.strip()
            
        except Exception as e:
            print(f"[erro] excecao: {e}")
            return None
    
    def get_project_info(self):
        """busca informacoes do projeto"""
        print("[1/5] buscando projeto...")
        
        # buscar projetos do usuario
        query = '''
        query($login: String!) {
          user(login: $login) {
            projectsV2(first: 20) {
              nodes {
                id
                title
                number
                fields(first: 20) {
                  nodes {
                    ... on ProjectV2Field {
                      id
                      name
                    }
                    ... on ProjectV2SingleSelectField {
                      id
                      name
                      options {
                        id
                        name
                      }
                    }
                    ... on ProjectV2IterationField {
                      id
                      name
                      configuration {
                        iterations {
                          id
                          title
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        '''
        
        # pegar login
        login = self.run_gh_command(['api', 'user', '-q', '.login'])
        if not login:
            return False
        
        variables = {'login': login}
        result = self.run_gh_command([
            'api', 'graphql',
            '-f', f'query={query}',
            '-f', f'variables={json.dumps(variables)}'
        ], parse_json=True)
        
        if not result or 'data' not in result:
            print("[erro] nao foi possivel buscar projeto")
            return False
        
        # encontrar projeto "CFD Pipeline - Scrumban"
        projects = result['data']['user']['projectsV2']['nodes']
        
        for project in projects:
            if 'CFD Pipeline' in project['title']:
                self.project_id = project['id']
                print(f"[ok] projeto encontrado: {project['title']} (#{project['number']})")
                
                # extrair field ids
                for field in project['fields']['nodes']:
                    field_name = field['name']
                    field_id = field['id']
                    
                    self.field_ids[field_name] = field_id
                    
                    # extrair opcoes de single select
                    if 'options' in field:
                        self.field_options[field_name] = {
                            opt['name']: opt['id'] for opt in field['options']
                        }
                    
                    # extrair iteracoes (sprints)
                    if 'configuration' in field and field['configuration']:
                        if 'iterations' in field['configuration']:
                            self.field_options[field_name] = {
                                it['title']: it['id'] 
                                for it in field['configuration']['iterations']
                            }
                    
                    # campo Status (padrao)
                    if field_name == 'Status':
                        self.status_field_id = field_id
                        if 'options' in field:
                            self.field_options['Status'] = {
                                opt['name']: opt['id'] for opt in field['options']
                            }
                
                print(f"[ok] campos encontrados: {list(self.field_ids.keys())}")
                return True
        
        print("[erro] projeto 'CFD Pipeline - Scrumban' nao encontrado")
        return False
    
    def get_project_item_id(self, issue_number):
        """busca project item id da issue"""
        query = '''
        query($projectId: ID!, $issueNumber: Int!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 100) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      number
                    }
                  }
                }
              }
            }
          }
        }
        '''
        
        variables = {
            'projectId': self.project_id,
            'issueNumber': issue_number
        }
        
        result = self.run_gh_command([
            'api', 'graphql',
            '-f', f'query={query}',
            '-f', f'variables={json.dumps(variables)}'
        ], parse_json=True)
        
        if result and 'data' in result:
            items = result['data']['node']['items']['nodes']
            for item in items:
                if item['content'] and item['content']['number'] == issue_number:
                    return item['id']
        
        return None
    
    def update_field(self, item_id, field_name, value):
        """atualiza campo da issue no projeto"""
        field_id = self.field_ids.get(field_name)
        if not field_id:
            print(f"[erro] campo '{field_name}' nao encontrado")
            return False
        
        # determinar tipo de valor
        if field_name in ['Priority', 'Component', 'Status']:
            # single select - precisa do option id
            if field_name not in self.field_options:
                print(f"[erro] opcoes do campo '{field_name}' nao encontradas")
                return False
            
            option_id = self.field_options[field_name].get(value)
            if not option_id:
                print(f"[erro] opcao '{value}' nao encontrada em '{field_name}'")
                return False
            
            query = '''
            mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
              updateProjectV2ItemFieldValue(input: {
                projectId: $projectId,
                itemId: $itemId,
                fieldId: $fieldId,
                value: $value
              }) {
                projectV2Item {
                  id
                }
              }
            }
            '''
            
            variables = {
                'projectId': self.project_id,
                'itemId': item_id,
                'fieldId': field_id,
                'value': {'singleSelectOptionId': option_id}
            }
            
        elif field_name == 'Story Points':
            # number
            query = '''
            mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
              updateProjectV2ItemFieldValue(input: {
                projectId: $projectId,
                itemId: $itemId,
                fieldId: $fieldId,
                value: $value
              }) {
                projectV2Item {
                  id
                }
              }
            }
            '''
            
            variables = {
                'projectId': self.project_id,
                'itemId': item_id,
                'fieldId': field_id,
                'value': {'number': float(value)}
            }
        
        elif field_name == 'Sprint':
            # iteration
            if 'Sprint' not in self.field_options:
                print(f"[aviso] nenhuma iteracao configurada ainda")
                return True  # nao falhar
            
            iteration_id = self.field_options['Sprint'].get(value)
            if not iteration_id:
                print(f"[aviso] sprint '{value}' nao encontrada")
                return True  # nao falhar
            
            query = '''
            mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
              updateProjectV2ItemFieldValue(input: {
                projectId: $projectId,
                itemId: $itemId,
                fieldId: $fieldId,
                value: $value
              }) {
                projectV2Item {
                  id
                }
              }
            }
            '''
            
            variables = {
                'projectId': self.project_id,
                'itemId': item_id,
                'fieldId': field_id,
                'value': {'iterationId': iteration_id}
            }
        
        else:
            print(f"[erro] tipo de campo desconhecido: {field_name}")
            return False
        
        result = self.run_gh_command([
            'api', 'graphql',
            '-f', f'query={query}',
            '-f', f'variables={json.dumps(variables)}'
        ], parse_json=True)
        
        if result and 'data' in result:
            return True
        
        return False
    
    def populate_issue(self, issue_number, metadata):
        """preenche todos os campos de uma issue"""
        print(f"\n[info] processando issue #{issue_number}...")
        
        # buscar project item id
        item_id = self.get_project_item_id(issue_number)
        if not item_id:
            print(f"[erro] issue #{issue_number} nao encontrada no projeto")
            return False
        
        success = True
        
        # atualizar priority
        if 'priority' in metadata:
            if self.update_field(item_id, 'Priority', metadata['priority']):
                print(f"[ok] priority: {metadata['priority']}")
            else:
                print(f"[erro] falha ao atualizar priority")
                success = False
        
        # atualizar story points
        if 'story_points' in metadata:
            if self.update_field(item_id, 'Story Points', metadata['story_points']):
                print(f"[ok] story points: {metadata['story_points']}")
            else:
                print(f"[erro] falha ao atualizar story points")
                success = False
        
        # atualizar component
        if 'component' in metadata:
            if self.update_field(item_id, 'Component', metadata['component']):
                print(f"[ok] component: {metadata['component']}")
            else:
                print(f"[erro] falha ao atualizar component")
                success = False
        
        # atualizar status
        if 'status' in metadata:
            if self.update_field(item_id, 'Status', metadata['status']):
                print(f"[ok] status: {metadata['status']}")
            else:
                print(f"[erro] falha ao atualizar status")
                success = False
        
        # atualizar sprint
        if 'sprint' in metadata:
            if self.update_field(item_id, 'Sprint', metadata['sprint']):
                print(f"[ok] sprint: {metadata['sprint']}")
            else:
                print(f"[aviso] sprint nao configurada")
        
        return success
    
    def populate_all_issues(self):
        """preenche campos de todas as issues"""
        print("\n[3/5] preenchendo campos das issues...")
        
        success_count = 0
        total = len(self.issue_metadata)
        
        for issue_number, metadata in self.issue_metadata.items():
            if self.populate_issue(issue_number, metadata):
                success_count += 1
        
        print(f"\n[ok] {success_count}/{total} issues configuradas")
        return True
    
    def print_summary(self):
        """imprime resumo"""
        print("\n" + "="*70)
        print("  CAMPOS PREENCHIDOS COM SUCESSO!")
        print("="*70)
        print()
        
        # contar por status
        done_count = sum(1 for m in self.issue_metadata.values() if m['status'] == 'Done')
        todo_count = sum(1 for m in self.issue_metadata.values() if m['status'] == 'Todo')
        backlog_count = sum(1 for m in self.issue_metadata.values() if m['status'] == 'Backlog')
        
        # contar story points
        total_points = sum(m['story_points'] for m in self.issue_metadata.values())
        done_points = sum(m['story_points'] for m in self.issue_metadata.values() if m['status'] == 'Done')
        sprint_points = sum(m['story_points'] for m in self.issue_metadata.values() if m.get('sprint') == 'Sprint 1')
        
        print(f"issues por status:")
        print(f"  Done: {done_count} issues ({done_points} pts)")
        print(f"  Todo: {todo_count} issues")
        print(f"  Backlog: {backlog_count} issues")
        print()
        print(f"sprint 1:")
        print(f"  issues: {todo_count}")
        print(f"  story points: {sprint_points}")
        print()
        print(f"total geral:")
        print(f"  issues: {len(self.issue_metadata)}")
        print(f"  story points: {total_points}")
        print()
        print("proximo passo:")
        print("  editar sprints/sprint-01.md e iniciar trabalho!")
        print()
    
    def run(self):
        """executa preenchimento completo"""
        print("="*70)
        print("  PREENCHEDOR AUTOMATICO DE CAMPOS")
        print("="*70)
        print()
        
        # passo 1: buscar projeto
        if not self.get_project_info():
            return False
        
        # passo 2: popular issues
        if not self.populate_all_issues():
            return False
        
        # passo 3: resumo
        self.print_summary()
        
        return True

def main():
    """funcao principal"""
    populator = ProjectFieldsPopulator()
    
    success = populator.run()
    
    if success:
        print("✅ campos preenchidos com sucesso!")
        sys.exit(0)
    else:
        print("❌ erro ao preencher campos")
        sys.exit(1)

if __name__ == "__main__":
    main()

