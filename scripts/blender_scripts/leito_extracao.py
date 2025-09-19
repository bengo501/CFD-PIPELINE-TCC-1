import bpy
import bmesh
import math
import random

def limpar_cena():
    """
    Remove todos os objetos da cena para começar com uma cena limpa
    """
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    print("Cena limpa.")

def criar_leito_extracao(altura=0.1, diametro_externo=0.025, espessura_parede=0.002):
    """
    Cria o leito de extração principal (cilindro oco)
    
    Args:
        altura (float): Altura do leito em metros (padrão: 0.1m = 10cm)
        diametro_externo (float): Diâmetro externo em metros (padrão: 0.025m = 2.5cm)
        espessura_parede (float): Espessura da parede em metros (padrão: 0.002m = 2mm)
    """
    # Calcular raios
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
    
    # Criar cilindro interno (para operação booleana)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=raio_interno,
        depth=altura + 0.01,  # Ligeiramente maior para garantir corte completo
        location=(0, 0, altura/2)
    )
    cilindro_interno = bpy.context.active_object
    cilindro_interno.name = "Cilindro_Interno_Temp"
    
    # Aplicar operação booleana de diferença
    bool_mod = cilindro_externo.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cilindro_interno
    
    # Aplicar o modificador
    bpy.context.view_layer.objects.active = cilindro_externo
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    # Remover cilindro interno temporário
    bpy.data.objects.remove(cilindro_interno, do_unlink=True)
    
    print(f"Leito de extração criado: altura={altura}m, diâmetro={diametro_externo}m")
    return cilindro_externo

def criar_tampa_superior(altura=0.1, diametro=0.025, espessura=0.003):
    """
    Cria a tampa superior do leito de extração
    
    Args:
        altura (float): Altura do leito para posicionar a tampa
        diametro (float): Diâmetro da tampa
        espessura (float): Espessura da tampa
    """
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diametro/2,
        depth=espessura,
        location=(0, 0, altura + espessura/2)
    )
    tampa_superior = bpy.context.active_object
    tampa_superior.name = "Tampa_Superior"
    
    print(f"Tampa superior criada na posição z={altura + espessura/2}m")
    return tampa_superior

def criar_tampa_inferior(diametro=0.025, espessura=0.003):
    """
    Cria a tampa inferior do leito de extração
    
    Args:
        diametro (float): Diâmetro da tampa
        espessura (float): Espessura da tampa
    """
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diametro/2,
        depth=espessura,
        location=(0, 0, -espessura/2)
    )
    tampa_inferior = bpy.context.active_object
    tampa_inferior.name = "Tampa_Inferior"
    
    print(f"Tampa inferior criada na posição z={-espessura/2}m")
    return tampa_inferior

def criar_esferas(num_esferas=30, raio_leito=0.0125, altura_leito=0.1, raio_esfera=0.001):
    """
    Cria esferas pequenas que cairão dentro do leito de extração
    
    Args:
        num_esferas (int): Número de esferas a serem criadas
        raio_leito (float): Raio interno do leito
        altura_leito (float): Altura do leito
        raio_esfera (float): Raio de cada esfera
    """
    esferas = []
    
    for i in range(num_esferas):
        # Posição aleatória dentro do leito
        # Usar coordenadas polares para distribuição uniforme
        r = random.uniform(0, raio_leito * 0.8)  # 80% do raio para evitar colisão com paredes
        theta = random.uniform(0, 2 * math.pi)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = random.uniform(raio_esfera, altura_leito - raio_esfera)
        
        # Criar esfera
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=raio_esfera,
            location=(x, y, z)
        )
        esfera = bpy.context.active_object
        esfera.name = f"Esfera_{i+1:02d}"
        esferas.append(esfera)
    
    print(f"{num_esferas} esferas criadas com raio {raio_esfera}m")
    return esferas

def aplicar_fisica_colisao(objeto, tipo="RIGID_BODY"):
    """
    Aplica física de colisão a um objeto
    
    Args:
        objeto: Objeto do Blender
        tipo (str): Tipo de corpo rígido ("RIGID_BODY" ou "PASSIVE")
    """
    # Adicionar corpo rígido
    bpy.context.view_layer.objects.active = objeto
    bpy.ops.rigidbody.object_add(type=tipo)
    
    # Configurar propriedades do corpo rígido
    if objeto.rigid_body:
        if tipo == "RIGID_BODY":
            # Para objetos móveis (esferas)
            objeto.rigid_body.mass = 0.1
            objeto.rigid_body.friction = 0.5
            objeto.rigid_body.restitution = 0.3
        else:
            # Para objetos estáticos (leito e tampas)
            objeto.rigid_body.mass = 0
            objeto.rigid_body.friction = 0.8
            objeto.rigid_body.restitution = 0.1
    
    print(f"Física aplicada ao objeto: {objeto.name}")

