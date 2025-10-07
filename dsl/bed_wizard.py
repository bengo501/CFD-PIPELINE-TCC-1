#!/usr/bin/env python3
"""
wizard interativo para criar arquivos .bed
permite ao usuario parametrizar leitos empacotados de duas formas:
1. questionario interativo - usuario responde perguntas passo a passo
2. edicao de template padrao - usuario edita um arquivo template
este wizard gera arquivos .bed que sao compilados pelo antlr
"""

# importar bibliotecas necessarias
import os  # para operacoes do sistema operacional (limpar tela, arquivos)
import sys  # para acessar argumentos e sair do programa
import subprocess  # para executar comandos externos (editores, compilador)
import tempfile  # para criar arquivos temporarios
from pathlib import Path  # para trabalhar com caminhos de arquivos
from typing import Dict, Any, List, Optional  # para tipagem de variaveis

class BedWizard:
    """classe principal do wizard para criacao de arquivos .bed"""
    
    def __init__(self):
        """inicializar wizard com parametros vazios"""
        self.params = {}  # dicionario para armazenar parametros do leito
        self.output_file = None  # nome do arquivo de saida
        
    def clear_screen(self):
        """limpar tela do terminal para melhor visualizacao"""
        # usar comando apropriado para windows (cls) ou unix (clear)
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """imprimir cabecalho formatado com titulo"""
        print("=" * 60)
        print(f"  {title}")
        print("=" * 60)
        print()
    
    def print_section(self, title: str):
        """imprimir titulo de secao formatado"""
        print(f"\n--- {title} ---")
    
    def get_input(self, prompt: str, default: str = "", required: bool = True) -> str:
        """obter entrada de texto do usuario com validacao"""
        while True:
            # formatar prompt com valor padrao se disponivel
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "
            
            # obter entrada do usuario (nao remover espacos ainda)
            value = input(full_prompt)
            
            # se for apenas espacos ou vazio e houver padrao, usar padrao
            if not value.strip() and default:
                return default
            
            # remover espacos para validacao
            value = value.strip()
            
            # validar entrada
            if value:
                return value  # retornar valor se fornecido
            elif default and not required:
                return default  # retornar padrao se nao obrigatorio
            elif not required:
                return ""  # retornar vazio se nao obrigatorio
            else:
                print("  aviso: campo obrigatorio!")  # avisar se obrigatorio
    
    def get_number_input(self, prompt: str, default: str = "", unit: str = "", required: bool = True) -> str:
        """obter entrada numerica com unidade e validacao"""
        while True:
            # formatar prompt com valor padrao e unidade se disponivel
            if default:
                full_prompt = f"{prompt} [{default} {unit}]: "
            else:
                full_prompt = f"{prompt} ({unit}): "
            
            # obter entrada do usuario (nao remover espacos ainda)
            value = input(full_prompt)
            
            # se for apenas espacos ou vazio e houver padrao, usar padrao
            if not value.strip() and default:
                return default
            
            # remover espacos para validacao
            value = value.strip()
            
            # validar entrada
            if value:
                try:
                    # tentar converter para float para validar se e numero
                    float(value)
                    return value  # retornar valor se valido
                except ValueError:
                    print("  aviso: digite um numero valido!")  # avisar se nao for numero
                    continue
            elif default and not required:
                return default  # retornar padrao se nao obrigatorio
            elif not required:
                return ""  # retornar vazio se nao obrigatorio
            else:
                print("  aviso: campo obrigatorio!")  # avisar se obrigatorio
    
    def get_choice(self, prompt: str, options: List[str], default: int = 0) -> str:
        """obter escolha do usuario de uma lista de opcoes"""
        print(f"\n{prompt}")
        # mostrar todas as opcoes numeradas
        for i, option in enumerate(options):
            print(f"  {i + 1}. {option}")
        
        while True:
            try:
                # obter escolha do usuario (nao remover espacos ainda)
                choice = input(f"\nescolha (1-{len(options)}) [{default + 1}]: ")
                
                # se for apenas espacos ou vazio, usar padrao
                if not choice.strip():
                    return options[default]
                
                # remover espacos para validacao
                choice = choice.strip()
                
                # converter para indice (comeca em 0)
                choice_idx = int(choice) - 1
                # validar se indice esta dentro do range
                if 0 <= choice_idx < len(options):
                    return options[choice_idx]
                else:
                    print(f"  aviso: escolha entre 1 e {len(options)}!")  # avisar se fora do range
            except ValueError:
                print("  aviso: digite um numero valido!")  # avisar se nao for numero
    
    def get_boolean(self, prompt: str, default: bool = True) -> bool:
        """obter entrada booleana (sim/nao) do usuario"""
        default_str = "sim" if default else "nao"
        while True:
            # obter entrada (nao remover espacos ainda)
            value = input(f"{prompt} (s/n) [{default_str}]: ")
            
            # se for apenas espacos ou vazio, usar padrao
            if not value.strip():
                return default
            
            # remover espacos e converter para minusculo
            value = value.strip().lower()
            
            # validar entrada
            if value in ['s', 'sim', 'y', 'yes']:
                return True  # retornar true para sim
            elif value in ['n', 'nao', 'no']:
                return False  # retornar false para nao
            else:
                print("  aviso: digite 's' para sim ou 'n' para nao!")  # avisar se entrada invalida
    
    def get_list_input(self, prompt: str, separator: str = ",") -> List[str]:
        """obter entrada de lista separada por delimitador"""
        value = input(f"{prompt} (separado por '{separator}'): ").strip()
        if value:
            # dividir string pelo separador e remover espacos de cada item
            return [item.strip() for item in value.split(separator)]
        return []  # retornar lista vazia se nao digitou nada
    
    def interactive_mode(self):
        """modo questionario interativo - usuario responde perguntas passo a passo"""
        self.clear_screen()
        self.print_header("wizard interativo - parametrizacao de leito")
        
        print("vamos criar seu leito empacotado passo a passo...")
        print("pressione enter ou espaco para usar valores padrao quando disponivel.")
        print()
        
        # secao bed - parametros geometricos do leito
        self.print_section("geometria do leito")
        self.params['bed'] = {
            'diameter': self.get_number_input("diametro do leito", "0.05", "m"),
            'height': self.get_number_input("altura do leito", "0.1", "m"),
            'wall_thickness': self.get_number_input("espessura da parede", "0.002", "m"),
            'clearance': self.get_number_input("folga superior", "0.01", "m"),
            'material': self.get_input("material da parede", "steel"),
            'roughness': self.get_number_input("rugosidade", "0.0", "m", False)
        }
        
        # secao lids - parametros das tampas do leito
        self.print_section("tampas")
        lid_types = ["flat", "hemispherical", "none"]  # tipos de tampa disponiveis
        self.params['lids'] = {
            'top_type': self.get_choice("tipo da tampa superior", lid_types),
            'bottom_type': self.get_choice("tipo da tampa inferior", lid_types),
            'top_thickness': self.get_number_input("espessura tampa superior", "0.003", "m"),
            'bottom_thickness': self.get_number_input("espessura tampa inferior", "0.003", "m"),
            'seal_clearance': self.get_number_input("folga do selo", "0.001", "m", False)
        }
        
        # secao particles - parametros das particulas do leito
        self.print_section("particulas")
        particle_kinds = ["sphere", "cube", "cylinder"]  # formas de particulas disponiveis
        self.params['particles'] = {
            'kind': self.get_choice("tipo de particula", particle_kinds),
            'diameter': self.get_number_input("diametro das particulas", "0.005", "m"),
            'count': int(self.get_number_input("numero de particulas", "100", "", True)),
            'target_porosity': self.get_number_input("porosidade alvo", "0.4", "", False),
            'density': self.get_number_input("densidade do material", "2500.0", "kg/m3"),
            'mass': self.get_number_input("massa das particulas", "0.0", "g", False),
            'restitution': self.get_number_input("coeficiente de restituicao", "0.3", "", False),
            'friction': self.get_number_input("coeficiente de atrito", "0.5", "", False),
            'rolling_friction': self.get_number_input("atrito de rolamento", "0.1", "", False),
            'linear_damping': self.get_number_input("amortecimento linear", "0.1", "", False),
            'angular_damping': self.get_number_input("amortecimento angular", "0.1", "", False),
            'seed': int(self.get_number_input("seed para reproducibilidade", "42", "", False))
        }
        
        # secao packing - parametros do empacotamento fisico
        self.print_section("empacotamento")
        packing_methods = ["rigid_body"]  # metodos de empacotamento disponiveis
        self.params['packing'] = {
            'method': self.get_choice("metodo de empacotamento", packing_methods),
            'gravity': self.get_number_input("gravidade", "-9.81", "m/s2"),
            'substeps': int(self.get_number_input("sub-passos de simulacao", "10", "", False)),
            'iterations': int(self.get_number_input("iteracoes", "10", "", False)),
            'damping': self.get_number_input("amortecimento", "0.1", "", False),
            'rest_velocity': self.get_number_input("velocidade de repouso", "0.01", "m/s", False),
            'max_time': self.get_number_input("tempo maximo", "5.0", "s", False),
            'collision_margin': self.get_number_input("margem de colisao", "0.001", "m", False)
        }
        
        # secao export - parametros de exportacao da geometria
        self.print_section("exportacao")
        wall_modes = ["surface", "solid"]  # modos de parede disponiveis
        fluid_modes = ["none", "cavity"]  # modos de fluido disponiveis
        self.params['export'] = {
            'formats': self.get_list_input("formatos de exportacao", ",") or ["stl_binary", "obj"],
            'units': self.get_input("unidades de saida", "m", False),
            'scale': self.get_number_input("escala", "1.0", "", False),
            'wall_mode': self.get_choice("modo da parede", wall_modes),
            'fluid_mode': self.get_choice("modo do fluido", fluid_modes),
            'manifold_check': self.get_boolean("verificar manifold", True),
            'merge_distance': self.get_number_input("distancia de fusao", "0.001", "m", False)
        }
        
        # secao cfd (opcional) - parametros de simulacao de fluidos
        self.print_section("parametros cfd (opcional)")
        if self.get_boolean("incluir parametros cfd?", False):
            cfd_regimes = ["laminar", "turbulent_rans"]  # regimes de escoamento disponiveis
            self.params['cfd'] = {
                'regime': self.get_choice("regime cfd", cfd_regimes),
                'inlet_velocity': self.get_number_input("velocidade de entrada", "0.1", "m/s", False),
                'fluid_density': self.get_number_input("densidade do fluido", "1.225", "kg/m3", False),
                'fluid_viscosity': self.get_number_input("viscosidade do fluido", "1.8e-5", "pa.s", False),
                'max_iterations': int(self.get_number_input("iteracoes maximas", "1000", "", False)),
                'convergence_criteria': self.get_number_input("criterio de convergencia", "1e-6", "", False),
                'write_fields': self.get_boolean("escrever campos", False)
            }
        
        # obter nome do arquivo de saida
        self.output_file = self.get_input("nome do arquivo de saida", "meu_leito.bed")
        
        # confirmar parametros e salvar arquivo
        self.confirm_and_save()
    
    def template_mode(self):
        """modo edicao de template - usuario edita um arquivo template padrao"""
        self.clear_screen()
        self.print_header("editor de template - parametrizacao de leito")
        
        # criar template padrao com valores exemplo
        template = self.create_default_template()
        
        # obter nome do arquivo de saida
        self.output_file = self.get_input("nome do arquivo de saida", "meu_leito.bed")
        
        # criar arquivo temporario para edicao
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bed', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(template)  # escrever template no arquivo temporario
            temp_file_path = temp_file.name  # obter caminho do arquivo temporario
        
        print(f"\ntemplate criado em: {temp_file_path}")
        print("\neditores disponiveis:")
        print("1. notepad (windows)")
        print("2. nano (linux/mac)")
        print("3. vim (linux/mac)")
        print("4. continuar sem editar")
        
        # obter escolha do editor
        editor_choice = self.get_choice("escolha um editor", 
                                      ["notepad", "nano", "vim", "continuar sem editar"], 3)
        
        # abrir editor se escolhido
        if editor_choice != "continuar sem editar":
            try:
                # executar editor com arquivo temporario
                if editor_choice == "notepad":
                    subprocess.run([editor_choice, temp_file_path], check=True)
                else:
                    subprocess.run([editor_choice, temp_file_path], check=True)
            except subprocess.CalledProcessError:
                print(f"  aviso: erro ao abrir editor {editor_choice}")
                print("  continuando sem edicao...")
            except FileNotFoundError:
                print(f"  aviso: editor {editor_choice} nao encontrado")
                print("  continuando sem edicao...")
        
        # ler conteudo editado do arquivo temporario
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # limpar arquivo temporario
        os.unlink(temp_file_path)
        
        # salvar arquivo final com conteudo editado
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\nsucesso: arquivo salvo: {self.output_file}")
        
        # verificar sintaxe e compilar arquivo
        self.verify_and_compile()
    
    def create_default_template(self) -> str:
        """criar template padrao com valores exemplo para edicao"""
        return '''// template padrao para leito empacotado
// edite os valores conforme necessario

bed {
    diameter = 0.05 m;           // diametro do leito
    height = 0.1 m;              // altura do leito
    wall_thickness = 0.002 m;    // espessura da parede
    clearance = 0.01 m;          // folga superior
    material = "steel";          // material da parede
    roughness = 0.0 m;           // rugosidade (opcional)
}

lids {
    top_type = "flat";           // tipo da tampa superior
    bottom_type = "flat";        // tipo da tampa inferior
    top_thickness = 0.003 m;     // espessura tampa superior
    bottom_thickness = 0.003 m;  // espessura tampa inferior
    seal_clearance = 0.001 m;    // folga do selo (opcional)
}

particles {
    kind = "sphere";             // tipo de particula
    diameter = 0.005 m;          // diametro das particulas
    count = 100;                 // numero de particulas
    target_porosity = 0.4;       // porosidade alvo (opcional)
    density = 2500.0 kg/m3;      // densidade do material
    mass = 0.0 g;                // massa das particulas (opcional)
    restitution = 0.3;           // coeficiente de restituicao (opcional)
    friction = 0.5;              // coeficiente de atrito (opcional)
    rolling_friction = 0.1;      // atrito de rolamento (opcional)
    linear_damping = 0.1;        // amortecimento linear (opcional)
    angular_damping = 0.1;       // amortecimento angular (opcional)
    seed = 42;                   // seed para reproducibilidade (opcional)
}

packing {
    method = "rigid_body";       // metodo de empacotamento
    gravity = -9.81 m/s2;        // gravidade
    substeps = 10;               // sub-passos de simulacao (opcional)
    iterations = 10;             // iteracoes (opcional)
    damping = 0.1;               // amortecimento (opcional)
    rest_velocity = 0.01 m/s;    // velocidade de repouso (opcional)
    max_time = 5.0 s;            // tempo maximo (opcional)
    collision_margin = 0.001 m;  // margem de colisao (opcional)
}

export {
    formats = ["stl_binary", "obj"];  // formatos de exportacao
    units = "m";                      // unidades de saida (opcional)
    scale = 1.0;                      // escala (opcional)
    wall_mode = "surface";            // modo da parede
    fluid_mode = "none";              // modo do fluido
    manifold_check = true;            // verificar manifold (opcional)
    merge_distance = 0.001 m;         // distancia de fusao (opcional)
}

// secao CFD (opcional - descomente se necessario)
/*
cfd {
    regime = "laminar";               // regime CFD
    inlet_velocity = 0.1 m/s;         // velocidade de entrada (opcional)
    fluid_density = 1.225 kg/m3;      // densidade do fluido (opcional)
    fluid_viscosity = 1.8e-5 Pa.s;   // viscosidade do fluido (opcional)
    max_iterations = 1000;            // iteracoes maximas (opcional)
    convergence_criteria = 1e-6;      // criterio de convergencia (opcional)
    write_fields = false;             // escrever campos (opcional)
}
*/
'''
    
    def confirm_and_save(self):
        """confirmar parametros configurados e salvar arquivo"""
        self.clear_screen()
        self.print_header("confirmacao dos parametros")
        
        print("parametros configurados:")
        print()
        
        # mostrar resumo dos parametros principais
        print(f"leito: {self.params['bed']['diameter']}m x {self.params['bed']['height']}m")
        print(f"particulas: {self.params['particles']['count']} {self.params['particles']['kind']} de {self.params['particles']['diameter']}m")
        print(f"empacotamento: {self.params['packing']['method']}")
        print(f"exportacao: {', '.join(self.params['export']['formats'])}")
        
        # mostrar parametros cfd se configurados
        if 'cfd' in self.params:
            print(f"cfd: {self.params['cfd']['regime']}")
        
        print()
        
        # confirmar se usuario quer salvar
        if self.get_boolean("salvar arquivo .bed?", True):
            self.save_bed_file()
            self.verify_and_compile()
        else:
            print("operacao cancelada.")
    
    def save_bed_file(self):
        """salvar arquivo .bed com conteudo gerado"""
        content = self.generate_bed_content()  # gerar conteudo do arquivo
        
        # escrever arquivo com codificacao utf-8
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"sucesso: arquivo salvo: {self.output_file}")
    
    def generate_bed_content(self) -> str:
        """gerar conteudo do arquivo .bed a partir dos parametros configurados"""
        lines = ["// arquivo .bed gerado pelo wizard"]
        lines.append("")
        
        # secao bed - parametros geometricos do leito
        lines.append("bed {")
        bed = self.params['bed']
        lines.append(f"    diameter = {bed['diameter']} m;")
        lines.append(f"    height = {bed['height']} m;")
        lines.append(f"    wall_thickness = {bed['wall_thickness']} m;")
        lines.append(f"    clearance = {bed['clearance']} m;")
        lines.append(f"    material = \"{bed['material']}\";")
        # adicionar rugosidade apenas se especificada
        if bed['roughness']:
            lines.append(f"    roughness = {bed['roughness']} m;")
        lines.append("}")
        lines.append("")
        
        # secao lids - parametros das tampas
        lines.append("lids {")
        lids = self.params['lids']
        lines.append(f"    top_type = \"{lids['top_type']}\";")
        lines.append(f"    bottom_type = \"{lids['bottom_type']}\";")
        lines.append(f"    top_thickness = {lids['top_thickness']} m;")
        lines.append(f"    bottom_thickness = {lids['bottom_thickness']} m;")
        # adicionar folga do selo apenas se especificada
        if lids['seal_clearance']:
            lines.append(f"    seal_clearance = {lids['seal_clearance']} m;")
        lines.append("}")
        lines.append("")
        
        # secao particles - parametros das particulas
        lines.append("particles {")
        particles = self.params['particles']
        lines.append(f"    kind = \"{particles['kind']}\";")
        lines.append(f"    diameter = {particles['diameter']} m;")
        lines.append(f"    count = {particles['count']};")
        # adicionar parametros opcionais apenas se especificados
        if particles['target_porosity']:
            lines.append(f"    target_porosity = {particles['target_porosity']};")
        lines.append(f"    density = {particles['density']} kg/m3;")
        if particles['mass']:
            lines.append(f"    mass = {particles['mass']} g;")
        if particles['restitution']:
            lines.append(f"    restitution = {particles['restitution']};")
        if particles['friction']:
            lines.append(f"    friction = {particles['friction']};")
        if particles['rolling_friction']:
            lines.append(f"    rolling_friction = {particles['rolling_friction']};")
        if particles['linear_damping']:
            lines.append(f"    linear_damping = {particles['linear_damping']};")
        if particles['angular_damping']:
            lines.append(f"    angular_damping = {particles['angular_damping']};")
        if particles['seed']:
            lines.append(f"    seed = {particles['seed']};")
        lines.append("}")
        lines.append("")
        
        # secao packing - parametros do empacotamento fisico
        lines.append("packing {")
        packing = self.params['packing']
        lines.append(f"    method = \"{packing['method']}\";")
        lines.append(f"    gravity = {packing['gravity']} m/s2;")
        # adicionar parametros opcionais apenas se especificados
        if packing['substeps']:
            lines.append(f"    substeps = {packing['substeps']};")
        if packing['iterations']:
            lines.append(f"    iterations = {packing['iterations']};")
        if packing['damping']:
            lines.append(f"    damping = {packing['damping']};")
        if packing['rest_velocity']:
            lines.append(f"    rest_velocity = {packing['rest_velocity']} m/s;")
        if packing['max_time']:
            lines.append(f"    max_time = {packing['max_time']} s;")
        if packing['collision_margin']:
            lines.append(f"    collision_margin = {packing['collision_margin']} m;")
        lines.append("}")
        lines.append("")
        
        # secao export - parametros de exportacao
        lines.append("export {")
        export = self.params['export']
        # formatar lista de formatos com aspas
        formats_str = ", ".join([f'"{fmt}"' for fmt in export['formats']])
        lines.append(f"    formats = [{formats_str}];")
        # adicionar parametros opcionais apenas se especificados
        if export['units']:
            lines.append(f"    units = \"{export['units']}\";")
        if export['scale']:
            lines.append(f"    scale = {export['scale']};")
        lines.append(f"    wall_mode = \"{export['wall_mode']}\";")
        lines.append(f"    fluid_mode = \"{export['fluid_mode']}\";")
        # converter boolean para string minuscula
        if export['manifold_check'] is not None:
            lines.append(f"    manifold_check = {str(export['manifold_check']).lower()};")
        if export['merge_distance']:
            lines.append(f"    merge_distance = {export['merge_distance']} m;")
        lines.append("}")
        lines.append("")
        
        # secao cfd (se presente)
        if 'cfd' in self.params:
            lines.append("cfd {")
            cfd = self.params['cfd']
            lines.append(f"    regime = \"{cfd['regime']}\";")
            if cfd['inlet_velocity']:
                lines.append(f"    inlet_velocity = {cfd['inlet_velocity']} m/s;")
            if cfd['fluid_density']:
                lines.append(f"    fluid_density = {cfd['fluid_density']} kg/m3;")
            if cfd['fluid_viscosity']:
                lines.append(f"    fluid_viscosity = {cfd['fluid_viscosity']} Pa.s;")
            if cfd['max_iterations']:
                lines.append(f"    max_iterations = {cfd['max_iterations']};")
            if cfd['convergence_criteria']:
                lines.append(f"    convergence_criteria = {cfd['convergence_criteria']};")
            if cfd['write_fields'] is not None:
                lines.append(f"    write_fields = {str(cfd['write_fields']).lower()};")
            lines.append("}")
        
        return "\n".join(lines)
    
    def verify_and_compile(self):
        """verificar sintaxe e compilar arquivo .bed"""
        print(f"\nverificando arquivo: {self.output_file}")
        
        # verificar se arquivo existe
        if not os.path.exists(self.output_file):
            print(f"  erro: arquivo nao encontrado: {self.output_file}")
            return False
        
        # tentar compilar com ANTLR
        try:
            result = subprocess.run([
                sys.executable, 
                "compiler/bed_compiler_antlr_standalone.py", 
                self.output_file, 
                "-o", f"{self.output_file}.json",
                "-v"
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                print("  sucesso: sintaxe valida!")
                print("  sucesso: compilacao bem-sucedida!")
                print(f"  arquivo json gerado: {self.output_file}.json")
                print(f"  resultado: {result.stdout}")
                return True
            else:
                print("  erro: erro na compilacao:")
                print(f"  {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("  aviso: compilador antlr nao encontrado!")
            print("  verifique se o arquivo bed_compiler_antlr_standalone.py existe")
            return False
        except Exception as e:
            print(f"  erro: erro inesperado: {e}")
            return False
    
    def blender_mode(self):
        """modo blender - apenas geracao de modelo 3d sem parametros cfd"""
        self.clear_screen()
        self.print_header("modo blender - geracao de modelo 3d")
        
        print("este modo gera apenas o modelo 3d no blender")
        print("parametros cfd nao serao configurados")
        print("pressione enter ou espaco para usar valores padrao quando disponivel.")
        print()
        
        # secao bed - parametros geometricos do leito
        self.print_section("geometria do leito")
        self.params['bed'] = {
            'diameter': self.get_number_input("diametro do leito", "0.05", "m"),
            'height': self.get_number_input("altura do leito", "0.1", "m"),
            'wall_thickness': self.get_number_input("espessura da parede", "0.002", "m"),
            'clearance': self.get_number_input("folga superior", "0.01", "m"),
            'material': self.get_input("material da parede", "steel"),
            'roughness': self.get_number_input("rugosidade", "0.0", "m", False)
        }
        
        # secao lids - parametros das tampas do leito
        self.print_section("tampas")
        lid_types = ["flat", "hemispherical", "none"]
        self.params['lids'] = {
            'top_type': self.get_choice("tipo da tampa superior", lid_types),
            'bottom_type': self.get_choice("tipo da tampa inferior", lid_types),
            'top_thickness': self.get_number_input("espessura tampa superior", "0.003", "m"),
            'bottom_thickness': self.get_number_input("espessura tampa inferior", "0.003", "m"),
            'seal_clearance': self.get_number_input("folga do selo", "0.001", "m", False)
        }
        
        # secao particles - parametros das particulas do leito
        self.print_section("particulas")
        particle_kinds = ["sphere", "cube", "cylinder"]
        self.params['particles'] = {
            'kind': self.get_choice("tipo de particula", particle_kinds),
            'diameter': self.get_number_input("diametro das particulas", "0.005", "m"),
            'count': int(self.get_number_input("numero de particulas", "100", "", True)),
            'target_porosity': self.get_number_input("porosidade alvo", "0.4", "", False),
            'density': self.get_number_input("densidade do material", "2500.0", "kg/m3"),
            'mass': self.get_number_input("massa das particulas", "0.0", "g", False),
            'restitution': self.get_number_input("coeficiente de restituicao", "0.3", "", False),
            'friction': self.get_number_input("coeficiente de atrito", "0.5", "", False),
            'rolling_friction': self.get_number_input("atrito de rolamento", "0.1", "", False),
            'linear_damping': self.get_number_input("amortecimento linear", "0.1", "", False),
            'angular_damping': self.get_number_input("amortecimento angular", "0.1", "", False),
            'seed': int(self.get_number_input("seed para reproducibilidade", "42", "", False))
        }
        
        # secao packing - parametros do empacotamento fisico
        self.print_section("empacotamento")
        packing_methods = ["rigid_body"]
        self.params['packing'] = {
            'method': self.get_choice("metodo de empacotamento", packing_methods),
            'gravity': self.get_number_input("gravidade", "-9.81", "m/s2"),
            'substeps': int(self.get_number_input("sub-passos de simulacao", "10", "", False)),
            'iterations': int(self.get_number_input("iteracoes", "10", "", False)),
            'damping': self.get_number_input("amortecimento", "0.1", "", False),
            'rest_velocity': self.get_number_input("velocidade de repouso", "0.01", "m/s", False),
            'max_time': self.get_number_input("tempo maximo", "5.0", "s", False),
            'collision_margin': self.get_number_input("margem de colisao", "0.001", "m", False)
        }
        
        # secao export - parametros de exportacao simplificados
        self.print_section("exportacao")
        self.params['export'] = {
            'formats': ["stl_binary", "blend"],  # formatos para blender
            'units': "m",
            'scale': 1.0,
            'wall_mode': "surface",
            'fluid_mode': "none",
            'manifold_check': True,
            'merge_distance': 0.001
        }
        
        # nao incluir secao cfd
        print("\nparametros cfd: nao configurados (modo blender)")
        
        # obter nome do arquivo de saida
        self.output_file = self.get_input("nome do arquivo de saida", "leito_blender.bed")
        
        # confirmar e processar
        self.confirm_and_generate_blender()
    
    def confirm_and_generate_blender(self):
        """confirmar parametros e executar geracao no blender"""
        self.clear_screen()
        self.print_header("confirmacao e geracao 3d")
        
        print("parametros configurados:")
        print()
        
        # mostrar resumo dos parametros principais
        print(f"leito: {self.params['bed']['diameter']}m x {self.params['bed']['height']}m")
        print(f"particulas: {self.params['particles']['count']} {self.params['particles']['kind']} de {self.params['particles']['diameter']}m")
        print(f"empacotamento: {self.params['packing']['method']}")
        print(f"exportacao: blend, stl")
        print()
        
        # confirmar se usuario quer continuar
        if not self.get_boolean("continuar com geracao no blender?", True):
            print("operacao cancelada.")
            return
        
        # salvar arquivo .bed
        self.save_bed_file()
        
        # compilar arquivo
        print("\ncompilando arquivo...")
        if not self.verify_and_compile():
            print("erro: nao foi possivel compilar o arquivo")
            return
        
        # executar blender
        print("\nexecutando blender...")
        self.execute_blender()
    
    def execute_blender(self):
        """executar script do blender para gerar modelo 3d"""
        try:
            # definir caminhos
            project_root = Path(__file__).parent.parent
            dsl_dir = Path(__file__).parent
            blender_script = project_root / "scripts" / "blender_scripts" / "leito_extracao.py"
            output_dir = project_root / "output" / "models"
            
            # obter caminho completo do arquivo json
            # o compilador gera arquivo.bed.json, nao arquivo.json
            json_file = Path(self.output_file + '.json')
            if not json_file.is_absolute():
                json_file = dsl_dir / json_file
            
            # criar diretorio de saida se nao existir
            output_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"script blender: {blender_script}")
            print(f"arquivo json: {json_file}")
            print(f"diretorio saida: {output_dir}")
            
            # verificar se arquivos existem
            if not blender_script.exists():
                print(f"erro: script blender nao encontrado: {blender_script}")
                return False
            
            if not json_file.exists():
                print(f"erro: arquivo json nao encontrado: {json_file}")
                return False
            
            # tentar encontrar blender
            blender_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender\blender.exe",
                "blender"
            ]
            
            blender_exe = None
            for path in blender_paths:
                if Path(path).exists() if path.startswith("C:") else True:
                    blender_exe = path
                    break
            
            if not blender_exe:
                print("erro: blender nao encontrado")
                print("instale o blender ou adicione ao path do sistema")
                return False
            
            print(f"blender encontrado: {blender_exe}")
            print("\niniciando geracao do modelo 3d...")
            print("isso pode levar alguns minutos...")
            
            # nome do arquivo de saida
            output_blend = output_dir / f"{Path(self.output_file).stem}.blend"
            
            # executar blender em modo headless
            result = subprocess.run([
                blender_exe,
                "--background",
                "--python", str(blender_script),
                "--",
                "--params", str(json_file),
                "--output", str(output_blend)
            ], capture_output=True, text=True, timeout=300)
            
            # mostrar saida do blender para debug
            if result.stdout:
                print("\nsaida do blender:")
                print(result.stdout)
            
            if result.returncode == 0:
                # verificar se arquivo foi realmente criado
                if output_blend.exists():
                    print("\nsucesso: modelo 3d gerado!")
                    print(f"arquivo salvo: {output_blend}")
                    print(f"tamanho: {output_blend.stat().st_size / 1024:.2f} kb")
                    print(f"diretorio: {output_dir}")
                    return True
                else:
                    print("\naviso: blender executou mas arquivo nao foi criado")
                    print(f"arquivo esperado: {output_blend}")
                    print("verifique a saida do blender acima")
                    return False
            else:
                print("\nerro: falha na geracao do modelo")
                print(f"codigo de erro: {result.returncode}")
                if result.stderr:
                    print(f"detalhes do erro:")
                    print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("erro: timeout na execucao do blender (limite: 5 minutos)")
            return False
        except FileNotFoundError:
            print("erro: blender nao encontrado no sistema")
            print("verifique a instalacao do blender")
            return False
        except Exception as e:
            print(f"erro: erro inesperado: {e}")
            return False
    
    def run(self):
        """executar wizard"""
        self.clear_screen()
        self.print_header("wizard de parametrizacao de leitos empacotados")
        
        print("bem-vindo ao wizard para criacao de arquivos .bed!")
        print("este wizard ajuda voce a criar arquivos de parametrizacao")
        print("para leitos empacotados que serao processados pelo compilador antlr.")
        print()
        
        print("escolha o modo de criacao:")
        print("1. questionario interativo - responda perguntas passo a passo")
        print("2. editor de template - edite um arquivo padrao")
        print("3. modo blender - apenas geracao de modelo 3d (sem cfd)")
        print("4. sair")
        
        while True:
            choice = input("\nescolha (1-4): ").strip()
            
            if choice == "1":
                self.interactive_mode()
                break
            elif choice == "2":
                self.template_mode()
                break
            elif choice == "3":
                self.blender_mode()
                break
            elif choice == "4":
                print("ate logo!")
                sys.exit(0)
            else:
                print("  aviso: escolha entre 1, 2, 3 ou 4!")

def main():
    """funcao principal"""
    wizard = BedWizard()
    wizard.run()

if __name__ == "__main__":
    main()
