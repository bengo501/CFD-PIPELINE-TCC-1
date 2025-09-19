#!/usr/bin/env python3
"""
demonstracao completa do pipeline DSL -> params.json -> blender
mostra o fluxo completo conforme proposto no TCC
"""

import sys
import json
from pathlib import Path

# adicionar caminhos
sys.path.append(str(Path(__file__).parent / 'compiler'))
sys.path.append(str(Path(__file__).parent / 'integration'))

from bed_compiler import BedCompiler
from blender_adapter import BlenderAdapter

def demonstrar_pipeline(arquivo_bed: str):
    """demonstra o pipeline completo da DSL"""
    print(f"\n{'='*60}")
    print(f"DEMONSTRAÇÃO PIPELINE DSL - {Path(arquivo_bed).name}")
    print(f"{'='*60}")
    
    # ETAPA 1: Compilar arquivo .bed
    print("\n1️⃣ COMPILAÇÃO .bed -> params.json")
    print("-" * 40)
    
    compiler = BedCompiler()
    params = compiler.parse_bed_file(arquivo_bed)
    
    if not params:
        print("❌ Erro na compilação:")
        for error in compiler.errors:
            print(f"   - {error}")
        return False
    
    print("✅ Compilação bem-sucedida!")
    print(f"   Hash: {params.hash}")
    print(f"   Versão: {params.version}")
    
    # Salvar params.json
    params_file = arquivo_bed.replace('.bed', '_params.json')
    if compiler.compile_to_json(params, params_file):
        print(f"   Arquivo salvo: {Path(params_file).name}")
    else:
        print("❌ Erro ao salvar params.json")
        return False
    
    # ETAPA 2: Carregar com adaptador
    print("\n2️⃣ CARREGAMENTO params.json -> adaptador")
    print("-" * 40)
    
    try:
        adapter = BlenderAdapter(params_file)
        print("✅ Adaptador carregado com sucesso!")
        
        # Mostrar configurações extraídas
        altura, diametro, espessura = adapter.get_bed_geometry()
        particles_config = adapter.get_particles_config()
        packing_config = adapter.get_packing_config()
        
        print(f"   Geometria: Ø{diametro*100:.1f}cm × {altura*100:.1f}cm")
        print(f"   Partículas: {particles_config['quantidade']} {particles_config['kind']}")
        print(f"   Física: {packing_config['substeps']} substeps, seed {particles_config['seed']}")
        
    except Exception as e:
        print(f"❌ Erro no adaptador: {e}")
        return False
    
    # ETAPA 3: Mostrar parâmetros para Blender
    print("\n3️⃣ PARÂMETROS PARA BLENDER")
    print("-" * 40)
    
    print("✅ Parâmetros extraídos para scripts Blender:")
    print(f"   • criar_cilindro_oco(altura={altura}, diametro={diametro}, espessura={espessura})")
    print(f"   • criar_particulas(quantidade={particles_config['quantidade']}, raio={particles_config['diameter']/2})")
    print(f"   • configurar_fisica(gravity={packing_config['gravity']}, seed={particles_config['seed']})")
    
    # ETAPA 4: Mostrar estrutura do JSON
    print("\n4️⃣ ESTRUTURA params.json")
    print("-" * 40)
    
    with open(params_file, 'r') as f:
        data = json.load(f)
    
    print("✅ Estrutura do arquivo params.json:")
    print("   📁 bed:")
    print(f"      - diameter: {data['bed']['diameter']} m")
    print(f"      - height: {data['bed']['height']} m")
    print(f"      - wall_thickness: {data['bed']['wall_thickness']} m")
    
    print("   📁 particles:")
    print(f"      - kind: {data['particles']['kind']}")
    print(f"      - diameter: {data['particles']['diameter']} m")
    if 'count' in data['particles']:
        print(f"      - count: {data['particles']['count']}")
    if 'target_porosity' in data['particles']:
        print(f"      - target_porosity: {data['particles']['target_porosity']}")
    
    print("   📁 export:")
    print(f"      - formats: {data['export']['formats']}")
    print(f"      - wall_mode: {data['export']['wall_mode']}")
    
    # ETAPA 5: Próximos passos
    print("\n5️⃣ PRÓXIMOS PASSOS")
    print("-" * 40)
    
    print("✅ Pipeline pronto para execução:")
    print("   1. Executar script Blender com params.json")
    print("   2. Gerar geometria 3D (STL, OBJ)")
    print("   3. Executar simulação CFD (OpenFOAM)")
    print("   4. Visualizar no dashboard web")
    
    print(f"\n   Comando sugerido:")
    print(f"   blender --background --python leito_extracao.py -- {params_file}")
    
    return True

def main():
    """funcao principal da demonstracao"""
    print("🚀 DEMONSTRAÇÃO COMPLETA - PIPELINE DSL PARA LEITOS EMPACOTADOS")
    print("Conforme proposto no TCC: DSL -> Compilador -> params.json -> Blender -> CFD")
    
    # exemplos para demonstrar
    exemplos = [
        'examples/leito_simples.bed',
        'examples/leito_avancado.bed',
        'examples/leito_cubos.bed'
    ]
    
    sucessos = 0
    
    for exemplo in exemplos:
        if Path(exemplo).exists():
            if demonstrar_pipeline(exemplo):
                sucessos += 1
        else:
            print(f"\n❌ Arquivo não encontrado: {exemplo}")
    
    # resumo final
    print(f"\n{'='*60}")
    print(f"RESUMO FINAL")
    print(f"{'='*60}")
    print(f"✅ Demonstrações bem-sucedidas: {sucessos}/{len(exemplos)}")
    
    if sucessos == len(exemplos):
        print("🎉 PIPELINE DSL IMPLEMENTADO COM SUCESSO!")
        print("\nA linguagem .bed está funcionando conforme especificado no TCC:")
        print("• ✅ DSL declarativa para descrever leitos empacotados")
        print("• ✅ Compilador que valida e normaliza parâmetros")
        print("• ✅ Geração de params.json canônico com hash")
        print("• ✅ Adaptador para integração com scripts Blender")
        print("• ✅ Suporte a diferentes tipos de partículas")
        print("• ✅ Configuração completa de física e exportação")
        print("• ✅ Preparado para integração com OpenFOAM e dashboard")
    else:
        print("⚠️ Alguns testes falharam - verificar implementação")
    
    return 0 if sucessos == len(exemplos) else 1

if __name__ == '__main__':
    exit(main())