def aplicar_materiais():
    """
    Aplica materiais coloridos aos objetos para melhor visualização
    """
    # Material para o leito de extração (azul)
    mat_leito = bpy.data.materials.new(name="Material_Leito")
    mat_leito.use_nodes = True
    mat_leito.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.4, 0.8, 1.0)
    
    # Material para tampas (vermelho)
    mat_tampa = bpy.data.materials.new(name="Material_Tampa")
    mat_tampa.use_nodes = True
    mat_tampa.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.2, 0.2, 1.0)
    
    # Material para esferas (verde)
    mat_esfera = bpy.data.materials.new(name="Material_Esfera")
    mat_esfera.use_nodes = True
    mat_esfera.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.8, 0.2, 1.0)
    
    # Aplicar materiais aos objetos
    leito = bpy.data.objects.get("Leito_Extracao_Externo")
    tampa_sup = bpy.data.objects.get("Tampa_Superior")
    tampa_inf = bpy.data.objects.get("Tampa_Inferior")
    
    if leito:
        leito.data.materials.append(mat_leito)
    if tampa_sup:
        tampa_sup.data.materials.append(mat_tampa)
    if tampa_inf:
        tampa_inf.data.materials.append(mat_tampa)
    
    # Aplicar material às esferas
    for i in range(1, 31):
        esfera = bpy.data.objects.get(f"Esfera_{i:02d}")
        if esfera:
            esfera.data.materials.append(mat_esfera)
    
    print("Materiais aplicados aos objetos.")

def configurar_cena():
    """
    Configura a cena para melhor visualização e simulação
    """
    # Configurar iluminação
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 5.0
    
    # Configurar câmera
    bpy.ops.object.camera_add(location=(0.1, -0.1, 0.15), rotation=(math.radians(60), 0, math.radians(45)))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera
    
    # Configurar renderização
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    
    print("Cena configurada para renderização.")

def main():
    """
    Função principal que executa todo o processo de criação do leito de extração
    """
    print("=== CRIANDO LEITO DE EXTRAÇÃO ===")
    print("Especificações:")
    print("- Altura: 10 cm (0.1 m)")
    print("- Diâmetro: 2.5 cm (0.025 m)")
    print("- 30 esferas pequenas")
    print("- Física de colisão habilitada")
    print()
    
    # Limpar cena
    limpar_cena()
    
    # Parâmetros do leito
    altura = 0.1  # 10 cm
    diametro = 0.025  # 2.5 cm
    espessura_parede = 0.002  # 2 mm
    
    # Criar leito de extração
    leito = criar_leito_extracao(altura, diametro, espessura_parede)
    
    # Criar tampas
    tampa_superior = criar_tampa_superior(altura, diametro)
    tampa_inferior = criar_tampa_inferior(diametro)
    
    # Criar esferas
    esferas = criar_esferas(30, diametro/2, altura, 0.001)
    
    # Aplicar física
    aplicar_fisica_colisao(leito, "PASSIVE")
    aplicar_fisica_colisao(tampa_superior, "PASSIVE")
    aplicar_fisica_colisao(tampa_inferior, "PASSIVE")
    
    for esfera in esferas:
        aplicar_fisica_colisao(esfera, "RIGID_BODY")
    
    # Aplicar materiais
    aplicar_materiais()
    
    # Configurar cena
    configurar_cena()
    
    print()
    print("=== LEITO DE EXTRAÇÃO CRIADO COM SUCESSO! ===")
    print("Para executar a simulação física:")
    print("1. Pressione ALT+A para executar a animação")
    print("2. Ou vá para a aba 'Physics' e clique em 'Bake'")
    print("3. Use a barra de espaço para visualizar a simulação")
    print()
    print("Componentes criados:")
    print("- Leito de extração (cilindro oco)")
    print("- Tampa superior")
    print("- Tampa inferior")
    print("- 30 esferas com física")
    print("- Todos os objetos com colisão habilitada")

# Executar o script
if __name__ == "__main__":
    main()
