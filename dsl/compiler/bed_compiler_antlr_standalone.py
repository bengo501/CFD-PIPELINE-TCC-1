#!/usr/bin/env python3
"""
compilador para linguagem .bed usando antlr
versao standalone que nao depende do bed_compiler.py
"""

import json
import hashlib
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

# tentar importar antlr
try:
    from antlr4 import *
    from antlr4.error.ErrorListener import ErrorListener
    
    # importar parser gerado
    sys.path.append(str(Path(__file__).parent.parent / "generated"))
    from BedLexer import BedLexer
    from BedParser import BedParser
    from BedListener import BedListener
    
    ANTLR_AVAILABLE = True
except ImportError as e:
    print(f"aviso: antlr nao disponivel: {e}")
    print("execute: java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 -o generated grammar/Bed.g4")
    ANTLR_AVAILABLE = False

# estruturas de dados para parametros do leito
@dataclass
class BedGeometry:
    diameter: float = 0.05
    height: float = 0.1
    wall_thickness: float = 0.002
    clearance: float = 0.01
    material: str = "steel"
    roughness: float = 0.0

@dataclass
class Lids:
    top_type: str = "flat"
    bottom_type: str = "flat"
    top_thickness: float = 0.003
    bottom_thickness: float = 0.003
    seal_clearance: float = 0.001

@dataclass
class Particles:
    kind: str = "sphere"
    diameter: float = 0.005
    count: int = 100
    target_porosity: float = 0.4
    density: float = 2500.0
    mass: float = 0.0
    restitution: float = 0.3
    friction: float = 0.5
    rolling_friction: float = 0.1
    linear_damping: float = 0.1
    angular_damping: float = 0.1
    seed: int = 42

@dataclass
class Packing:
    method: str = "rigid_body"
    gravity: float = -9.81
    substeps: int = 10
    iterations: int = 10
    damping: float = 0.1
    rest_velocity: float = 0.01
    max_time: float = 5.0
    collision_margin: float = 0.001

@dataclass
class Export:
    formats: List[str] = None
    units: str = "m"
    scale: float = 1.0
    wall_mode: str = "surface"
    fluid_mode: str = "none"
    manifold_check: bool = True
    merge_distance: float = 0.001
    
    def __post_init__(self):
        if self.formats is None:
            self.formats = ["stl_binary"]

@dataclass
class CFD:
    regime: str = "laminar"
    inlet_velocity: float = 0.1
    fluid_density: float = 1.225
    fluid_viscosity: float = 1.8e-5
    max_iterations: int = 1000
    convergence_criteria: float = 1e-6
    write_fields: bool = False

@dataclass
class BedParameters:
    bed: BedGeometry = None
    lids: Lids = None
    particles: Particles = None
    packing: Packing = None
    export: Export = None
    cfd: CFD = None
    
    def __post_init__(self):
        if self.bed is None:
            self.bed = BedGeometry()
        if self.lids is None:
            self.lids = Lids()
        if self.particles is None:
            self.particles = Particles()
        if self.packing is None:
            self.packing = Packing()
        if self.export is None:
            self.export = Export()
        if self.cfd is None:
            self.cfd = CFD()

class BedErrorListener(ErrorListener):
    """listener para capturar erros de parsing"""
    
    def __init__(self):
        self.errors = []
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_msg = f"erro de sintaxe na linha {line}:{column} - {msg}"
        self.errors.append(error_msg)

