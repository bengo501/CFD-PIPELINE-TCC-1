import bpy  # importar o blender 
import math 
import random
import json  # para ler arquivo json
import sys  # para ler argumentos da linha de comando
import argparse  # para processar argumentos
from pathlib import Path  # para trabalhar com caminhos

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
def criar_tampa(posicao_z, diametro=0.025, espessura=0.003, nome="tampa", tem_colisao=True):
    # cria uma tampa circular
    # parametros: posicao_z: posicao vertical da tampa
    #             diametro: diametro da tampa
    #             espessura: espessura da tampa
    #             nome: nome do objeto
    #             tem_colisao: se false, particulas atravessam (tampa superior)
    bpy.ops.mesh.primitive_cylinder_add( # criar cilindro com tamanho especifico e localizacao 0,0,0 (centro)
        radius=diametro/2,
        depth=espessura, # espessura do cilindro
        location=(0, 0, posicao_z) # localizacao do cilindro baseada na posicao z
    )
    tampa = bpy.context.active_object # objeto ativo atual
    tampa.name = nome # nome do objeto
    tampa["tem_colisao"] = tem_colisao  # marcar se tem colisao
    
    print(f"{nome} criada na posicao z={posicao_z}m (colisao: {tem_colisao})")
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
def aplicar_fisica(objeto, eh_movel=True, tem_colisao=True):
    # aplica fisica de corpo rigido aos objetos    
    # parametros: objeto: objeto do blender
    #             eh_movel: se true, objeto pode se mover (particulas)
    #             se false, objeto eh estatico (leito e tampas)
    #             tem_colisao: se false, objeto nao colide (tampa superior)

    # selecionar o objeto
    bpy.context.view_layer.objects.active = objeto
    
    # verificar se objeto tem marcacao de colisao customizada
    if "tem_colisao" in objeto and not objeto["tem_colisao"]:
        print(f"fisica nao aplicada (sem colisao): {objeto.name}")
        return
    
    #aplicar fisica de acordo com o tipo de objeto
    if eh_movel:
        # particulas: corpo rigido com gravidade
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        objeto.rigid_body.mass = 0.01  # massa pequena
        objeto.rigid_body.friction = 0.5  # atrito medio
        objeto.rigid_body.restitution = 0.3  # pouco elastica
        objeto.rigid_body.linear_damping = 0.1  # amortecimento linear
        objeto.rigid_body.angular_damping = 0.1  # amortecimento angular
        print(f"fisica aplicada (movel): {objeto.name}")
    else:
        # leito e tampas: corpo rigido sem gravidade (estatico)
        bpy.ops.rigidbody.object_add(type='PASSIVE')
        objeto.rigid_body.friction = 0.8  # muito atrito para segurar particulas
        objeto.rigid_body.restitution = 0.1  # pouco elastico
        
        # importante: usar mesh collision para cilindro oco
        objeto.rigid_body.collision_shape = 'MESH'
        objeto.rigid_body.mesh_source = 'FINAL'  # usar geometria final (pos-boolean)
        
        print(f"fisica aplicada (estatico, mesh collision): {objeto.name}")
# =========================================================================================

# =============================
# Configurar simulacao fisica =
# =========================================================================================
def configurar_simulacao_fisica(gravidade=-9.81, substeps=10, iterations=10):
    #configura parametros globais da simulacao fisica
    scene = bpy.context.scene
    
    # configurar mundo da fisica
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    # configurar propriedades do mundo da fisica
    if scene.rigidbody_world:
        try:
            # configurar gravidade
            if hasattr(scene.rigidbody_world, 'effector_weights'):
                scene.rigidbody_world.effector_weights.gravity = abs(gravidade) / 9.81
            
            # configurar qualidade da simulacao
            if hasattr(scene.rigidbody_world, 'substeps_per_frame'):
                scene.rigidbody_world.substeps_per_frame = substeps
            
            if hasattr(scene.rigidbody_world, 'solver_iterations'):
                scene.rigidbody_world.solver_iterations = iterations
            
            # configurar velocidade de repouso
            if hasattr(scene.rigidbody_world, 'use_split_impulse'):
                scene.rigidbody_world.use_split_impulse = True
                
            print(f"simulacao fisica configurada (gravidade: {gravidade}, substeps: {substeps}, iterations: {iterations})")
            
        except AttributeError as e:
            print(f"aviso: nao foi possivel configurar todas as propriedades da fisica: {e}")
            print("usando configuracao padrao do blender")
    else:
        print("erro: nao foi possivel criar mundo da fisica")
