#!/usr/bin/env python3
"""
script simplificado para criar issues do sprint 5 sem labels
"""

import subprocess
from pathlib import Path

REPO = "bengo501/CFD-PIPELINE-TCC-1"

TASKS = [
    ("032", "implementar wizard web completo (4 modos)", "wizard web com 4 modos, ajuda, documentação, preview 3d"),
    ("033", "corrigir física blender (animação + colisões)", "corrigir animação automática 20s, tampa sem colisão, mesh collision"),
    ("034", "integrar simulação cfd openfoam no web", "5 endpoints, monitoramento tempo real, background tasks"),
    ("035", "aplicar identidade visual (paleta institucional)", "vinho, verde, amarelo, laranja - wcag aa/aaa"),
    ("036", "implementar internacionalização (pt/en)", "100 traduções, toggle bandeiras, persistência"),
    ("037", "melhorar tipografia e legibilidade", "inter + jetbrains mono, 16px base, line-height 1.7"),
    ("038", "implementar seleção de formatos exportação", "6 formatos: blend, gltf, glb, obj, fbx, stl"),
    ("039", "criar visualização de casos cfd existentes", "listar, analisar, gerenciar casos em output/cfd/"),
    ("040", "implementar pipeline completo end-to-end", "fluxo automatizado completo, log tempo real, 1 clique")
]

print("="*60)
print("  criando issues do sprint 5")
print("="*60)

milestone_num = 9  # milestone já criada

for numero, titulo, descricao in TASKS:
    titulo_completo = f"[task-{numero}] {titulo}"
    
    body = f"""
**status:** ✅ concluído em 12/10/2025

**descrição:**
{descricao}

**sprint:** 5 - interface completa e cfd
**story points:** variável
**milestone:** #{milestone_num}

---
_criado automaticamente via script sync_sprint_05_simple.py_
"""
    
    cmd = [
        "gh", "issue", "create",
        "--repo", REPO,
        "--title", titulo_completo,
        "--body", body,
        "--milestone", str(milestone_num)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ [{numero}] {titulo}")
        else:
            print(f"✗ [{numero}] erro: {result.stderr.strip()}")
    except Exception as e:
        print(f"✗ [{numero}] erro: {e}")

print("\n" + "="*60)
print("  concluído!")
print("="*60)
print(f"\nverificar: https://github.com/{REPO}/milestone/{milestone_num}")

