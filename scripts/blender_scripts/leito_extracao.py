import bpy # importar o blender 
import math 
import random

# =============
# Limpar cena =
# =========================================================================================
def limpar_cena():
    #remove todos os objetos da cena
    bpy.ops.object.select_all(action='SELECT') #selecionar todos os objetos da cena
    bpy.ops.object.delete(use_global=False) # deletar todos os objetos da cena
    print("cena limpa")
# =========================================================================================

# ====================
# Criar cilindro oco =
# =========================================================================================
def criar_cilindro_oco(altura=0.1, diametro_externo=0.025, espessura_parede=0.002):
    # cria um cilindro oco (leito de extracao)
    # parametros: altura: altura do leito em metros
    #             diametro_externo: diametro externo em metros  
    #             espessura_parede: espessura da parede em metros
    
    # calcular raios
    raio_externo = diametro_externo / 2 # calcular raio externo baseado no diametro externo dividido por 2
    raio_interno = raio_externo - espessura_parede # calcular raio interno baseado no raio externo e espessura da parede
    
    # criar cilindro externo
    bpy.ops.mesh.primitive_cylinder_add( # criar cilindro com tamanho especifico e localizacao 0,0,0 (centro)
        radius=raio_externo, # raio do cilindro baseado no raio externo
        depth=altura, # altura do cilindro baseado na altura
        location=(0, 0, altura/2) # localizacao do cilindro baseada na altura dividida por 2
    )
    cilindro_externo = bpy.context.active_object # objeto ativo atual
    cilindro_externo.name = "leito_extracao" # nome do objeto leito_extracao
    
    # criar cilindro interno para fazer o furo
    bpy.ops.mesh.primitive_cylinder_add( # criar cilindro com tamanho especifico e localizacao 0,0,0 (centro)
        radius=raio_interno, # raio do cilindro baseado no raio interno
        depth=altura + 0.01,  # um pouco maior para cortar bem
        location=(0, 0, altura/2) # localizacao do cilindro baseada na altura dividida por 2
    )
    cilindro_interno = bpy.context.active_object # objeto ativo atual
    cilindro_interno.name = "furo_temporario" # nome do objeto furo_temporario
    
    # fazer operacao booleana (subtracao)
    bool_mod = cilindro_externo.modifiers.new(name="Boolean", type='BOOLEAN') # criar modificador booleano
    bool_mod.operation = 'DIFFERENCE' # operacao booleana (subtracao)
    bool_mod.object = cilindro_interno # objeto interno para subtrair
    
    # aplicar o modificador
    bpy.context.view_layer.objects.active = cilindro_externo # objeto ativo atual
    bpy.ops.object.modifier_apply(modifier="Boolean") # aplicar o modificador booleano
    
    # remover cilindro interno temporario
    bpy.data.objects.remove(cilindro_interno, do_unlink=True) # remover o cilindro interno
    
    print(f"leito criado: altura={altura}m, diametro={diametro_externo}m")
    return cilindro_externo # retornar o cilindro externo
# =========================================================================================

# =============
# Criar tampa =
# =========================================================================================
def criar_tampa(posicao_z, diametro=0.025, espessura=0.003, nome="tampa"):
    # cria uma tampa circular
    # parametros: posicao_z: posicao vertical da tampa
    #             diametro: diametro da tampa
    #             espessura: espessura da tampa
    #             nome: nome do objeto
    bpy.ops.mesh.primitive_cylinder_add( # criar cilindro com tamanho especifico e localizacao 0,0,0 (centro)
        radius=diametro/2,
        depth=espessura, # espessura do cilindro
        location=(0, 0, posicao_z) # localizacao do cilindro baseada na posicao z
    )
    tampa = bpy.context.active_object # objeto ativo atual
    tampa.name = nome # nome do objeto
    
    print(f"{nome} criada na posicao z={posicao_z}m")
    return tampa
# =========================================================================================

