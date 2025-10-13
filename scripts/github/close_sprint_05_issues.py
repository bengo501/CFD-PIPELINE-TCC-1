#!/usr/bin/env python3
"""
fechar issues do sprint 5 (já concluídas)
"""

import subprocess

REPO = "bengo501/CFD-PIPELINE-TCC-1"

# issues do sprint 5 (task-032 a task-040)
ISSUES_CONCLUIDAS = [77, 78, 79, 80, 81, 82, 83, 84, 85]

COMMENT = "✅ concluído em 12/10/2025 - sprint 5 (interface completa e cfd)"

def fechar_issue(issue_num):
    """fechar uma issue específica"""
    try:
        cmd = [
            "gh", "issue", "close", str(issue_num),
            "--repo", REPO,
            "--comment", COMMENT
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✓ issue #{issue_num} fechada")
            return True
        else:
            print(f"  ✗ erro ao fechar #{issue_num}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ✗ erro: {e}")
        return False


def main():
    print("="*60)
    print("  fechando issues do sprint 5")
    print("="*60)
    
    sucesso = 0
    falha = 0
    
    for issue_num in ISSUES_CONCLUIDAS:
        if fechar_issue(issue_num):
            sucesso += 1
        else:
            falha += 1
    
    print("\n" + "="*60)
    print(f"  {sucesso} issues fechadas, {falha} falhas")
    print("="*60)
    print(f"\nverificar em:")
    print(f"https://github.com/{REPO}/issues?q=is%3Aissue+is%3Aclosed")


if __name__ == "__main__":
    main()

