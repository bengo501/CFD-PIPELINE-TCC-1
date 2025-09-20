#!/usr/bin/env python3
"""
wizard interativo para criar arquivos .bed
permite ao usuario parametrizar leitos empacotados de duas formas:
1. questionario interativo
2. edicao de template padrao
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional

class BedWizard:
    """wizard para criacao de arquivos .bed"""
    
    def __init__(self):
        self.params = {}
        self.output_file = None
        
    def clear_screen(self):
        """limpar tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """imprimir cabecalho"""
        print("=" * 60)
        print(f"  {title}")
        print("=" * 60)
        print()
    
    def print_section(self, title: str):
        """imprimir secao"""
        print(f"\n--- {title} ---")
    
    def get_input(self, prompt: str, default: str = "", required: bool = True) -> str:
        """obter entrada do usuario"""
        while True:
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "
            
            value = input(full_prompt).strip()
            
            if value:
                return value
            elif default and not required:
                return default
            elif not required:
                return ""
            else:
                print("  ⚠️  Campo obrigatorio!")
    
    def get_number_input(self, prompt: str, default: str = "", unit: str = "", required: bool = True) -> str:
        """obter entrada numerica com unidade"""
        while True:
            if default:
                full_prompt = f"{prompt} [{default} {unit}]: "
            else:
                full_prompt = f"{prompt} ({unit}): "
            
            value = input(full_prompt).strip()
            
            if value:
                try:
                    float(value)
                    return value
                except ValueError:
                    print("  ⚠️  Digite um numero valido!")
                    continue
            elif default and not required:
                return default
            elif not required:
                return ""
            else:
                print("  ⚠️  Campo obrigatorio!")
    
    def get_choice(self, prompt: str, options: List[str], default: int = 0) -> str:
        """obter escolha do usuario"""
        print(f"\n{prompt}")
        for i, option in enumerate(options):
            print(f"  {i + 1}. {option}")
        
        while True:
            try:
                choice = input(f"\nEscolha (1-{len(options)}) [{default + 1}]: ").strip()
                
                if not choice:
                    return options[default]
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    return options[choice_idx]
                else:
                    print(f"  ⚠️  Escolha entre 1 e {len(options)}!")
            except ValueError:
                print("  ⚠️  Digite um numero valido!")
    
    def get_boolean(self, prompt: str, default: bool = True) -> bool:
        """obter entrada booleana"""
        default_str = "sim" if default else "nao"
        while True:
            value = input(f"{prompt} (s/n) [{default_str}]: ").strip().lower()
            
            if value in ['s', 'sim', 'y', 'yes']:
                return True
            elif value in ['n', 'nao', 'no']:
                return False
            elif not value:
                return default
            else:
                print("  ⚠️  Digite 's' para sim ou 'n' para nao!")
    
    def get_list_input(self, prompt: str, separator: str = ",") -> List[str]:
        """obter entrada de lista"""
        value = input(f"{prompt} (separado por '{separator}'): ").strip()
        if value:
            return [item.strip() for item in value.split(separator)]
        return []
    
    def interactive_mode(self):
        """modo questionario interativo"""
        self.clear_screen()
        self.print_header("WIZARD INTERATIVO - PARAMETRIZACAO DE LEITO")
        
        print("Vamos criar seu leito empacotado passo a passo...")
        print("Pressione ENTER para usar valores padrao quando disponivel.")
        print()
        
        # secao bed
        self.print_section("GEOMETRIA DO LEITO")
        self.params['bed'] = {
            'diameter': self.get_number_input("Diametro do leito", "0.05", "m"),
            'height': self.get_number_input("Altura do leito", "0.1", "m"),
            'wall_thickness': self.get_number_input("Espessura da parede", "0.002", "m"),
            'clearance': self.get_number_input("Folga superior", "0.01", "m"),
            'material': self.get_input("Material da parede", "steel"),
            'roughness': self.get_number_input("Rugosidade", "0.0", "m", False)
        }
        
        # secao lids
        self.print_section("TAMPAS")
        lid_types = ["flat", "hemispherical", "none"]
        self.params['lids'] = {
            'top_type': self.get_choice("Tipo da tampa superior", lid_types),
            'bottom_type': self.get_choice("Tipo da tampa inferior", lid_types),
            'top_thickness': self.get_number_input("Espessura tampa superior", "0.003", "m"),
            'bottom_thickness': self.get_number_input("Espessura tampa inferior", "0.003", "m"),
            'seal_clearance': self.get_number_input("Folga do selo", "0.001", "m", False)
        }
        
        # secao particles
        self.print_section("PARTICULAS")
        particle_kinds = ["sphere", "cube", "cylinder"]
        self.params['particles'] = {
            'kind': self.get_choice("Tipo de particula", particle_kinds),
            'diameter': self.get_number_input("Diametro das particulas", "0.005", "m"),
            'count': int(self.get_number_input("Numero de particulas", "100", "", True)),
            'target_porosity': self.get_number_input("Porosidade alvo", "0.4", "", False),
            'density': self.get_number_input("Densidade do material", "2500.0", "kg/m3"),
            'mass': self.get_number_input("Massa das particulas", "0.0", "g", False),
            'restitution': self.get_number_input("Coeficiente de restituicao", "0.3", "", False),
            'friction': self.get_number_input("Coeficiente de atrito", "0.5", "", False),
            'rolling_friction': self.get_number_input("Atrito de rolamento", "0.1", "", False),
            'linear_damping': self.get_number_input("Amortecimento linear", "0.1", "", False),
            'angular_damping': self.get_number_input("Amortecimento angular", "0.1", "", False),
            'seed': int(self.get_number_input("Seed para reproducibilidade", "42", "", False))
        }
        
        # secao packing
        self.print_section("EMPACOTAMENTO")
        packing_methods = ["rigid_body"]
        self.params['packing'] = {
            'method': self.get_choice("Metodo de empacotamento", packing_methods),
            'gravity': self.get_number_input("Gravidade", "-9.81", "m/s2"),
            'substeps': int(self.get_number_input("Sub-passos de simulacao", "10", "", False)),
            'iterations': int(self.get_number_input("Iteracoes", "10", "", False)),
            'damping': self.get_number_input("Amortecimento", "0.1", "", False),
            'rest_velocity': self.get_number_input("Velocidade de repouso", "0.01", "m/s", False),
            'max_time': self.get_number_input("Tempo maximo", "5.0", "s", False),
            'collision_margin': self.get_number_input("Margem de colisao", "0.001", "m", False)
        }
        
        # secao export
        self.print_section("EXPORTACAO")
        wall_modes = ["surface", "solid"]
        fluid_modes = ["none", "cavity"]
        self.params['export'] = {
            'formats': self.get_list_input("Formatos de exportacao", ",") or ["stl_binary", "obj"],
            'units': self.get_input("Unidades de saida", "m", False),
            'scale': self.get_number_input("Escala", "1.0", "", False),
            'wall_mode': self.get_choice("Modo da parede", wall_modes),
            'fluid_mode': self.get_choice("Modo do fluido", fluid_modes),
            'manifold_check': self.get_boolean("Verificar manifold", True),
            'merge_distance': self.get_number_input("Distancia de fusao", "0.001", "m", False)
        }
        
        # secao cfd (opcional)
        self.print_section("PARAMETROS CFD (OPCIONAL)")
        if self.get_boolean("Incluir parametros CFD?", False):
            cfd_regimes = ["laminar", "turbulent_rans"]
            self.params['cfd'] = {
                'regime': self.get_choice("Regime CFD", cfd_regimes),
                'inlet_velocity': self.get_number_input("Velocidade de entrada", "0.1", "m/s", False),
                'fluid_density': self.get_number_input("Densidade do fluido", "1.225", "kg/m3", False),
                'fluid_viscosity': self.get_number_input("Viscosidade do fluido", "1.8e-5", "Pa.s", False),
                'max_iterations': int(self.get_number_input("Iteracoes maximas", "1000", "", False)),
                'convergence_criteria': self.get_number_input("Criterio de convergencia", "1e-6", "", False),
                'write_fields': self.get_boolean("Escrever campos", False)
            }
        
        # nome do arquivo
        self.output_file = self.get_input("Nome do arquivo de saida", "meu_leito.bed")
        
        # confirmar
        self.confirm_and_save()
    
    def template_mode(self):
        """modo edicao de template"""
        self.clear_screen()
        self.print_header("EDITOR DE TEMPLATE - PARAMETRIZACAO DE LEITO")
        
        # criar template padrao
        template = self.create_default_template()
        
        # obter nome do arquivo
        self.output_file = self.get_input("Nome do arquivo de saida", "meu_leito.bed")
        
        # criar arquivo temporario para edicao
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bed', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(template)
            temp_file_path = temp_file.name
        
        print(f"\nTemplate criado em: {temp_file_path}")
        print("\nEditores disponiveis:")
        print("1. notepad (Windows)")
        print("2. nano (Linux/Mac)")
        print("3. vim (Linux/Mac)")
        print("4. Continuar sem editar")
        
        editor_choice = self.get_choice("Escolha um editor", 
                                      ["notepad", "nano", "vim", "Continuar sem editar"], 3)
        
        if editor_choice != "Continuar sem editar":
            try:
                if editor_choice == "notepad":
                    subprocess.run([editor_choice, temp_file_path], check=True)
                else:
                    subprocess.run([editor_choice, temp_file_path], check=True)
            except subprocess.CalledProcessError:
                print(f"  ⚠️  Erro ao abrir editor {editor_choice}")
                print("  Continuando sem edicao...")
            except FileNotFoundError:
                print(f"  ⚠️  Editor {editor_choice} nao encontrado")
                print("  Continuando sem edicao...")
        
        # ler conteudo editado
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # limpar arquivo temporario
        os.unlink(temp_file_path)
        
        # salvar arquivo final
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Arquivo salvo: {self.output_file}")
        
        # verificar e compilar
        self.verify_and_compile()
    
    def create_default_template(self) -> str:
        """criar template padrao"""
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
        """confirmar parametros e salvar"""
        self.clear_screen()
        self.print_header("CONFIRMACAO DOS PARAMETROS")
        
        print("Parametros configurados:")
        print()
        
        # mostrar resumo
        print(f"📏 LEITO: {self.params['bed']['diameter']}m x {self.params['bed']['height']}m")
        print(f"🔘 PARTICULAS: {self.params['particles']['count']} {self.params['particles']['kind']} de {self.params['particles']['diameter']}m")
        print(f"📦 EMPACOTAMENTO: {self.params['packing']['method']}")
        print(f"💾 EXPORTACAO: {', '.join(self.params['export']['formats'])}")
        
        if 'cfd' in self.params:
            print(f"🌊 CFD: {self.params['cfd']['regime']}")
        
        print()
        
        if self.get_boolean("Salvar arquivo .bed?", True):
            self.save_bed_file()
            self.verify_and_compile()
        else:
            print("Operacao cancelada.")
    
    def save_bed_file(self):
        """salvar arquivo .bed"""
        content = self.generate_bed_content()
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Arquivo salvo: {self.output_file}")
    
    def generate_bed_content(self) -> str:
        """gerar conteudo do arquivo .bed"""
        lines = ["// arquivo .bed gerado pelo wizard"]
        lines.append("")
        
        # secao bed
        lines.append("bed {")
        bed = self.params['bed']
        lines.append(f"    diameter = {bed['diameter']} m;")
        lines.append(f"    height = {bed['height']} m;")
        lines.append(f"    wall_thickness = {bed['wall_thickness']} m;")
        lines.append(f"    clearance = {bed['clearance']} m;")
        lines.append(f"    material = \"{bed['material']}\";")
        if bed['roughness']:
            lines.append(f"    roughness = {bed['roughness']} m;")
        lines.append("}")
        lines.append("")
        
        # secao lids
        lines.append("lids {")
        lids = self.params['lids']
        lines.append(f"    top_type = \"{lids['top_type']}\";")
        lines.append(f"    bottom_type = \"{lids['bottom_type']}\";")
        lines.append(f"    top_thickness = {lids['top_thickness']} m;")
        lines.append(f"    bottom_thickness = {lids['bottom_thickness']} m;")
        if lids['seal_clearance']:
            lines.append(f"    seal_clearance = {lids['seal_clearance']} m;")
        lines.append("}")
        lines.append("")
        
        # secao particles
        lines.append("particles {")
        particles = self.params['particles']
        lines.append(f"    kind = \"{particles['kind']}\";")
        lines.append(f"    diameter = {particles['diameter']} m;")
        lines.append(f"    count = {particles['count']};")
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
        
        # secao packing
        lines.append("packing {")
        packing = self.params['packing']
        lines.append(f"    method = \"{packing['method']}\";")
        lines.append(f"    gravity = {packing['gravity']} m/s2;")
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
        
        # secao export
        lines.append("export {")
        export = self.params['export']
        formats_str = ", ".join([f'"{fmt}"' for fmt in export['formats']])
        lines.append(f"    formats = [{formats_str}];")
        if export['units']:
            lines.append(f"    units = \"{export['units']}\";")
        if export['scale']:
            lines.append(f"    scale = {export['scale']};")
        lines.append(f"    wall_mode = \"{export['wall_mode']}\";")
        lines.append(f"    fluid_mode = \"{export['fluid_mode']}\";")
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
        print(f"\n🔍 Verificando arquivo: {self.output_file}")
        
        # verificar se arquivo existe
        if not os.path.exists(self.output_file):
            print(f"  ❌ Arquivo nao encontrado: {self.output_file}")
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
                print("  ✅ Sintaxe valida!")
                print("  ✅ Compilacao bem-sucedida!")
                print(f"  📄 Arquivo JSON gerado: {self.output_file}.json")
                print(f"  📊 {result.stdout}")
                return True
            else:
                print("  ❌ Erro na compilacao:")
                print(f"  {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("  ⚠️  Compilador ANTLR nao encontrado!")
            print("  Verifique se o arquivo bed_compiler_antlr_standalone.py existe")
            return False
        except Exception as e:
            print(f"  ❌ Erro inesperado: {e}")
            return False
    
    def run(self):
        """executar wizard"""
        self.clear_screen()
        self.print_header("WIZARD DE PARAMETRIZACAO DE LEITOS EMPACOTADOS")
        
        print("Bem-vindo ao wizard para criacao de arquivos .bed!")
        print("Este wizard ajuda voce a criar arquivos de parametrizacao")
        print("para leitos empacotados que serao processados pelo compilador ANTLR.")
        print()
        
        print("Escolha o modo de criacao:")
        print("1. Questionario interativo - responda perguntas passo a passo")
        print("2. Editor de template - edite um arquivo padrao")
        print("3. Sair")
        
        while True:
            choice = input("\nEscolha (1-3): ").strip()
            
            if choice == "1":
                self.interactive_mode()
                break
            elif choice == "2":
                self.template_mode()
                break
            elif choice == "3":
                print("Ate logo!")
                sys.exit(0)
            else:
                print("  ⚠️  Escolha entre 1, 2 ou 3!")

def main():
    """funcao principal"""
    wizard = BedWizard()
    wizard.run()

if __name__ == "__main__":
    main()
