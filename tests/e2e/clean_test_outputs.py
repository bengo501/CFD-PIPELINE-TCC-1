#!/usr/bin/env python3
# script para limpar saidas dos testes e2e
import shutil
from pathlib import Path

def clean_e2e_outputs():
    """limpa todos os arquivos gerados pelos testes e2e"""
    test_dir = Path(__file__).parent
    
    dirs_to_clean = [
        test_dir / "outputs",
        test_dir / "results",
        test_dir / "logs"
    ]
    
    print("limpando arquivos dos testes e2e...")
    
    total_freed = 0
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            # calcular tamanho
            size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
            
            # remover tudo exceto .gitkeep
            for item in dir_path.iterdir():
                if item.name != '.gitkeep':
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            
            total_freed += size
            print(f"[ok] {dir_path.name}/ limpo ({size / (1024*1024):.2f} mb)")
    
    print(f"\ntotal liberado: {total_freed / (1024*1024):.2f} mb")

if __name__ == "__main__":
    clean_e2e_outputs()

