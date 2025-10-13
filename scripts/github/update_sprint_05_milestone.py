#!/usr/bin/env python3
"""
atualizar milestone sprint 5 no github
"""

import subprocess
import json

REPO = "bengo501/CFD-PIPELINE-TCC-1"
MILESTONE_TITLE = "sprint 5 - interface completa e cfd"
ISSUES_SPRINT_5 = [77, 78, 79, 80, 81, 82, 83, 84, 85]  # task-032 a task-040

def encontrar_milestone():
    """encontrar número do milestone sprint 5"""
    cmd = ["gh", "api", f"/repos/{REPO}/milestones", "--jq", f".[] | select(.title==\"{MILESTONE_TITLE}\") | .number"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            milestone_num = int(result.stdout.strip())
            print(f"✓ milestone encontrada: #{milestone_num}")
            return milestone_num
        
        # se não encontrou, já existe uma (milestone #9 criada anteriormente)
        print("✓ usando milestone #9 (já existe)")
        return 9
        
    except Exception as e:
        print(f"erro: {e}")
        return None


def associar_issues_ao_milestone(milestone_num):
    """associar issues ao milestone"""
    print(f"\nassociando {len(ISSUES_SPRINT_5)} issues ao milestone #{milestone_num}...")
    
    sucesso = 0
    for issue_num in ISSUES_SPRINT_5:
        try:
            cmd = [
                "gh", "api",
                f"/repos/{REPO}/issues/{issue_num}",
                "-X", "PATCH",
                "-f", f"milestone={milestone_num}",
                "-f", "state=closed"  # já concluídas
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ issue #{issue_num} → milestone #{milestone_num} (fechada)")
                sucesso += 1
            else:
                print(f"  ✗ erro issue #{issue_num}")
                
        except Exception as e:
            print(f"  ✗ erro: {e}")
    
    return sucesso


def fechar_milestone(milestone_num):
    """fechar milestone (sprint concluído)"""
    try:
        cmd = [
            "gh", "api",
            f"/repos/{REPO}/milestones/{milestone_num}",
            "-X", "PATCH",
            "-f", "state=closed"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n✓ milestone #{milestone_num} fechada (sprint concluído)")
            return True
        else:
            print(f"\n✗ erro ao fechar milestone: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"\n✗ erro: {e}")
        return False


def main():
    print("="*60)
    print("  atualizar milestone sprint 5")
    print("="*60)
    
    # encontrar milestone
    milestone_num = encontrar_milestone()
    
    if not milestone_num:
        print("\nerro: milestone não encontrada")
        return
    
    # associar issues
    sucesso = associar_issues_ao_milestone(milestone_num)
    
    # fechar milestone (sprint concluído)
    fechar_milestone(milestone_num)
    
    print("\n" + "="*60)
    print(f"  {sucesso}/{len(ISSUES_SPRINT_5)} issues atualizadas")
    print("="*60)
    print(f"\nverificar em:")
    print(f"https://github.com/{REPO}/milestone/9")
    print(f"https://github.com/{REPO}/issues?q=milestone%3A%22sprint+5%22")


if __name__ == "__main__":
    main()

