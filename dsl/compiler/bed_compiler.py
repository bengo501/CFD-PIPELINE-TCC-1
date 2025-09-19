#!/usr/bin/env python3
#compilador para linguagem .bed
#converte arquivos .bed em params.json para uso com blender

import json 
import hashlib # para calcular hash
import argparse # para processar argumentos da linha de comando
from pathlib import Path # para manipular caminhos de arquivos
from typing import Dict, Any, Optional, List # para definir tipos de dados
from dataclasses import dataclass, asdict # para definir classes e converter para dict
import re # para manipular strings

# estrutura de dados para parametros do leito
@dataclass
class BedGeometry:
    # geometria do leito cilindrico
    diameter: float         # metros
    height: float           # metros  
    wall_thickness: float   # metros
    clearance: float        # metros
    material: str = "steel"
    roughness: float = 0.0  # metros

# estrutura de dados para parametros das tampas
@dataclass
class Lids:
    #configuracao das tampas
    top_type: str = "flat"           # flat, hemispherical, none
    bottom_type: str = "flat"
    top_thickness: float = 0.003     # metros
    bottom_thickness: float = 0.003  # metros
    seal_clearance: float = 0.0      # metros

# estrutura de dados para parametros das particulas
@dataclass
class Particles:
    #propriedades das particulas
    kind: str = "sphere"             # sphere, cube, cylinder
    diameter: float = 0.005          # metros
    count: Optional[int] = None      # numero de particulas
    target_porosity: Optional[float] = None  # 0.0 a 1.0
    density: float = 2500.0          # kg/m3
    mass: Optional[float] = None     # kg (calculado se None)
    restitution: float = 0.3         # 0.0 a 1.0
    friction: float = 0.5            # 0.0 a 1.0
    rolling_friction: float = 0.1    # 0.0 a 1.0
    linear_damping: float = 0.1      # 0.0 a 1.0
    angular_damping: float = 0.1     # 0.0 a 1.0
    seed: int = 42                   # seed para reproducibilidade

# estrutura de dados para parametros do empacotamento fisico
@dataclass
class Packing:
    #configuracao do empacotamento fisico
    method: str = "rigid_body"
    gravity: float = -9.81           # m/s2
    substeps: int = 10
    iterations: int = 10
    damping: float = 0.1
    rest_velocity: float = 0.01      # m/s
    max_time: float = 10.0           # segundos
    collision_margin: float = 0.001  # metros

# estrutura de dados para parametros de exportacao
@dataclass
class Export:
    #configuracao de exportacao
    formats: List[str] = None        # ["stl_binary", "obj"]
    units: str = "m"
    scale: float = 1.0
    wall_mode: str = "surface"       # surface, solid
    fluid_mode: str = "none"         # none, cavity
    manifold_check: bool = True
    merge_distance: float = 0.0001   # metros

    def __post_init__(self):
        if self.formats is None:
            self.formats = ["stl_binary"]

# estrutura de dados para parametros opcionais para CFD
@dataclass
class CFD:
    #parametros opcionais para CFD
    regime: str = "laminar"          # laminar, turbulent_rans
    inlet_velocity: float = 0.1      # m/s
    fluid_density: float = 1.0       # kg/m3 (agua)
    fluid_viscosity: float = 1e-6    # Pa.s
    max_iterations: int = 1000
    convergence_criteria: float = 1e-6
    write_fields: bool = True

# estrutura de dados para parametros completos do leito
@dataclass
class BedParameters:
    #estrutura completa dos parametros do leito
    bed: BedGeometry
    lids: Lids
    particles: Particles
    packing: Packing
    export: Export
    cfd: Optional[CFD] = None
    
    # metadados: versao e hash
    # metadados
    version: str = "1.0"
    hash: str = ""
    
    # metodos: calcular hash e validar parametros
    def calculate_hash(self) -> str:
        #calcula hash dos parametros para versionamento
        # converter para dict e remover hash atual
        data = asdict(self)
        data.pop('hash', None)
        
        # criar string json ordenada
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        # calcular hash sha256
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]

