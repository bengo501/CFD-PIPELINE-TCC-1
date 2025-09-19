#!/usr/bin/env python3
# script independente para geracao de leito de extracao
# funciona fora do Blender usando modo headless
import sys
import os
import math
import random 
import argparse # para argumentos de linha de comando
import subprocess # para executar o Blender em modo headless
import tempfile # para criar arquivos temporarios
import json # para ler e escrever arquivos JSON
from pathlib import Path # para manipular caminhos de arquivos

# =======================
# class LeitoStandalone =
# =========================================================================================
class LeitoStandalone:
    def __init__(self):
        self.script_content = self.get_blender_script()
    
# ====================
# get_blender_script =
# =========================================================================================
    def get_blender_script(self):
        # retorna o script Python que sera executado no Blender
        return '''
import bpy
import bmesh
import math
import random
import json
import sys

def limpar_cena():
    # remove todos os objetos da cena
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def criar_leito_extracao(altura, diametro_externo, espessura_parede):
    # cria o leito de extracao principal
    raio_externo = diametro_externo / 2
    raio_interno = raio_externo - espessura_parede
    
    # Criar cilindro externo
    bpy.ops.mesh.primitive_cylinder_add(
        radius=raio_externo,
        depth=altura,
        location=(0, 0, altura/2)
    )
    cilindro_externo = bpy.context.active_object
    cilindro_externo.name = "Leito_Extracao_Externo"
    
    # Criar cilindro interno
    bpy.ops.mesh.primitive_cylinder_add(
        radius=raio_interno,
        depth=altura + 0.01,
        location=(0, 0, altura/2)
    )
    cilindro_interno = bpy.context.active_object
    cilindro_interno.name = "Cilindro_Interno_Temp"
    
    # Aplicar operação booleana
    bool_mod = cilindro_externo.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cilindro_interno
    
    bpy.context.view_layer.objects.active = cilindro_externo
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    bpy.data.objects.remove(cilindro_interno, do_unlink=True)
    
    return cilindro_externo

def criar_tampa_superior(altura, diametro, espessura=0.003):
    # cria a tampa superior
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diametro/2,
        depth=espessura,
        location=(0, 0, altura + espessura/2)
    )
    tampa_superior = bpy.context.active_object
    tampa_superior.name = "Tampa_Superior"
    return tampa_superior

def criar_tampa_inferior(diametro, espessura=0.003):
    # cria a tampa inferior
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diametro/2,
        depth=espessura,
        location=(0, 0, -espessura/2)
    )
    tampa_inferior = bpy.context.active_object
    tampa_inferior.name = "Tampa_Inferior"
    return tampa_inferior

def criar_particulas(num_particulas, raio_leito, altura_leito, tamanho, tipo):
    # cria as particulas especificadas
    particulas = []
    
    for i in range(num_particulas):
        # Posição aleatória
        r = random.uniform(0, raio_leito * 0.8)
        theta = random.uniform(0, 2 * math.pi)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = random.uniform(tamanho, altura_leito - tamanho)
        
        if tipo == "esferas":
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=tamanho,
                location=(x, y, z)
            )
        elif tipo == "cilindros":
            bpy.ops.mesh.primitive_cylinder_add(
                radius=tamanho,
                depth=tamanho*2,
                location=(x, y, z)
            )
        elif tipo == "cubos":
            bpy.ops.mesh.primitive_cube_add(
                size=tamanho*2,
                location=(x, y, z)
            )
        
        particula = bpy.context.active_object
        particula.name = f"{tipo.capitalize()}_{i+1:02d}"
        particulas.append(particula)
    
    return particulas

def aplicar_fisica_colisao(objeto, tipo, massa=0.1):
    # aplica fisica de colisao
    bpy.context.view_layer.objects.active = objeto
    bpy.ops.rigidbody.object_add(type=tipo)
    
    if objeto.rigid_body:
        if tipo == "RIGID_BODY":
            objeto.rigid_body.mass = massa
            objeto.rigid_body.friction = 0.5
            objeto.rigid_body.restitution = 0.3
        else:
            objeto.rigid_body.mass = 0
            objeto.rigid_body.friction = 0.8
            objeto.rigid_body.restitution = 0.1

def aplicar_materiais(cor_leito, cor_particulas):
    # aplica materiais coloridos
    cores = {
        "azul": (0.2, 0.4, 0.8, 1.0),
        "vermelho": (0.8, 0.2, 0.2, 1.0),
        "verde": (0.2, 0.8, 0.2, 1.0),
        "amarelo": (0.8, 0.8, 0.2, 1.0),
        "laranja": (0.8, 0.5, 0.2, 1.0),
        "roxo": (0.5, 0.2, 0.8, 1.0)
    }
    
    # Material do leito
    mat_leito = bpy.data.materials.new(name="Material_Leito")
    mat_leito.use_nodes = True
    mat_leito.node_tree.nodes["Principled BSDF"].inputs[0].default_value = cores[cor_leito]
    
    # Material das partículas
    mat_particulas = bpy.data.materials.new(name="Material_Particulas")
    mat_particulas.use_nodes = True
    mat_particulas.node_tree.nodes["Principled BSDF"].inputs[0].default_value = cores[cor_particulas]
    
    # Aplicar materiais
    leito = bpy.data.objects.get("Leito_Extracao_Externo")
    tampa_sup = bpy.data.objects.get("Tampa_Superior")
    tampa_inf = bpy.data.objects.get("Tampa_Inferior")
    
    if leito:
        leito.data.materials.append(mat_leito)
    if tampa_sup:
        tampa_sup.data.materials.append(mat_leito)
    if tampa_inf:
        tampa_inf.data.materials.append(mat_leito)
    
    # Aplicar material às partículas
    for obj in bpy.data.objects:
        if obj.name.startswith(("Esfera_", "Cilindro_", "Cubo_")):
            obj.data.materials.append(mat_particulas)

def configurar_cena():
    # configura a cena
    # Iluminação
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 5.0
    
    # Câmera
    bpy.ops.object.camera_add(location=(0.1, -0.1, 0.15), 
                             rotation=(math.radians(60), 0, math.radians(45)))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera
    
    # Renderização
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128

def main():
    # funcao principal
    # Ler parâmetros do arquivo JSON
    try:
        with open(sys.argv[-1], 'r') as f:
            params = json.load(f)
    except:
        print("erro ao ler parametros")
        return
    
    # Extrair parametros
    altura = params.get('altura', 0.1)
    diametro = params.get('diametro', 0.025)
    espessura_parede = params.get('espessura_parede', 0.002)
    num_particulas = params.get('num_particulas', 30)
    tamanho_particula = params.get('tamanho_particula', 0.001)
    massa_particula = params.get('massa_particula', 0.1)
    tipo_particula = params.get('tipo_particula', 'esferas')
    cor_leito = params.get('cor_leito', 'azul')
    cor_particulas = params.get('cor_particulas', 'verde')
    output_file = params.get('output_file', 'leito_gerado.blend')
    
    print(f"Criando leito com parametros:")
    print(f"  Altura: {altura}m")
    print(f"  Diâmetro: {diametro}m")
    print(f"  Particulas: {num_particulas} {tipo_particula}")
    
    # Limpar cena
    limpar_cena()
    
    # Criar leito
    leito = criar_leito_extracao(altura, diametro, espessura_parede)
    
    # Criar tampas
    tampa_superior = criar_tampa_superior(altura, diametro)
    tampa_inferior = criar_tampa_inferior(diametro)
    
    # Criar particulas
    particulas = criar_particulas(num_particulas, diametro/2, altura, 
                                 tamanho_particula, tipo_particula)
    
    # Aplicar fisica
    aplicar_fisica_colisao(leito, "PASSIVE")
    aplicar_fisica_colisao(tampa_superior, "PASSIVE")
    aplicar_fisica_colisao(tampa_inferior, "PASSIVE")
    
    for particula in particulas:
        aplicar_fisica_colisao(particula, "RIGID_BODY", massa_particula)
    
    # Aplicar materiais
    aplicar_materiais(cor_leito, cor_particulas)
    
    # Configurar cena
    configurar_cena()
    
    # Salvar arquivo
    output_path = os.path.abspath(output_file)
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    
    print(f"Leito criado e salvo em: {output_file}")

if __name__ == "__main__":
    main()
'''
    
    def criar_parametros_json(self, **kwargs):
        """Cria arquivo JSON com parâmetros"""
        params = {
            'altura': kwargs.get('altura', 0.1),
            'diametro': kwargs.get('diametro', 0.025),
            'espessura_parede': kwargs.get('espessura_parede', 0.002),
            'num_particulas': kwargs.get('num_particulas', 30),
            'tamanho_particula': kwargs.get('tamanho_particula', 0.001),
            'massa_particula': kwargs.get('massa_particula', 0.1),
            'tipo_particula': kwargs.get('tipo_particula', 'esferas'),
            'cor_leito': kwargs.get('cor_leito', 'azul'),
            'cor_particulas': kwargs.get('cor_particulas', 'verde'),
            'output_file': kwargs.get('output_file', 'leito_gerado.blend')
        }
        
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(params, temp_file, indent=2)
        temp_file.close()
        
        return temp_file.name
    
    def encontrar_blender(self):
        """Tenta encontrar o executável do Blender"""
        possiveis_caminhos = [
            # Windows - Caminhos específicos por versão
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.4\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender\blender.exe",
            # Linux
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            # macOS
            "/Applications/Blender.app/Contents/MacOS/Blender",
        ]
        
        # Verificar PATH
        try:
            result = subprocess.run(['blender', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return 'blender'
        except:
            pass
        
        # Verificar caminhos específicos
        for caminho in possiveis_caminhos:
            if os.path.exists(caminho):
                return caminho
        
        return None
    
    def gerar_leito(self, **kwargs):
        """Gera o leito usando Blender em modo headless"""
        # Encontrar Blender
        blender_path = self.encontrar_blender()
        if not blender_path:
            raise RuntimeError("Blender nao encontrado. Instale o Blender ou adicione ao PATH")
        
        print(f"Usando Blender: {blender_path}")
        
        # criar arquivo de parametros
        params_file = self.criar_parametros_json(**kwargs)
        
        # criar arquivo de script temporario
        script_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        script_file.write(self.script_content)
        script_file.close()
        
        try:
            # executar Blender em modo headless
            cmd = [
                blender_path,
                '--background',  # Modo headless
                '--python', script_file.name,
                '--',  # Separador para argumentos do script
                params_file
            ]
            
            print("Executando Blender...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(" Leito gerado com sucesso")
                print(f"📁 Arquivo salvo: {kwargs.get('output_file', 'leito_gerado.blend')}")
            else:
                print(" Erro ao gerar leito:")
                print(result.stderr)
                raise RuntimeError("Falha na execução do Blender")
                
        finally:
            # limpar arquivos temporarios
            try:
                os.unlink(params_file)
                os.unlink(script_file)
            except:
                pass  # Ignora erros na limpeza

def main():
    # funcao principal com interface de linha de comando
    parser = argparse.ArgumentParser(description='Gerador de Leito de Extração Standalone')
    
    # parametros do leito
    parser.add_argument('--altura', type=float, default=0.1, 
                       help='Altura do leito em metros (padrao: 0.1)')
    parser.add_argument('--diametro', type=float, default=0.025, 
                       help='Diametro do leito em metros (padrao: 0.025)')
    parser.add_argument('--espessura-parede', type=float, default=0.002, 
                       help='Espessura da parede em metros (padrao: 0.002)')
    
    # parametros das particulas
    parser.add_argument('--num-particulas', type=int, default=30, 
                       help='Numero de particulas (padrao: 30)')
    parser.add_argument('--tamanho-particula', type=float, default=0.001, 
                       help='Tamanho das particulas em metros (padrao: 0.001)')
    parser.add_argument('--massa-particula', type=float, default=0.1, 
                       help='Massa das particulas em kg (padrao: 0.1)')
    parser.add_argument('--tipo-particula', choices=['esferas', 'cilindros', 'cubos'], 
                       default='esferas', help='Tipo de particula (padrao: esferas)')
    
    # Aparência
    parser.add_argument('--cor-leito', choices=['azul', 'vermelho', 'verde', 'amarelo', 'laranja', 'roxo'], 
                       default='azul', help='Cor do leito (padrao: azul)')
    parser.add_argument('--cor-particulas', choices=['azul', 'vermelho', 'verde', 'amarelo', 'laranja', 'roxo'], 
                       default='verde', help='Cor das particulas (padrao: verde)')
    
    # Saída
    parser.add_argument('--output', '-o', default='leito_gerado.blend', 
                       help='Arquivo de saida (padrao: leito_gerado.blend)')
    
    args = parser.parse_args()
    
    # Criar gerador
    gerador = LeitoStandalone()
    
    # Gerar leito
    try:
        gerador.gerar_leito(
            altura=args.altura,
            diametro=args.diametro,
            espessura_parede=args.espessura_parede,
            num_particulas=args.num_particulas,
            tamanho_particula=args.tamanho_particula,
            massa_particula=args.massa_particula,
            tipo_particula=args.tipo_particula,
            cor_leito=args.cor_leito,
            cor_particulas=args.cor_particulas,
            output_file=args.output
        )
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