# ==================
# Criar particulas =
# =========================================================================================
def criar_particulas(quantidade=30, raio_leito=0.0125, altura_leito=0.1, raio_particula=0.001):
    # cria particulas esfericas que vao cair no leito    
    # parametros: quantidade: numero de particulas
    #             raio_leito: raio interno do leito
    #             altura_leito: altura do leito
    #             raio_particula: raio de cada particula
    particulas = []
    
    #criar particulas 
    for i in range(quantidade):
        # posicao aleatoria acima do leito para as particulas cairem
        x = random.uniform(-raio_leito * 0.7, raio_leito * 0.7)
        y = random.uniform(-raio_leito * 0.7, raio_leito * 0.7)
        z = altura_leito + 0.02 + (i * 0.005)  # espacar verticalmente para evitar sobreposicao
        
        # criar particula esferica
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=raio_particula,
            location=(x, y, z)
        )
        particula = bpy.context.active_object
        particula.name = f"particula_{i+1:02d}"
        particulas.append(particula)
    
    print(f"{quantidade} particulas criadas")
    return particulas
# =========================================================================================

# ================
# Aplicar fisica =
# =========================================================================================
def aplicar_fisica(objeto, eh_movel=True):
    # aplica fisica de corpo rigido aos objetos    
    # parametros: objeto: objeto do blender
    #             eh_movel: se true, objeto pode se mover (particulas)
    #             se false, objeto eh estatico (leito e tampas)

    # selecionar o objeto
    bpy.context.view_layer.objects.active = objeto
    
    #aplicar fisica de acordo com o tipo de objeto
    if eh_movel:
        # particulas: corpo rigido com gravidade
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        objeto.rigid_body.mass = 0.01  # massa pequena
        objeto.rigid_body.friction = 0.5  # atrito medio
        objeto.rigid_body.restitution = 0.3  # pouco elastica
        print(f"fisica aplicada (movel): {objeto.name}")
    else:
        # leito e tampas: corpo rigido sem gravidade (estatico)
        bpy.ops.rigidbody.object_add(type='PASSIVE')
        objeto.rigid_body.friction = 0.8  # muito atrito para segurar particulas
        objeto.rigid_body.restitution = 0.1  # pouco elastico
        print(f"fisica aplicada (estatico): {objeto.name}")
# =========================================================================================

# =============================
# Configurar simulacao fisica =
# =========================================================================================
def configurar_simulacao_fisica():
    #configura parametros globais da simulacao fisica
    scene = bpy.context.scene
    # configurar mundo da fisica
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    # configurar gravidade (particulas vao cair)
    scene.rigidbody_world.gravity = (0, 0, -9.81)  # gravidade normal
    # configurar qualidade da simulacao
    scene.rigidbody_world.substeps_per_frame = 10  # mais precisao
    scene.rigidbody_world.solver_iterations = 10   # mais estabilidade
    
    print("simulacao fisica configurada")
# =========================================================================================

# ======
# Main =
# =========================================================================================
def main():
    #funcao principal - cria tudo e configura fisica
    print("======criando leito de extracao com fisica=======")
    # limpar tudo
    limpar_cena()
    # parametros do leito
    altura = 0.1          # 10 cm
    diametro = 0.025      # 2.5 cm  
    espessura = 0.002     # 2 mm
    # criar geometria
    print("criando geometria...")
    leito = criar_cilindro_oco(altura, diametro, espessura)
    tampa_inferior = criar_tampa(-espessura/2, diametro, espessura, "tampa_inferior")
    tampa_superior = criar_tampa(altura + espessura/2, diametro, espessura, "tampa_superior")
    # criar particulas
    particulas = criar_particulas(30, diametro/2, altura, 0.001)
    # configurar fisica
    print("configurando fisica...")
    configurar_simulacao_fisica()
    # aplicar fisica ao leito e tampas (estaticos)
    aplicar_fisica(leito, eh_movel=False)
    aplicar_fisica(tampa_inferior, eh_movel=False)  
    aplicar_fisica(tampa_superior, eh_movel=False)
    # aplicar fisica as particulas (moveis)
    for particula in particulas:
        aplicar_fisica(particula, eh_movel=True)
    
    print()
        print("=====pronto=====")
        print("para ver a simulacao:")
        print("1. pressione spacebar para iniciar animacao")
        print("2. ou pressione alt + a ")
        print("3. as particulas vao cair e se acomodar no leito")
        print()
        print(f"objetos criados:")
        print(f"- leito cilindrico oco")
        print(f"- 2 tampas")
        print(f"- {len(particulas)} particulas com fisica")

if __name__ == "__main__":
    main()
# =========================================================================================

