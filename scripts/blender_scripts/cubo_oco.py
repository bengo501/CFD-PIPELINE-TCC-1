import bpy
def limpar_cena():
    #remove todos os objetos da cena
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    print("cena limpa")

def criar_cubo_oco(tamanho=1.0, espessura_parede=0.1):
    # cria um cubo oco com espessura especifica nas paredes
    # parametros: tamanho: tamanho do cubo externo
    #             espessura_parede: espessura das 4 faces laterais
    # criar cubo externo
    bpy.ops.mesh.primitive_cube_add(size=tamanho, location=(0, 0, 0))
    cubo_externo = bpy.context.active_object
    cubo_externo.name = "cubo_oco"
    
    # calcular tamanho do cubo interno
    # subtrair 2x a espessura (uma para cada lado)
    tamanho_interno = tamanho - (2 * espessura_parede)
    
    # criar cubo interno para fazer o furo
    bpy.ops.mesh.primitive_cube_add(size=tamanho_interno, location=(0, 0, 0))
    cubo_interno = bpy.context.active_object
    cubo_interno.name = "furo_temporario"
    
    # aplicar operacao booleana (subtracao)
    bool_mod = cubo_externo.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cubo_interno
    
    # aplicar o modificador
    bpy.context.view_layer.objects.active = cubo_externo
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    # remover cubo interno temporario
    bpy.data.objects.remove(cubo_interno, do_unlink=True)
    
    # remover face superior para deixar aberto
    remover_face_superior(cubo_externo, tamanho)
    
    print(f"cubo oco criado: tamanho={tamanho}, espessura paredes={espessura_parede}")
    return cubo_externo

def remover_face_superior(cubo, tamanho):
    #remove a face superior do cubo para deixar aberto
    # entrar em modo de edicao
    bpy.context.view_layer.objects.active = cubo
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # selecionar face superior baseado na posicao z
    limite_superior = (tamanho / 2) - 0.01  # um pouco abaixo do topo
    
    for face in cubo.data.polygons:
        if face.center.z > limite_superior:
            face.select = True
    
    # deletar face superior selecionada
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print("face superior removida - cubo agora esta aberto")

def criar_tampa(tamanho=1.0, espessura=0.05, altura_tampa=None):
    #cria uma tampa separada para o cubo
    #parametros: tamanho: tamanho da tampa (deve coincidir com cubo)
    #            espessura: espessura da tampa
    #            altura_tampa: altura onde posicionar (se None, usa metade do tamanho do cubo)
    if altura_tampa is None:
        altura_tampa = (tamanho / 2) + (espessura / 2)
    
    # criar tampa como cilindro achatado (mais realista)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=tamanho/2,
        depth=espessura,
        location=(0, 0, altura_tampa)
    )
    tampa = bpy.context.active_object
    tampa.name = "tampa"
    
    print(f"tampa criada na altura z={altura_tampa}")
    return tampa

def main():
    #funcao principal - cria cubo oco com tampa
    print("=====criando cubo oco=====")
    
    # limpar tudo
    limpar_cena()
    
    # parametros
    tamanho_cubo = 1.0      # 1 unidade de lado
    espessura = 0.1         # 0.1 unidades de espessura nas paredes
    
    # criar geometria
    print("criando cubo oco")
    cubo = criar_cubo_oco(tamanho_cubo, espessura)
    
    print("criando tampa")
    tampa = criar_tampa(tamanho_cubo)
    
    print()
        print("===pronto===")
        print(f"cubo oco criado:")
        print(f"tamanho externo: {tamanho_cubo} u")
        print(f"espessura das paredes: {espessura} u")
        print(f"aberto na parte superior")
        print(f"tampa separada incluida")

# executar
if __name__ == "__main__":
    main()