# classe compilador para linguagem .bed
class BedCompiler:
    #compilador para linguagem .bed
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    # metodo para fazer parsing de um arquivo .bed
    def parse_bed_file(self, filepath: str) -> Optional[BedParameters]:

        #faz parsing de um arquivo .bed e retorna parametros
        
        #args:
            #filepath: caminho para arquivo .bed
            
        #returns:
            #BedParameters ou None se houver erro

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_bed_content(content)
            
        except FileNotFoundError:
            self.errors.append(f"arquivo nao encontrado: {filepath}")
            return None
        except Exception as e:
            self.errors.append(f"erro ao ler arquivo: {e}")
            return None
    
    def parse_bed_content(self, content: str) -> Optional[BedParameters]:
        #faz parsing do conteudo de um arquivo .bed
        #args:
            #content: conteudo do arquivo .bed   
        #returns:
            #BedParameters ou None se houver erro

        # remover comentarios
        content = self._remove_comments(content)
        
        # inicializar com valores padrao
        bed_params = BedParameters(
            bed=BedGeometry(diameter=0.05, height=0.1, wall_thickness=0.002, clearance=0.01),
            lids=Lids(),
            particles=Particles(),
            packing=Packing(),
            export=Export()
        )
        
        # fazer parsing das secoes
        sections = self._extract_sections(content)
        
        for section_name, section_content in sections.items():
            if section_name == 'bed':
                self._parse_bed_section(section_content, bed_params.bed)
            elif section_name == 'lids':
                self._parse_lids_section(section_content, bed_params.lids)
            elif section_name == 'particles':
                self._parse_particles_section(section_content, bed_params.particles)
            elif section_name == 'packing':
                self._parse_packing_section(section_content, bed_params.packing)
            elif section_name == 'export':
                self._parse_export_section(section_content, bed_params.export)
            elif section_name == 'cfd':
                bed_params.cfd = CFD()
                self._parse_cfd_section(section_content, bed_params.cfd)
        
        # validar parametros
        if not self._validate_parameters(bed_params):
            return None
        
        # calcular hash
        bed_params.hash = bed_params.calculate_hash()
        
        return bed_params
    
    def _remove_comments(self, content: str) -> str:
        #remove comentarios do conteudo
        # remover comentarios de linha //
        content = re.sub(r'//.*', '', content)
        # remover comentarios de bloco /* */
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        #extrai secoes do arquivo .bed
        sections = {}
        
        # regex para encontrar secoes: nome { conteudo }
        pattern = r'(\w+)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for section_name, section_content in matches:
            sections[section_name.strip()] = section_content.strip()
        
        return sections
    
    def _parse_property(self, line: str) -> tuple:
        #faz parsing de uma propriedade: nome = valor;
        # regex para propriedade
        match = re.match(r'(\w+)\s*=\s*(.+?);', line.strip())
        if not match:
            return None, None
        
        prop_name = match.group(1).strip()
        prop_value = match.group(2).strip()
        
        # remover aspas de strings
        if prop_value.startswith('"') and prop_value.endswith('"'):
            prop_value = prop_value[1:-1]
        
        return prop_name, prop_value
    
    def _parse_number_with_unit(self, value_str: str) -> float:
        #converte numero com unidade para metros/SI
        # regex para numero + unidade (incluindo unidades compostas e numeros negativos)
        match = re.match(r'([-+]?[\d.]+)\s*([a-zA-Z0-9/.]+)?', value_str.strip())
        if not match:
            raise ValueError(f"formato invalido: {value_str}")
        
        number = float(match.group(1))
        unit = match.group(2) or ""
        
        # conversoes para SI
        conversions = {
            # comprimento
            'm': 1.0,
            'cm': 0.01,
            'mm': 0.001,
            # massa
            'kg': 1.0,
            'g': 0.001,
            # tempo
            's': 1.0,
            # pressao
            'Pa': 1.0,
            'N': 1.0,
            # velocidade
            'm/s': 1.0,
            # densidade
            'kg/m3': 1.0,
            # viscosidade
            'Pa.s': 1.0,
            'Pas': 1.0,
            # aceleracao
            'm/s2': 1.0,
            'm/s²': 1.0,
            # sem unidade
            '': 1.0
        }
        
        return number * conversions.get(unit, 1.0)
    
    # metodo para fazer parsing da secao bed
    def _parse_bed_section(self, content: str, bed: BedGeometry):
        #faz parsing da secao bed
        for line in content.split('\n'):
            prop_name, prop_value = self._parse_property(line)
            if not prop_name:
                continue
                
            if prop_name == 'diameter':
                bed.diameter = self._parse_number_with_unit(prop_value)
            elif prop_name == 'height':
                bed.height = self._parse_number_with_unit(prop_value)
            elif prop_name == 'wall_thickness':
                bed.wall_thickness = self._parse_number_with_unit(prop_value)
            elif prop_name == 'clearance':
                bed.clearance = self._parse_number_with_unit(prop_value)
            elif prop_name == 'material':
                bed.material = prop_value
            elif prop_name == 'roughness':
                bed.roughness = self._parse_number_with_unit(prop_value)
    
    # metodo para fazer parsing da secao lids
    def _parse_lids_section(self, content: str, lids: Lids):
        #faz parsing da secao lids
        for line in content.split('\n'):
            prop_name, prop_value = self._parse_property(line)
            if not prop_name:
                continue
                
            if prop_name == 'top_type':
                lids.top_type = prop_value
            elif prop_name == 'bottom_type':
                lids.bottom_type = prop_value
            elif prop_name == 'top_thickness':
                lids.top_thickness = self._parse_number_with_unit(prop_value)
            elif prop_name == 'bottom_thickness':
                lids.bottom_thickness = self._parse_number_with_unit(prop_value)
            elif prop_name == 'seal_clearance':
                lids.seal_clearance = self._parse_number_with_unit(prop_value)
    
    # metodo para fazer parsing da secao particles
    def _parse_particles_section(self, content: str, particles: Particles):
        #faz parsing da secao particles
        for line in content.split('\n'):
            prop_name, prop_value = self._parse_property(line)
            if not prop_name:
                continue
                
            if prop_name == 'kind':
                particles.kind = prop_value
            elif prop_name == 'diameter':
                particles.diameter = self._parse_number_with_unit(prop_value)
            elif prop_name == 'count':
                particles.count = int(prop_value)
            elif prop_name == 'target_porosity':
                particles.target_porosity = float(prop_value)
            elif prop_name == 'density':
                particles.density = self._parse_number_with_unit(prop_value)
            elif prop_name == 'mass':
                particles.mass = self._parse_number_with_unit(prop_value)
            elif prop_name == 'restitution':
                particles.restitution = float(prop_value)
            elif prop_name == 'friction':
                particles.friction = float(prop_value)
            elif prop_name == 'rolling_friction':
                particles.rolling_friction = float(prop_value)
            elif prop_name == 'linear_damping':
                particles.linear_damping = float(prop_value)
            elif prop_name == 'angular_damping':
                particles.angular_damping = float(prop_value)
            elif prop_name == 'seed':
                particles.seed = int(prop_value)
    
    # metodo para fazer parsing da secao packing
    def _parse_packing_section(self, content: str, packing: Packing):
        #faz parsing da secao packing
        for line in content.split('\n'):
            prop_name, prop_value = self._parse_property(line)
            if not prop_name:
                continue
                
            if prop_name == 'method':
                packing.method = prop_value
            elif prop_name == 'gravity':
                packing.gravity = self._parse_number_with_unit(prop_value)
            elif prop_name == 'substeps':
                packing.substeps = int(prop_value)
            elif prop_name == 'iterations':
                packing.iterations = int(prop_value)
            elif prop_name == 'damping':
                packing.damping = float(prop_value)
            elif prop_name == 'rest_velocity':
                packing.rest_velocity = self._parse_number_with_unit(prop_value)
            elif prop_name == 'max_time':
                packing.max_time = self._parse_number_with_unit(prop_value)
            elif prop_name == 'collision_margin':
                packing.collision_margin = self._parse_number_with_unit(prop_value)
    
    # metodo para fazer parsing da secao export
    def _parse_export_section(self, content: str, export: Export):
        #faz parsing da secao export
        for line in content.split('\n'):
            prop_name, prop_value = self._parse_property(line)
            if not prop_name:
                continue
                
            if prop_name == 'formats':
                # parsing de lista: ["stl_binary", "obj"]
                formats_str = prop_value.strip('[]')
                export.formats = [f.strip(' "') for f in formats_str.split(',')]
            elif prop_name == 'units':
                export.units = prop_value
            elif prop_name == 'scale':
                export.scale = float(prop_value)
            elif prop_name == 'wall_mode':
                export.wall_mode = prop_value
            elif prop_name == 'fluid_mode':
                export.fluid_mode = prop_value
            elif prop_name == 'manifold_check':
                export.manifold_check = prop_value.lower() == 'true'
            elif prop_name == 'merge_distance':
                export.merge_distance = self._parse_number_with_unit(prop_value)
    
    # metodo para fazer parsing da secao cfd
    def _parse_cfd_section(self, content: str, cfd: CFD):
        #faz parsing da secao cfd
        for line in content.split('\n'):
            prop_name, prop_value = self._parse_property(line)
            if not prop_name:
                continue
                
            if prop_name == 'regime':
                cfd.regime = prop_value
            elif prop_name == 'inlet_velocity':
                cfd.inlet_velocity = self._parse_number_with_unit(prop_value)
            elif prop_name == 'fluid_density':
                cfd.fluid_density = self._parse_number_with_unit(prop_value)
            elif prop_name == 'fluid_viscosity':
                cfd.fluid_viscosity = self._parse_number_with_unit(prop_value)
            elif prop_name == 'max_iterations':
                cfd.max_iterations = int(prop_value)
            elif prop_name == 'convergence_criteria':
                cfd.convergence_criteria = float(prop_value)
            elif prop_name == 'write_fields':
                cfd.write_fields = prop_value.lower() == 'true'
    
    # metodo para validar os parametros do leito
    def _validate_parameters(self, params: BedParameters) -> bool:
        #valida os parametros do leito
        valid = True
        
        # validacoes basicas
        if params.bed.diameter <= 0:
            self.errors.append("diametro do leito deve ser positivo")
            valid = False
            
        if params.bed.height <= 0:
            self.errors.append("altura do leito deve ser positiva")
            valid = False
            
        if params.bed.wall_thickness >= params.bed.diameter / 2:
            self.errors.append("espessura da parede muito grande")
            valid = False
            
        if params.particles.diameter >= params.bed.diameter / 2:
            self.errors.append("particulas muito grandes para o leito")
            valid = False
            
        # validar count XOR target_porosity
        if params.particles.count is not None and params.particles.target_porosity is not None:
            self.errors.append("especifique count OU target_porosity, nao ambos")
            valid = False
            
        if params.particles.count is None and params.particles.target_porosity is None:
            self.errors.append("especifique count OU target_porosity")
            valid = False
        
        return valid
    
    # metodo para compilar parametros para arquivo params.json
    def compile_to_json(self, params: BedParameters, output_path: str) -> bool:
        #compila parametros para arquivo params.json
        
        #args:
        #    params: parametros do leito
        #    output_path: caminho do arquivo de saida
            
        #returns:
        #    True se sucesso, False se erro
     
        try:
            # converter para dict
            data = asdict(params)
            
            # escrever json formatado
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.errors.append(f"erro ao escrever json: {e}")
            return False

