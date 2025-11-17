#!/usr/bin/env python3
# script de limpeza automatica de arquivos temporarios e cache
import os
import sys
import shutil
from pathlib import Path
import time

class ProjectCleanup:
    """classe para limpeza automatica do projeto"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.total_freed = 0
        self.files_removed = 0
        self.dirs_removed = 0
        
    def get_size(self, path):
        """retorna tamanho de arquivo ou diretorio em bytes"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total = 0
            for item in path.rglob('*'):
                if item.is_file():
                    try:
                        total += item.stat().st_size
                    except:
                        pass
            return total
        return 0
    
    def format_size(self, bytes_size):
        """formata tamanho em bytes para legivel"""
        for unit in ['b', 'kb', 'mb', 'gb']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} tb"
    
    def clean_python_cache(self):
        """limpa arquivos __pycache__ e .pyc"""
        print("\n[1/7] limpando cache python...")
        
        patterns = ['__pycache__', '*.pyc', '*.pyo']
        
        for pattern in patterns:
            for item in self.project_root.rglob(pattern):
                try:
                    size = self.get_size(item)
                    
                    if item.is_dir():
                        shutil.rmtree(item)
                        self.dirs_removed += 1
                    else:
                        item.unlink()
                        self.files_removed += 1
                    
                    self.total_freed += size
                    print(f"  removido: {item.relative_to(self.project_root)}")
                    
                except Exception as e:
                    print(f"  erro ao remover {item}: {e}")
    
    def clean_temp_files(self):
        """limpa arquivos temporarios"""
        print("\n[2/7] limpando arquivos temporarios...")
        
        temp_dir = self.project_root / "temp"
        
        if temp_dir.exists():
            size = self.get_size(temp_dir)
            
            try:
                shutil.rmtree(temp_dir)
                temp_dir.mkdir()
                
                self.total_freed += size
                self.dirs_removed += 1
                print(f"  temp/ limpo ({self.format_size(size)})")
                
            except Exception as e:
                print(f"  erro ao limpar temp/: {e}")
        else:
            print("  temp/ nao existe")
    
    def clean_blender_autosave(self):
        """limpa arquivos de autosave do blender"""
        print("\n[3/7] limpando autosave do blender...")
        
        patterns = ['*.blend1', '*.blend2']
        count = 0
        
        for pattern in patterns:
            for item in self.project_root.rglob(pattern):
                try:
                    size = self.get_size(item)
                    item.unlink()
                    
                    self.total_freed += size
                    self.files_removed += 1
                    count += 1
                    print(f"  removido: {item.relative_to(self.project_root)}")
                    
                except Exception as e:
                    print(f"  erro ao remover {item}: {e}")
        
        if count == 0:
            print("  nenhum arquivo de autosave encontrado")
    
    def clean_openfoam_logs(self):
        """limpa logs do openfoam"""
        print("\n[4/7] limpando logs openfoam...")
        
        cfd_dir = self.project_root / "generated" / "cfd"
        
        if not cfd_dir.exists():
            print("  generated/cfd/ nao existe")
            return
        
        log_patterns = ['log.*', '*.log']
        count = 0
        
        for pattern in log_patterns:
            for item in cfd_dir.rglob(pattern):
                if item.is_file():
                    try:
                        size = self.get_size(item)
                        item.unlink()
                        
                        self.total_freed += size
                        self.files_removed += 1
                        count += 1
                        print(f"  removido: {item.relative_to(self.project_root)}")
                        
                    except Exception as e:
                        print(f"  erro ao remover {item}: {e}")
        
        if count == 0:
            print("  nenhum log encontrado")
    
    def clean_old_simulations(self, days_old=7):
        """limpa simulacoes antigas"""
        print(f"\n[5/7] limpando simulacoes antigas (>{days_old} dias)...")
        
        cfd_dir = self.project_root / "generated" / "cfd"
        
        if not cfd_dir.exists():
            print("  generated/cfd/ nao existe")
            return
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        count = 0
        
        for case_dir in cfd_dir.iterdir():
            if case_dir.is_dir():
                try:
                    # verificar data de modificacao
                    mtime = case_dir.stat().st_mtime
                    
                    if mtime < cutoff_time:
                        size = self.get_size(case_dir)
                        shutil.rmtree(case_dir)
                        
                        self.total_freed += size
                        self.dirs_removed += 1
                        count += 1
                        
                        age_days = (time.time() - mtime) / (24 * 60 * 60)
                        print(f"  removido: {case_dir.name} ({age_days:.0f} dias)")
                        
                except Exception as e:
                    print(f"  erro ao remover {case_dir.name}: {e}")
        
        if count == 0:
            print(f"  nenhuma simulacao antiga encontrada")
    
    def clean_git_ignored(self):
        """limpa arquivos ignorados pelo git"""
        print("\n[6/7] limpando arquivos git-ignored...")
        
        try:
            result = subprocess.run(
                ['git', 'clean', '-fdX', '--dry-run'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    print(f"  encontrados {len(lines)} itens")
                    
                    response = input("  remover? (s/n) [n]: ").strip().lower()
                    
                    if response in ['s', 'sim', 'y', 'yes']:
                        result = subprocess.run(
                            ['git', 'clean', '-fdX'],
                            capture_output=True,
                            text=True,
                            timeout=30,
                            cwd=self.project_root
                        )
                        print("  arquivos removidos")
                    else:
                        print("  pulado")
                else:
                    print("  nenhum arquivo git-ignored encontrado")
            else:
                print("  git clean falhou")
                
        except FileNotFoundError:
            print("  git nao disponivel")
        except Exception as e:
            print(f"  erro: {e}")
    
    def clean_test_outputs(self):
        """limpa arquivos de teste"""
        print("\n[7/7] limpando arquivos de teste...")
        
        test_patterns = ['test_*.bed', 'test_*.json', 'test_*.blend', 'test_report.json']
        count = 0
        
        for pattern in test_patterns:
            for item in self.project_root.rglob(pattern):
                if item.is_file():
                    try:
                        size = self.get_size(item)
                        item.unlink()
                        
                        self.total_freed += size
                        self.files_removed += 1
                        count += 1
                        print(f"  removido: {item.relative_to(self.project_root)}")
                        
                    except Exception as e:
                        print(f"  erro ao remover {item}: {e}")
        
        if count == 0:
            print("  nenhum arquivo de teste encontrado")
    
    def show_summary(self):
        """mostra resumo da limpeza"""
        print("\n" + "="*70)
        print("  RESUMO DA LIMPEZA")
        print("="*70)
        print(f"\narquivos removidos: {self.files_removed}")
        print(f"diretorios removidos: {self.dirs_removed}")
        print(f"espaco liberado: {self.format_size(self.total_freed)}")
    
    def cleanup(self, clean_old=False, days_old=7):
        """executa limpeza completa"""
        print("="*70)
        print("  LIMPEZA AUTOMATICA DO PROJETO")
        print("="*70)
        print(f"projeto: {self.project_root}")
        
        # executar limpezas
        self.clean_python_cache()
        self.clean_temp_files()
        self.clean_blender_autosave()
        self.clean_openfoam_logs()
        
        if clean_old:
            self.clean_old_simulations(days_old)
        
        self.clean_test_outputs()
        
        # resumo
        self.show_summary()

def main():
    """funcao principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='limpeza automatica do projeto')
    parser.add_argument('--clean-old', action='store_true',
                       help='remover simulacoes antigas')
    parser.add_argument('--days', type=int, default=7,
                       help='dias para considerar simulacao antiga (padrao: 7)')
    parser.add_argument('--dry-run', action='store_true',
                       help='apenas mostrar o que seria removido')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("[modo dry-run] nenhum arquivo sera removido\n")
    
    # executar limpeza
    cleanup = ProjectCleanup()
    cleanup.cleanup(clean_old=args.clean_old, days_old=args.days)
    
    print("\n[concluido] limpeza finalizada")

if __name__ == "__main__":
    import subprocess  # importar aqui para evitar erro se nao usado
    main()

