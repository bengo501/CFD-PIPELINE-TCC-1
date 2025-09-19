import bpy
import bmesh
import math
import random
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class LeitoInterativoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Configurador de Leito de Extração")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Variáveis para armazenar os valores
        self.altura = tk.DoubleVar(value=0.1)
        self.diametro = tk.DoubleVar(value=0.025)
        self.espessura_parede = tk.DoubleVar(value=0.002)
        self.num_esferas = tk.IntVar(value=30)
        self.raio_esfera = tk.DoubleVar(value=0.001)
        self.massa_esfera = tk.DoubleVar(value=0.1)
        self.tipo_particula = tk.StringVar(value="esferas")
        self.cor_leito = tk.StringVar(value="azul")
        self.cor_particulas = tk.StringVar(value="verde")
        
        self.criar_interface()
    
    def criar_interface(self):
        # Título principal
        titulo = tk.Label(self.root, text="Configurador de Leito de Extração", 
                         font=("Arial", 16, "bold"))
        titulo.pack(pady=10)
        
        # Frame principal com scroll
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # === SEÇÃO 1: PARÂMETROS DO LEITO ===
        self.criar_secao_leito(scrollable_frame)
        
        # === SEÇÃO 2: PARÂMETROS DAS PARTÍCULAS ===
        self.criar_secao_particulas(scrollable_frame)
        
        # === SEÇÃO 3: PROPRIEDADES FÍSICAS ===
        self.criar_secao_fisica(scrollable_frame)
        
        # === SEÇÃO 4: APARÊNCIA ===
        self.criar_secao_aparencia(scrollable_frame)
        
        # === SEÇÃO 5: BOTÕES ===
        self.criar_botoes(scrollable_frame)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para scroll com mouse
        self.root.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def criar_secao_leito(self, parent):
        # Frame para parâmetros do leito
        frame_leito = ttk.LabelFrame(parent, text="Parâmetros do Leito", padding=10)
        frame_leito.pack(fill=tk.X, padx=5, pady=5)
        
        # Altura
        ttk.Label(frame_leito, text="Altura (metros):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_leito, textvariable=self.altura, width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame_leito, text="(padrão: 0.1 = 10cm)").grid(row=0, column=2, sticky=tk.W, pady=2)
        
        # Diâmetro
        ttk.Label(frame_leito, text="Diâmetro (metros):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_leito, textvariable=self.diametro, width=10).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(frame_leito, text="(padrão: 0.025 = 2.5cm)").grid(row=1, column=2, sticky=tk.W, pady=2)
        
        # Espessura da parede
        ttk.Label(frame_leito, text="Espessura da parede (metros):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_leito, textvariable=self.espessura_parede, width=10).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(frame_leito, text="(padrão: 0.002 = 2mm)").grid(row=2, column=2, sticky=tk.W, pady=2)
    
    def criar_secao_particulas(self, parent):
        # Frame para parâmetros das partículas
        frame_particulas = ttk.LabelFrame(parent, text="Parâmetros das Partículas", padding=10)
        frame_particulas.pack(fill=tk.X, padx=5, pady=5)
        
        # Tipo de partícula
        ttk.Label(frame_particulas, text="Tipo de partícula:").grid(row=0, column=0, sticky=tk.W, pady=2)
        tipo_combo = ttk.Combobox(frame_particulas, textvariable=self.tipo_particula, 
                                 values=["esferas", "cilindros", "cubos"], state="readonly", width=15)
        tipo_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Número de partículas
        ttk.Label(frame_particulas, text="Número de partículas:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_particulas, textvariable=self.num_esferas, width=10).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(frame_particulas, text="(padrão: 30)").grid(row=1, column=2, sticky=tk.W, pady=2)
        
        # Tamanho das partículas
        ttk.Label(frame_particulas, text="Tamanho (metros):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_particulas, textvariable=self.raio_esfera, width=10).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(frame_particulas, text="(padrão: 0.001 = 1mm)").grid(row=2, column=2, sticky=tk.W, pady=2)
    
    def criar_secao_fisica(self, parent):
        # Frame para propriedades físicas
        frame_fisica = ttk.LabelFrame(parent, text="Propriedades Físicas", padding=10)
        frame_fisica.pack(fill=tk.X, padx=5, pady=5)
        
        # Massa das partículas
        ttk.Label(frame_fisica, text="Massa das partículas (kg):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_fisica, textvariable=self.massa_esfera, width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame_fisica, text="(padrão: 0.1)").grid(row=0, column=2, sticky=tk.W, pady=2)
    
    def criar_secao_aparencia(self, parent):
        # Frame para aparência
        frame_aparencia = ttk.LabelFrame(parent, text="Aparência", padding=10)
        frame_aparencia.pack(fill=tk.X, padx=5, pady=5)
        
        # Cor do leito
        ttk.Label(frame_aparencia, text="Cor do leito:").grid(row=0, column=0, sticky=tk.W, pady=2)
        cor_leito_combo = ttk.Combobox(frame_aparencia, textvariable=self.cor_leito,
                                      values=["azul", "vermelho", "verde", "amarelo", "laranja", "roxo"], 
                                      state="readonly", width=15)
        cor_leito_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Cor das partículas
        ttk.Label(frame_aparencia, text="Cor das partículas:").grid(row=1, column=0, sticky=tk.W, pady=2)
        cor_particulas_combo = ttk.Combobox(frame_aparencia, textvariable=self.cor_particulas,
                                           values=["verde", "azul", "vermelho", "amarelo", "laranja", "roxo"], 
                                           state="readonly", width=15)
        cor_particulas_combo.grid(row=1, column=1, padx=5, pady=2)
    
    def criar_botoes(self, parent):
        # Frame para botões
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill=tk.X, padx=5, pady=10)
        
        # Botão Criar
        btn_criar = ttk.Button(frame_botoes, text="Criar Leito", command=self.criar_leito)
        btn_criar.pack(side=tk.LEFT, padx=5)
        
        # Botão Limpar
        btn_limpar = ttk.Button(frame_botoes, text="Limpar Cena", command=self.limpar_cena)
        btn_limpar.pack(side=tk.LEFT, padx=5)
        
        # Botão Sair
        btn_sair = ttk.Button(frame_botoes, text="Sair", command=self.root.quit)
        btn_sair.pack(side=tk.RIGHT, padx=5)
    
    def validar_parametros(self):
        """Valida os parâmetros inseridos pelo usuário"""
        try:
            if self.altura.get() <= 0:
                raise ValueError("Altura deve ser maior que zero")
            if self.diametro.get() <= 0:
                raise ValueError("Diâmetro deve ser maior que zero")
            if self.espessura_parede.get() <= 0:
                raise ValueError("Espessura da parede deve ser maior que zero")
            if self.espessura_parede.get() >= self.diametro.get() / 2:
                raise ValueError("Espessura da parede deve ser menor que o raio")
            if self.num_esferas.get() <= 0:
                raise ValueError("Número de partículas deve ser maior que zero")
            if self.raio_esfera.get() <= 0:
                raise ValueError("Tamanho das partículas deve ser maior que zero")
            if self.massa_esfera.get() <= 0:
                raise ValueError("Massa das partículas deve ser maior que zero")
            
            return True
        except ValueError as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
    
    def limpar_cena(self):
        """Limpa a cena do Blender"""
        def limpar():
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
            messagebox.showinfo("Sucesso", "Cena limpa com sucesso!")
        
        threading.Thread(target=limpar).start()
    
    def criar_leito(self):
        """Cria o leito com os parâmetros especificados"""
        if not self.validar_parametros():
            return
        
        def executar_criacao():
            try:
                # Limpar cena
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.delete(use_global=False)
                
                # Obter parâmetros
                altura = self.altura.get()
                diametro = self.diametro.get()
                espessura_parede = self.espessura_parede.get()
                num_particulas = self.num_esferas.get()
                tamanho_particula = self.raio_esfera.get()
                massa_particula = self.massa_esfera.get()
                tipo_particula = self.tipo_particula.get()
                cor_leito = self.cor_leito.get()
                cor_particulas = self.cor_particulas.get()
                
                # Criar leito
                leito = self.criar_leito_extracao(altura, diametro, espessura_parede)
                
                # Criar tampas
                tampa_superior = self.criar_tampa_superior(altura, diametro)
                tampa_inferior = self.criar_tampa_inferior(diametro)
                
                # Criar partículas
                particulas = self.criar_particulas(num_particulas, diametro/2, altura, 
                                                 tamanho_particula, tipo_particula)
                
                # Aplicar física
                self.aplicar_fisica_colisao(leito, "PASSIVE")
                self.aplicar_fisica_colisao(tampa_superior, "PASSIVE")
                self.aplicar_fisica_colisao(tampa_inferior, "PASSIVE")
                
                for particula in particulas:
                    self.aplicar_fisica_colisao(particula, "RIGID_BODY", massa_particula)
                
                # Aplicar materiais
                self.aplicar_materiais(cor_leito, cor_particulas)
                
                # Configurar cena
                self.configurar_cena()
                
                messagebox.showinfo("Sucesso", 
                    f"Leito criado com sucesso!\n"
                    f"Altura: {altura}m\n"
                    f"Diâmetro: {diametro}m\n"
                    f"Partículas: {num_particulas} {tipo_particula}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao criar leito: {str(e)}")
        
        threading.Thread(target=executar_criacao).start()
    
    def criar_leito_extracao(self, altura, diametro_externo, espessura_parede):
        """Cria o leito de extração principal"""
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
    
    def criar_tampa_superior(self, altura, diametro, espessura=0.003):
        """Cria a tampa superior"""
        bpy.ops.mesh.primitive_cylinder_add(
            radius=diametro/2,
            depth=espessura,
            location=(0, 0, altura + espessura/2)
        )
        tampa_superior = bpy.context.active_object
        tampa_superior.name = "Tampa_Superior"
        return tampa_superior
    
    def criar_tampa_inferior(self, diametro, espessura=0.003):
        """Cria a tampa inferior"""
        bpy.ops.mesh.primitive_cylinder_add(
            radius=diametro/2,
            depth=espessura,
            location=(0, 0, -espessura/2)
        )
        tampa_inferior = bpy.context.active_object
        tampa_inferior.name = "Tampa_Inferior"
        return tampa_inferior
    
    def criar_particulas(self, num_particulas, raio_leito, altura_leito, tamanho, tipo):
        """Cria as partículas especificadas"""
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
    
    def aplicar_fisica_colisao(self, objeto, tipo, massa=0.1):
        """Aplica física de colisão"""
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
    
    def aplicar_materiais(self, cor_leito, cor_particulas):
        """Aplica materiais coloridos"""
        # Mapeamento de cores
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
    
    def configurar_cena(self):
        """Configura a cena"""
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
    
    def executar(self):
        """Executa a interface"""
        self.root.mainloop()

# Função para iniciar a interface
def iniciar_interface():
    """Inicia a interface gráfica"""
    app = LeitoInterativoGUI()
    app.executar()

# Executar se chamado diretamente
if __name__ == "__main__":
    iniciar_interface()