# metodo principal do compilador
def main():
    #funcao principal do compilador
    parser = argparse.ArgumentParser(description='compilador para linguagem .bed')
    parser.add_argument('input', help='arquivo .bed de entrada')
    parser.add_argument('-o', '--output', default='params.json', help='arquivo params.json de saida')
    parser.add_argument('-v', '--verbose', action='store_true', help='saida detalhada')
    
    args = parser.parse_args()
    
    # compilar
    compiler = BedCompiler()
    params = compiler.parse_bed_file(args.input)
    
    if not params:
        print("erro na compilacao:")
        for error in compiler.errors:
            print(f"  - {error}")
        return 1
    
    # salvar params.json
    if compiler.compile_to_json(params, args.output):
        print(f"compilacao bem-sucedida: {args.output}")
        if args.verbose:
            print(f"hash: {params.hash}")
            print(f"particulas: {params.particles.count or 'calculado pela porosidade'}")
    else:
        print("erro ao salvar arquivo:")
        for error in compiler.errors:
            print(f"  - {error}")
        return 1
    
    # mostrar warnings
    if compiler.warnings:
        print("avisos:")
        for warning in compiler.warnings:
            print(f"  - {warning}")
    
    return 0

if __name__ == '__main__':
    exit(main())
#===================================================================================
