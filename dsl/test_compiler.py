#!/usr/bin/env python3
"""
script de teste para o compilador .bed
demonstra o funcionamento completo da DSL
"""

import sys
import json
from pathlib import Path

# adicionar o compilador ao path
sys.path.append(str(Path(__file__).parent / 'compiler'))

from bed_compiler import BedCompiler

def test_compilation(bed_file: str):
    """testa a compilacao de um arquivo .bed"""
    print(f"\n=== testando: {bed_file} ===")
    
    # compilar
    compiler = BedCompiler()
    params = compiler.parse_bed_file(bed_file)
    
    if not params:
        print("erro na compilacao:")
        for error in compiler.errors:
            print(f"  - {error}")
        return False
    
    # mostrar informacoes
    print(f"compilacao bem-sucedida!")
    print(f"hash: {params.hash}")
    print(f"leito: {params.bed.diameter*100:.1f}cm x {params.bed.height*100:.1f}cm")
    print(f"particulas: {params.particles.kind}, {params.particles.diameter*1000:.1f}mm")
    
    if params.particles.count:
        print(f"quantidade: {params.particles.count} particulas")
    else:
        print(f"porosidade alvo: {params.particles.target_porosity:.1%}")
    
    # salvar params.json
    output_file = bed_file.replace('.bed', '_params.json')
    if compiler.compile_to_json(params, output_file):
        print(f"params.json salvo: {output_file}")
        
        # mostrar trecho do json
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        print("\ntrecho do params.json:")
        print(f"  bed.diameter: {data['bed']['diameter']} m")
        print(f"  bed.height: {data['bed']['height']} m")
        print(f"  particles.kind: {data['particles']['kind']}")
        print(f"  export.formats: {data['export']['formats']}")
        
        return True
    else:
        print("erro ao salvar params.json")
        return False

def main():
    """funcao principal de teste"""
    print("=== teste do compilador .bed ===")
    
    # diretorio de exemplos
    examples_dir = Path(__file__).parent / 'examples'
    
    # testar todos os exemplos
    examples = [
        'leito_simples.bed',
        'leito_avancado.bed', 
        'leito_cubos.bed'
    ]
    
    success_count = 0
    
    for example in examples:
        example_path = examples_dir / example
        if example_path.exists():
            if test_compilation(str(example_path)):
                success_count += 1
        else:
            print(f"\narquivo nao encontrado: {example_path}")
    
    print(f"\n=== resultado final ===")
    print(f"testes bem-sucedidos: {success_count}/{len(examples)}")
    
    if success_count == len(examples):
        print("todos os testes passaram!")
        return 0
    else:
        print("alguns testes falharam")
        return 1

if __name__ == '__main__':
    exit(main())
