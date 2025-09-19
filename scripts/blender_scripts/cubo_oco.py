import bpy

def limpar_cena():
    """Remove todos os objetos da cena"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def criar_cubo_oco():
    """Cria um cubo oco com bordas ultra-finas - apenas faces externas"""
    # Criar cubo externo
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    cubo = bpy.context.active_object
    cubo.name = "Cubo_Oco"
    
    # Criar cubo interno MUITO grande para bordas ultra-finas
    bpy.ops.mesh.primitive_cube_add(size=0.98, location=(0, 0, 0))
    cubo_interno = bpy.context.active_object
    
    # Aplicar diferença booleana
    bool_mod = cubo.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cubo_interno
    
    # Aplicar o modificador
    bpy.context.view_layer.objects.active = cubo
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    # Remover cubo interno
    bpy.data.objects.remove(cubo_interno, do_unlink=True)
    
    # Remover face superior
    bpy.context.view_layer.objects.active = cubo
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Selecionar face superior
    for face in cubo.data.polygons:
        if face.center.z > 0.4:
            face.select = True
    
    # Deletar face superior
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return cubo

def criar_tampa():
    """Cria tampa independente"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.5))
    tampa = bpy.context.active_object
    tampa.name = "Tampa"
    return tampa

def aplicar_materiais():
    """Aplica materiais simples"""
    # Material cubo (azul)
    mat_cubo = bpy.data.materials.new(name="Cubo")
    mat_cubo.use_nodes = True
    mat_cubo.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.6, 1.0, 1.0)
    
    # Material tampa (vermelho)
    mat_tampa = bpy.data.materials.new(name="Tampa")
    mat_tampa.use_nodes = True
    mat_tampa.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1.0, 0.3, 0.3, 1.0)
    
    # Aplicar materiais
    cubo = bpy.data.objects.get("Cubo_Oco")
    tampa = bpy.data.objects.get("Tampa")
    
    if cubo:
        cubo.data.materials.append(mat_cubo)
    if tampa:
        tampa.data.materials.append(mat_tampa)

# Executar script
print("Criando cubo oco com bordas ultra-finas...")
limpar_cena()
cubo = criar_cubo_oco()
tampa = criar_tampa()
aplicar_materiais()
print("Pronto! Cubo oco com bordas ultra-finas criado.")
print("Bordas: 0.01 unidades de espessura (mínimo possível)")
