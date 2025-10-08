#!/usr/bin/env python3
# script para migrar tarefas do .kanbn para github issues
import os
import sys
import re
from pathlib import Path
import subprocess

class KanbnToGithubMigrator:
    """migra tarefas do kanban local para github issues"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.kanbn_dir = self.project_root / ".kanbn_boards" / "tcc1" / ".kanbn" / "tasks"
        self.repo = None  # será detectado automaticamente
        
    def detect_repo(self):
        """detecta repositório github do git remote"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                # extrair user/repo de: git@github.com:user/repo.git ou https://github.com/user/repo.git
                match = re.search(r'github\.com[:/](.+)/(.+?)(?:\.git)?$', remote_url)
                if match:
                    self.repo = f"{match.group(1)}/{match.group(2)}"
                    print(f"[ok] repositório detectado: {self.repo}")
                    return True
            
            print("[erro] não foi possível detectar repositório github")
            return False
            
        except Exception as e:
            print(f"[erro] erro ao detectar repositório: {e}")
            return False
    
    def parse_task_file(self, task_file):
        """extrai informações do arquivo de tarefa"""
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # extrair frontmatter
        frontmatter_match = re.match(r'---\n(.*?)\n---\n', content, re.DOTALL)
        if not frontmatter_match:
            return None
        
        frontmatter = frontmatter_match.group(1)
        body = content[len(frontmatter_match.group(0)):]
        
        # parsear frontmatter
        task_data = {
            'name': None,
            'tags': [],
            'created': None,
            'body': body.strip()
        }
        
        for line in frontmatter.split('\n'):
            if line.startswith('name:'):
                task_data['name'] = line.split(':', 1)[1].strip()
            elif line.startswith('  -'):
                task_data['tags'].append(line.strip('- ').strip())
            elif line.startswith('created:'):
                task_data['created'] = line.split(':', 1)[1].strip()
        
        # extrair número da tarefa do nome do arquivo
        task_num = task_file.stem.split('-')[1]  # task-001.md → 001
        task_data['number'] = int(task_num)
        
        return task_data
    
    def determine_type_and_labels(self, task_data):
        """determina tipo de issue e labels baseado nas tags"""
        tags = task_data['tags']
        
        # determinar tipo
        if 'bug' in tags:
            issue_type = 'BUG'
        elif 'task' in tags or 'manutencao' in tags or 'testes' in tags:
            issue_type = 'TASK'
        else:
            issue_type = 'FEATURE'
        
        # criar labels
        labels = []
        
        # tags de componente
        component_map = {
            'dsl': 'component-dsl',
            'blender': 'component-blender',
            'openfoam': 'component-openfoam',
            'automacao': 'component-automation',
            'testes': 'component-tests',
            'documentacao': 'component-docs',
            'ci-cd': 'component-cicd',
            'api': 'component-api',
            'frontend': 'component-frontend'
        }
        
        for tag in tags:
            if tag in component_map:
                labels.append(component_map[tag])
        
        # determinar prioridade (baseado no número da tarefa)
        if task_data['number'] <= 10:
            labels.append('priority-high')
        elif task_data['number'] <= 100:
            labels.append('status-done')
        else:
            labels.append('priority-medium')
        
        return issue_type, labels
    
    def create_github_issue_command(self, task_data):
        """gera comando gh cli para criar issue"""
        issue_type, labels = self.determine_type_and_labels(task_data)
        
        title = f"[{issue_type}] {task_data['name']}"
        body = task_data['body']
        labels_str = ','.join(labels)
        
        # comando gh cli
        cmd = [
            'gh', 'issue', 'create',
            '--title', title,
            '--body', body,
            '--label', labels_str
        ]
        
        return cmd, title
    
    def migrate_task(self, task_file, dry_run=True):
        """migra uma tarefa para github issue"""
        print(f"\n[info] processando {task_file.name}...")
        
        task_data = self.parse_task_file(task_file)
        if not task_data:
            print(f"[erro] não foi possível parsear {task_file.name}")
            return False
        
        cmd, title = self.create_github_issue_command(task_data)
        
        if dry_run:
            print(f"[dry-run] comando que seria executado:")
            print(f"  {' '.join(cmd)}")
            print(f"  título: {title}")
            return True
        else:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    issue_url = result.stdout.strip()
                    print(f"[ok] issue criada: {issue_url}")
                    return True
                else:
                    print(f"[erro] falha ao criar issue: {result.stderr}")
                    return False
                    
            except Exception as e:
                print(f"[erro] erro ao executar gh cli: {e}")
                return False
    
    def migrate_all(self, dry_run=True):
        """migra todas as tarefas"""
        print("="*70)
        print("  MIGRAÇÃO KANBN → GITHUB ISSUES")
        print("="*70)
        
        if not self.detect_repo():
            return False
        
        # verificar gh cli
        try:
            subprocess.run(['gh', '--version'], capture_output=True, timeout=5, check=True)
        except:
            print("[erro] github cli (gh) não encontrado")
            print("instale: https://cli.github.com/")
            return False
        
        # listar tarefas
        task_files = sorted(self.kanbn_dir.glob('task-*.md'))
        
        print(f"\n[info] encontradas {len(task_files)} tarefas")
        
        if dry_run:
            print("[modo dry-run] nenhuma issue será criada")
        
        success_count = 0
        
        for task_file in task_files:
            if self.migrate_task(task_file, dry_run):
                success_count += 1
        
        print(f"\n{'='*70}")
        print(f"[resumo] {success_count}/{len(task_files)} tarefas processadas")
        
        if dry_run:
            print("\npara criar as issues de verdade, execute:")
            print("  python .github/migrate_kanbn_to_github.py --execute")
        
        return True

def main():
    """funcao principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='migrar tarefas kanbn para github issues')
    parser.add_argument('--execute', action='store_true',
                       help='executar migração (sem dry-run)')
    parser.add_argument('--task', type=str,
                       help='migrar apenas uma tarefa específica (ex: task-101)')
    
    args = parser.parse_args()
    
    migrator = KanbnToGithubMigrator()
    
    if args.task:
        task_file = migrator.kanbn_dir / f"{args.task}.md"
        if not task_file.exists():
            print(f"[erro] tarefa não encontrada: {args.task}")
            sys.exit(1)
        
        migrator.detect_repo()
        migrator.migrate_task(task_file, dry_run=not args.execute)
    else:
        migrator.migrate_all(dry_run=not args.execute)

if __name__ == "__main__":
    main()