# =========================================================================================

# =====================
# Executar simulacao =
# =========================================================================================
def executar_simulacao_fisica(tempo_simulacao=5.0, fps=24):
    """
    executa a animacao de fisica para fazer particulas cairem
    
    parametros:
        tempo_simulacao: tempo em segundos da simulacao
        fps: frames por segundo (padrao 24)
    """
    scene = bpy.context.scene
    
    # configurar range de frames
    total_frames = int(tempo_simulacao * fps)
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.frame_current = 1
    
    print(f"\nexecutando simulacao fisica...")
    print(f"tempo: {tempo_simulacao}s | frames: {total_frames} | fps: {fps}")
    
    # executar frame por frame para garantir fisica
    for frame in range(1, total_frames + 1):
        scene.frame_set(frame)
        
        # mostrar progresso a cada 10%
        if frame % (total_frames // 10) == 0 or frame == 1 or frame == total_frames:
            progresso = (frame / total_frames) * 100
            print(f"  progresso: {progresso:.0f}% (frame {frame}/{total_frames})")
    
    print("simulacao fisica executada com sucesso!")
    print("particulas acomodadas no leito\n")
# =========================================================================================

# ==================
# Bake da fisica =
# =========================================================================================
def fazer_bake_fisica(particulas):
    """
    faz bake (congelamento) da fisica nas particulas
    isso converte a simulacao em keyframes fixos
    """
    print("\nfazendo bake da fisica...")
    
    # selecionar todas as particulas
    bpy.ops.object.select_all(action='DESELECT')
    for particula in particulas:
        particula.select_set(True)
    
    # fazer bake
    try:
        # bake to keyframes (converte fisica em animacao)
        bpy.ops.rigidbody.bake_to_keyframes(
            frame_start=bpy.context.scene.frame_start,
            frame_end=bpy.context.scene.frame_end,
            step=1
        )
        print("bake concluido - fisica convertida em keyframes")
        
        # remover rigid body das particulas (agora sao keyframes)
        for particula in particulas:
            if particula.rigid_body:
                bpy.context.view_layer.objects.active = particula
                bpy.ops.rigidbody.object_remove()
        
        print("rigid body removido - particulas estao fixas nas posicoes finais")
        
    except Exception as e:
        print(f"aviso: erro no bake: {e}")
        print("particulas manterao fisica ativa")
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
    tampa_inferior = criar_tampa(-espessura/2, diametro, espessura, "tampa_inferior", tem_colisao=True)
    tampa_superior = criar_tampa(altura + espessura/2, diametro, espessura, "tampa_superior", tem_colisao=False)
    # criar particulas
    particulas = criar_particulas(30, diametro/2, altura, 0.001)
    # configurar fisica
    print("configurando fisica...")
    configurar_simulacao_fisica()
    # aplicar fisica ao leito e tampas (estaticos)
    aplicar_fisica(leito, eh_movel=False)
    aplicar_fisica(tampa_inferior, eh_movel=False)
    # tampa superior sem colisao (particulas atravessam)
    aplicar_fisica(tampa_superior, eh_movel=False)
    # aplicar fisica as particulas (moveis)
    for particula in particulas:
        aplicar_fisica(particula, eh_movel=True)
    
    # executar simulacao para particulas cairem
    executar_simulacao_fisica(tempo_simulacao=5.0, fps=24)
    
    # fazer bake para fixar posicoes finais
    fazer_bake_fisica(particulas)
    
    print()
    print("=====pronto=====")
    print(f"objetos criados:")
    print(f"- leito cilindrico oco (colisao: mesh)")
    print(f"- tampa inferior (colisao: ativa)")
    print(f"- tampa superior (colisao: desativada)")
    print(f"- {len(particulas)} particulas (posicoes finais apos fisica)")
    print()
    print("particulas ja estao acomodadas dentro do leito!")
    print("abra o arquivo para ver o resultado final")

def ler_parametros_json(json_path):
    """ler parametros do arquivo json"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            params = json.load(f)
        print(f"parametros carregados de: {json_path}")
        return params
    except Exception as e:
        print(f"erro ao ler json: {e}")
        return None

def main_com_parametros():
    """funcao principal que aceita parametros da linha de comando"""
    # processar argumentos apenas se houver '--' nos argumentos
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        # se nao houver argumentos, usar valores padrao
        print("executando com parametros padrao...")
        main()
        return
    
    # criar parser de argumentos
    parser = argparse.ArgumentParser(description='gerar leito empacotado no blender')
    parser.add_argument('--params', type=str, help='caminho do arquivo json com parametros')
    parser.add_argument('--output', type=str, help='caminho do arquivo de saida .blend')
    parser.add_argument('--formats', type=str, default='blend,gltf,glb', 
                        help='formatos de exportacao separados por virgula (blend,gltf,glb,obj,fbx,stl)')
    
    try:
        args = parser.parse_args(argv)
    except:
        # se falhar ao processar argumentos, usar padrao
        print("erro ao processar argumentos, usando padrao...")
        main()
        return
    
    # ler parametros do json se fornecido
    if args.params:
        params = ler_parametros_json(args.params)
        if params:
            # extrair parametros
            bed = params.get('bed', {})
            particles = params.get('particles', {})
            
            # valores com fallback para padrao
            altura = bed.get('height', 0.1)
            diametro = bed.get('diameter', 0.05)
            espessura = bed.get('wall_thickness', 0.002)
            num_particulas = particles.get('count', 100)
            diametro_particula = particles.get('diameter', 0.005)
            
            print(f"parametros do json:")
            print(f"  altura: {altura}m")
            print(f"  diametro: {diametro}m")
            print(f"  espessura parede: {espessura}m")
            print(f"  particulas: {num_particulas}")
            print(f"  diametro particula: {diametro_particula}m")
        else:
            # se falhar ao ler json, usar padrao
            altura = 0.1
            diametro = 0.05
            espessura = 0.002
            num_particulas = 100
            diametro_particula = 0.005
    else:
        # sem json, usar padrao
        altura = 0.1
        diametro = 0.05
        espessura = 0.002
        num_particulas = 100
        diametro_particula = 0.005
    
    try:
        # limpar cena
        limpar_cena()
        
        # criar geometria
        print("criando geometria...")
        leito = criar_cilindro_oco(altura, diametro, espessura)
        print(f"leito criado: altura={altura}m, diametro={diametro}m")
        
        tampa_inferior = criar_tampa(posicao_z=0, diametro=diametro, espessura=0.003, nome="tampa_inferior", tem_colisao=True)
        print("tampa inferior criada (com colisao)")
        
        tampa_superior = criar_tampa(posicao_z=altura, diametro=diametro, espessura=0.003, nome="tampa_superior", tem_colisao=False)
        print("tampa superior criada (sem colisao - particulas atravessam)")
        
        # calcular raio do leito e raio da particula
        raio_leito = (diametro / 2) - espessura  # raio interno
        raio_particula = diametro_particula / 2
        
        particulas = criar_particulas(
            quantidade=num_particulas,
            raio_leito=raio_leito,
            altura_leito=altura,
            raio_particula=raio_particula
        )
        print(f"{num_particulas} particulas criadas")
        
        # configurar fisica
        print("configurando fisica...")
        configurar_simulacao_fisica()
        
        print("aplicando fisica ao leito...")
        aplicar_fisica(leito, eh_movel=False)
        
        print("aplicando fisica as tampas...")
        aplicar_fisica(tampa_inferior, eh_movel=False)  
        aplicar_fisica(tampa_superior, eh_movel=False)
        
        print("aplicando fisica as particulas...")
        for i, particula in enumerate(particulas):
            aplicar_fisica(particula, eh_movel=True)
            if (i + 1) % 20 == 0:
                print(f"  {i + 1}/{num_particulas} particulas processadas")
        
        print("fisica aplicada a todas as particulas")
        
        # obter parametros de empacotamento
        packing = params.get('packing', {}) if params else {}
        tempo_sim = packing.get('max_time', 20.0)  # padrao 20s para garantir acomodacao
        gravidade = packing.get('gravity', -9.81)
        substeps = packing.get('substeps', 10)
        iterations = packing.get('iterations', 10)
        
        # reconfigurar fisica com parametros do json
        print(f"\nreconfigurando fisica com parametros do arquivo...")
        print(f"  gravidade: {gravidade} m/s2")
        print(f"  tempo simulacao: {tempo_sim}s")
        print(f"  substeps: {substeps}")
        print(f"  iterations: {iterations}")
        
        configurar_simulacao_fisica(gravidade=gravidade, substeps=substeps, iterations=iterations)
        
        # executar simulacao para particulas cairem
        print(f"\n{'='*60}")
        print(f"  executando animacao de fisica")
        print(f"{'='*60}")
        print(f"tempo de simulacao: {tempo_sim}s")
        print(f"fps: 24 (frames por segundo)")
        print(f"total de frames: {int(tempo_sim * 24)}")
        print(f"\naguarde - as particulas estao caindo dentro do leito...")
        print(f"isso pode levar alguns minutos dependendo da quantidade...")
        print()
        
        executar_simulacao_fisica(tempo_simulacao=tempo_sim, fps=24)
        
        # fazer bake para fixar posicoes finais
        print(f"\n{'='*60}")
        print(f"  congelando posicoes finais")
        print(f"{'='*60}")
        fazer_bake_fisica(particulas)
        
        print(f"\n{'='*60}")
        print(f"  animacao completa!")
        print(f"{'='*60}")
        print("particulas cairam e se acomodaram dentro do leito")
        print("posicoes finais foram salvas (bake aplicado)")
        print("pronto para exportacao\n")
        
        # salvar arquivo se caminho fornecido
        if args.output:
            print(f"\nsalvando arquivo em: {args.output}")
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # obter formatos desejados
            formats = [f.strip().lower() for f in args.formats.split(',')]
            print(f"formatos selecionados: {', '.join(formats)}")
            
            # salvar arquivo .blend
            if 'blend' in formats:
                try:
                    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
                    print(f"✓ arquivo .blend salvo: {output_path}")
                except Exception as e:
                    print(f"✗ erro ao salvar .blend: {e}")
            
            # exportar para gltf
            if 'gltf' in formats:
                try:
                    gltf_path = output_path.with_suffix('.gltf')
                    bpy.ops.export_scene.gltf(
                        filepath=str(gltf_path),
                        export_format='GLTF_SEPARATE',
                        export_apply=True,
                        export_yup=True,
                        export_lights=True,
                        export_extras=True
                    )
                    print(f"✓ arquivo .gltf exportado: {gltf_path}")
                except Exception as e:
                    print(f"✗ erro ao exportar .gltf: {e}")
            
            # exportar para glb
            if 'glb' in formats:
                try:
                    glb_path = output_path.with_suffix('.glb')
                    bpy.ops.export_scene.gltf(
                        filepath=str(glb_path),
                        export_format='GLB',
                        export_apply=True,
                        export_yup=True,
                        export_lights=True,
                        export_extras=True
                    )
                    print(f"✓ arquivo .glb exportado: {glb_path}")
                except Exception as e:
                    print(f"✗ erro ao exportar .glb: {e}")
            
            # exportar para obj
            if 'obj' in formats:
                try:
                    obj_path = output_path.with_suffix('.obj')
                    bpy.ops.wm.obj_export(
                        filepath=str(obj_path),
                        export_selected_objects=False,
                        apply_modifiers=True,
                        export_normals=True,
                        export_uv=True,
                        export_materials=True
                    )
                    print(f"✓ arquivo .obj exportado: {obj_path}")
                except Exception as e:
                    print(f"✗ erro ao exportar .obj: {e}")
            
            # exportar para fbx
            if 'fbx' in formats:
                try:
                    fbx_path = output_path.with_suffix('.fbx')
                    bpy.ops.export_scene.fbx(
                        filepath=str(fbx_path),
                        use_selection=False,
                        apply_scale_options='FBX_SCALE_ALL',
                        axis_forward='-Z',
                        axis_up='Y',
                        apply_unit_scale=True,
                        mesh_smooth_type='FACE'
                    )
                    print(f"✓ arquivo .fbx exportado: {fbx_path}")
                except Exception as e:
                    print(f"✗ erro ao exportar .fbx: {e}")
            
            # exportar para stl
            if 'stl' in formats:
                try:
                    stl_path = output_path.with_suffix('.stl')
                    bpy.ops.wm.stl_export(
                        filepath=str(stl_path),
                        export_selected_objects=False,
                        apply_modifiers=True,
                        ascii_format=False  # binário é mais compacto
                    )
                    print(f"✓ arquivo .stl exportado: {stl_path}")
                except Exception as e:
                    print(f"✗ erro ao exportar .stl: {e}")
            
            print(f"\nexportação concluída! {len(formats)} formato(s) processado(s)")
        else:
            print("\naviso: caminho de saida nao especificado, arquivo nao foi salvo")
        
        print("\nmodelo 3d gerado com sucesso!")
        
    except Exception as e:
        print(f"\nerro ao gerar modelo: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main_com_parametros()
# =========================================================================================