class BedCompilerListener(BedListener):
    """listener antlr para processar a arvore de parsing"""
    
    def __init__(self):
        self.params = BedParameters()
    
    def _parse_number_with_unit(self, number: str, unit: str) -> float:
        """converter numero com unidade para SI"""
        value = float(number)
        
        # conversoes para metros
        if unit == "mm":
            return value / 1000.0
        elif unit == "cm":
            return value / 100.0
        elif unit == "m":
            return value
        
        # conversoes para kg
        elif unit == "g":
            return value / 1000.0
        elif unit == "kg":
            return value
        
        # conversoes para segundos
        elif unit == "s":
            return value
        
        # conversoes para Pa
        elif unit == "Pa":
            return value
        
        # conversoes para N
        elif unit == "N":
            return value
        
        # conversoes para m/s
        elif unit == "m/s":
            return value
        
        # conversoes para kg/m3
        elif unit == "kg/m3":
            return value
        
        # conversoes para Pa.s
        elif unit == "Pa.s":
            return value
        
        # conversoes para m/s2
        elif unit == "m/s2" or unit == "m/s²":
            return value
        
        else:
            return value
    
    # bed properties
    def exitBedDiameter(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.bed.diameter = self._parse_number_with_unit(number, unit)
    
    def exitBedHeight(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.bed.height = self._parse_number_with_unit(number, unit)
    
    def exitBedWallThickness(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.bed.wall_thickness = self._parse_number_with_unit(number, unit)
    
    def exitBedClearance(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.bed.clearance = self._parse_number_with_unit(number, unit)
    
    def exitBedMaterial(self, ctx):
        material = ctx.STRING().getText().strip('"')
        self.params.bed.material = material
    
    def exitBedRoughness(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.bed.roughness = self._parse_number_with_unit(number, unit)
    
    # lids properties
    def exitLidsTopType(self, ctx):
        if hasattr(ctx, 'STRING') and ctx.STRING():
            lid_type = ctx.STRING().getText().strip('"')
        else:
            # pegar apenas o texto do tipo, não toda a regra
            lid_type = ctx.lidType().getText().strip('"')
        self.params.lids.top_type = lid_type
    
    def exitLidsBottomType(self, ctx):
        if hasattr(ctx, 'STRING') and ctx.STRING():
            lid_type = ctx.STRING().getText().strip('"')
        else:
            # pegar apenas o texto do tipo, não toda a regra
            lid_type = ctx.lidType().getText().strip('"')
        self.params.lids.bottom_type = lid_type
    
    def exitLidsTopThickness(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.lids.top_thickness = self._parse_number_with_unit(number, unit)
    
    def exitLidsBottomThickness(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.lids.bottom_thickness = self._parse_number_with_unit(number, unit)
    
    def exitLidsSealClearance(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.lids.seal_clearance = self._parse_number_with_unit(number, unit)
    
    # particles properties
    def exitParticlesKind(self, ctx):
        if hasattr(ctx, 'STRING') and ctx.STRING():
            kind = ctx.STRING().getText().strip('"')
        else:
            # pegar apenas o texto do tipo, não toda a regra
            kind = ctx.particleKind().getText().strip('"')
        self.params.particles.kind = kind
    
    def exitParticlesDiameter(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.particles.diameter = self._parse_number_with_unit(number, unit)
    
    def exitParticlesCount(self, ctx):
        self.params.particles.count = int(float(ctx.NUMBER().getText()))
    
    def exitParticlesTargetPorosity(self, ctx):
        self.params.particles.target_porosity = float(ctx.NUMBER().getText())
    
    def exitParticlesDensity(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.particles.density = self._parse_number_with_unit(number, unit)
    
    def exitParticlesMass(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.particles.mass = self._parse_number_with_unit(number, unit)
    
    def exitParticlesRestitution(self, ctx):
        self.params.particles.restitution = float(ctx.NUMBER().getText())
    
    def exitParticlesFriction(self, ctx):
        self.params.particles.friction = float(ctx.NUMBER().getText())
    
    def exitParticlesRollingFriction(self, ctx):
        self.params.particles.rolling_friction = float(ctx.NUMBER().getText())
    
    def exitParticlesLinearDamping(self, ctx):
        self.params.particles.linear_damping = float(ctx.NUMBER().getText())
    
    def exitParticlesAngularDamping(self, ctx):
        self.params.particles.angular_damping = float(ctx.NUMBER().getText())
    
    def exitParticlesSeed(self, ctx):
        self.params.particles.seed = int(float(ctx.NUMBER().getText()))
    
    # packing properties
    def exitPackingMethodProp(self, ctx):
        if hasattr(ctx, 'STRING') and ctx.STRING():
            method = ctx.STRING().getText().strip('"')
        else:
            # pegar apenas o texto do método, não toda a regra
            method = ctx.packingMethod().getText().strip('"')
        self.params.packing.method = method
    
    def exitPackingGravity(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.packing.gravity = self._parse_number_with_unit(number, unit)
    
    def exitPackingSubsteps(self, ctx):
        self.params.packing.substeps = int(float(ctx.NUMBER().getText()))
    
    def exitPackingIterations(self, ctx):
        self.params.packing.iterations = int(float(ctx.NUMBER().getText()))
    
    def exitPackingDamping(self, ctx):
        self.params.packing.damping = float(ctx.NUMBER().getText())
    
    def exitPackingRestVelocity(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.packing.rest_velocity = self._parse_number_with_unit(number, unit)
    
    def exitPackingMaxTime(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.packing.max_time = self._parse_number_with_unit(number, unit)
    
    def exitPackingCollisionMargin(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.packing.collision_margin = self._parse_number_with_unit(number, unit)
    
    # export properties
    def exitExportFormats(self, ctx):
        formats = []
        for string_ctx in ctx.formatList().STRING():
            formats.append(string_ctx.getText().strip('"'))
        self.params.export.formats = formats
    
    def exitExportUnits(self, ctx):
        units = ctx.STRING().getText().strip('"')
        self.params.export.units = units
    
    def exitExportScale(self, ctx):
        self.params.export.scale = float(ctx.NUMBER().getText())
    
    def exitExportWallMode(self, ctx):
        if hasattr(ctx, 'STRING') and ctx.STRING():
            mode = ctx.STRING().getText().strip('"')
        else:
            # pegar apenas o texto do modo, não toda a regra
            mode = ctx.wallMode().getText().strip('"')
        self.params.export.wall_mode = mode
    
    def exitExportFluidMode(self, ctx):
        if hasattr(ctx, 'STRING') and ctx.STRING():
            mode = ctx.STRING().getText().strip('"')
        else:
            # pegar apenas o texto do modo, não toda a regra
            mode = ctx.fluidMode().getText().strip('"')
        self.params.export.fluid_mode = mode
    
    def exitExportManifoldCheck(self, ctx):
        self.params.export.manifold_check = ctx.BOOLEAN().getText() == "true"
    
    def exitExportMergeDistance(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.export.merge_distance = self._parse_number_with_unit(number, unit)
    
    # cfd properties
    def exitCfdRegimeProp(self, ctx):
        if hasattr(ctx, 'STRING') and ctx.STRING():
            regime = ctx.STRING().getText().strip('"')
        else:
            # pegar apenas o texto do regime, não toda a regra
            regime = ctx.cfdRegime().getText().strip('"')
        self.params.cfd.regime = regime
    
    def exitCfdInletVelocity(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.cfd.inlet_velocity = self._parse_number_with_unit(number, unit)
    
    def exitCfdFluidDensity(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.cfd.fluid_density = self._parse_number_with_unit(number, unit)
    
    def exitCfdFluidViscosity(self, ctx):
        unit = ctx.UNIT().getText()
        number = ctx.NUMBER().getText()
        self.params.cfd.fluid_viscosity = self._parse_number_with_unit(number, unit)
    
    def exitCfdMaxIterations(self, ctx):
        self.params.cfd.max_iterations = int(float(ctx.NUMBER().getText()))
    
    def exitCfdConvergenceCriteria(self, ctx):
        self.params.cfd.convergence_criteria = float(ctx.NUMBER().getText())
    
    def exitCfdWriteFields(self, ctx):
        self.params.cfd.write_fields = ctx.BOOLEAN().getText() == "true"

def compile_bed_file(input_file: str, output_file: str = None, verbose: bool = False) -> str:
    """compilar arquivo .bed para params.json usando antlr"""
    
    if not ANTLR_AVAILABLE:
        raise RuntimeError("antlr nao disponivel - execute setup primeiro")
    
    # ler arquivo de entrada
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read()
    
    # criar stream de entrada
    input_stream = InputStream(input_text)
    
    # criar lexer
    lexer = BedLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    
    # criar parser
    parser = BedParser(token_stream)
    
    # adicionar listener de erros
    error_listener = BedErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    
    # fazer parsing
    tree = parser.bedFile()
    
    # verificar erros
    if error_listener.errors:
        raise SyntaxError(f"erros de sintaxe: {'; '.join(error_listener.errors)}")
    
    # processar arvore
    listener = BedCompilerListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    
    # converter para dict
    params_dict = asdict(listener.params)
    
    # gerar hash
    params_json = json.dumps(params_dict, indent=2, ensure_ascii=False)
    hash_obj = hashlib.sha256(params_json.encode())
    hash_hex = hash_obj.hexdigest()[:8]
    
    # adicionar metadados
    params_dict['_metadata'] = {
        'hash': hash_hex,
        'compiler': 'bed_compiler_antlr_standalone',
        'input_file': input_file
    }
    
    # salvar arquivo
    if output_file is None:
        output_file = Path(input_file).with_suffix('.json').name
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(params_dict, f, indent=2, ensure_ascii=False)
    
    if verbose:
        print(f"compilacao bem-sucedida (antlr): {output_file}")
        print(f"hash: {hash_hex}")
        print(f"particulas: {listener.params.particles.count}")
    
    return output_file

def main():
    """funcao principal"""
    parser = argparse.ArgumentParser(description='compilador .bed para params.json (antlr)')
    parser.add_argument('input', help='arquivo .bed de entrada')
    parser.add_argument('-o', '--output', help='arquivo .json de saida')
    parser.add_argument('-v', '--verbose', action='store_true', help='modo verboso')
    
    args = parser.parse_args()
    
    try:
        output_file = compile_bed_file(args.input, args.output, args.verbose)
        print(f"arquivo compilado: {output_file}")
    except Exception as e:
        print(f"erro na compilacao: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
