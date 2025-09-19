#!/usr/bin/env python3
"""
Script de teste para verificar se o Blender está funcionando
"""

import subprocess
import os
import tempfile

def testar_blender():
    """Testa se o Blender está funcionando"""
    
    # Caminho do Blender
    blender_path = r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
    
    if not os.path.exists(blender_path):
        print(f"❌ Blender não encontrado em: {blender_path}")
        return False
    
    print(f"✅ Blender encontrado em: {blender_path}")
    
    # Script simples para testar
    script_teste = '''
import bpy
import os

# Criar um cubo simples
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cubo = bpy.context.active_object
cubo.name = "Cubo_Teste"

# Salvar arquivo
arquivo_saida = os.path.join(os.getcwd(), "teste_simples.blend")
bpy.ops.wm.save_as_mainfile(filepath=arquivo_saida)

print(f"Arquivo salvo em: {arquivo_saida}")
'''
    
    # Criar arquivo temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_teste)
        script_file = f.name
    
    try:
        # Executar Blender
        cmd = [
            blender_path,
            '--background',
            '--python', script_file
        ]
        
        print("Executando Blender...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Blender executou com sucesso!")
            
            # Verificar se o arquivo foi criado
            if os.path.exists("teste_simples.blend"):
                print("✅ Arquivo .blend criado com sucesso!")
                return True
            else:
                print("❌ Arquivo .blend não foi criado")
                return False
        else:
            print("❌ Erro na execução do Blender")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        # Limpar arquivo temporário
        try:
            os.unlink(script_file)
        except:
            pass

if __name__ == "__main__":
    print("🧪 Testando Blender...")
    sucesso = testar_blender()
    
    if sucesso:
        print("\n🎉 Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou!")
