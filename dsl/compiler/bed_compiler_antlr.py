#!/usr/bin/env python3
"""
compilador para linguagem .bed usando antlr
versao que usa a gramatica bed.g4 corretamente
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
    
    # importar parser gerado (sera criado pelo setup_antlr.py)
    sys.path.append(str(Path(__file__).parent.parent / "generated" / "grammar"))
    from BedLexer import BedLexer
    from BedParser import BedParser
    from BedListener import BedListener
    
    ANTLR_AVAILABLE = True
except ImportError as e:
    print(f"aviso: antlr nao disponivel: {e}")
    print("execute: python setup_antlr.py para configurar")
    ANTLR_AVAILABLE = False

# importar estruturas de dados do compilador original
from bed_compiler import (
    BedGeometry, Lids, Particles, Packing, Export, CFD, BedParameters
)

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
        self.bed_params = BedParameters(
            bed=BedGeometry(diameter=0.05, height=0.1, wall_thickness=0.002, clearance=0.01),
            lids=Lids(),
            particles=Particles(),
            packing=Packing(),
            export=Export()
        )
        self.errors = []
    
    def _parse_number_with_unit(self, number_text: str, unit_text: str) -> float:
        """converte numero com unidade para si"""
        try:
            number = float(number_text)
            unit = unit_text if unit_text else ""
            
            # conversoes para si
            conversions = {
                'm': 1.0, 'cm': 0.01, 'mm': 0.001,
                'kg': 1.0, 'g': 0.001,
                's': 1.0,
                'Pa': 1.0, 'N': 1.0,
                'm/s': 1.0, 'kg/m3': 1.0, 'Pa.s': 1.0,
                'm/s2': 1.0, 'm/s²': 1.0,
                '': 1.0
            }
            
            return number * conversions.get(unit, 1.0)
            
        except ValueError as e:
            self.errors.append(f"erro ao converter numero: {number_text} {unit_text}")
            return 0.0
    
    # bed section
    def exitBedDiameter(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.bed.diameter = self._parse_number_with_unit(number, unit)
    
    def exitBedHeight(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.bed.height = self._parse_number_with_unit(number, unit)
    
    def exitBedWallThickness(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.bed.wall_thickness = self._parse_number_with_unit(number, unit)
    
    def exitBedClearance(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.bed.clearance = self._parse_number_with_unit(number, unit)
    
    def exitBedMaterial(self, ctx):
        material = ctx.STRING().getText().strip('"')
        self.bed_params.bed.material = material
    
    def exitBedRoughness(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.bed.roughness = self._parse_number_with_unit(number, unit)
    
    # lids section
    def exitLidsTopType(self, ctx):
        lid_type = ctx.lidType().getText().strip('"')
        self.bed_params.lids.top_type = lid_type
    
    def exitLidsBottomType(self, ctx):
        lid_type = ctx.lidType().getText().strip('"')
        self.bed_params.lids.bottom_type = lid_type
    
    def exitLidsTopThickness(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.lids.top_thickness = self._parse_number_with_unit(number, unit)
    
    def exitLidsBottomThickness(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.lids.bottom_thickness = self._parse_number_with_unit(number, unit)
    
    def exitLidsSealClearance(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.lids.seal_clearance = self._parse_number_with_unit(number, unit)
    
    # particles section
    def exitParticlesKind(self, ctx):
        kind = ctx.particleKind().getText().strip('"')
        self.bed_params.particles.kind = kind
    
    def exitParticlesDiameter(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.particles.diameter = self._parse_number_with_unit(number, unit)
    
    def exitParticlesCount(self, ctx):
        count = int(float(ctx.NUMBER().getText()))
        self.bed_params.particles.count = count
        self.bed_params.particles.target_porosity = None  # exclusivo
    
    def exitParticlesTargetPorosity(self, ctx):
        porosity = float(ctx.NUMBER().getText())
        self.bed_params.particles.target_porosity = porosity
        self.bed_params.particles.count = None  # exclusivo
    
    def exitParticlesDensity(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.particles.density = self._parse_number_with_unit(number, unit)
    
    def exitParticlesMass(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.particles.mass = self._parse_number_with_unit(number, unit)
    
    def exitParticlesRestitution(self, ctx):
        self.bed_params.particles.restitution = float(ctx.NUMBER().getText())
    
    def exitParticlesFriction(self, ctx):
        self.bed_params.particles.friction = float(ctx.NUMBER().getText())
    
    def exitParticlesRollingFriction(self, ctx):
        self.bed_params.particles.rolling_friction = float(ctx.NUMBER().getText())
    
    def exitParticlesLinearDamping(self, ctx):
        self.bed_params.particles.linear_damping = float(ctx.NUMBER().getText())
    
    def exitParticlesAngularDamping(self, ctx):
        self.bed_params.particles.angular_damping = float(ctx.NUMBER().getText())
    
    def exitParticlesSeed(self, ctx):
        self.bed_params.particles.seed = int(float(ctx.NUMBER().getText()))
    
    # packing section
    def exitPackingMethodProp(self, ctx):
        method = ctx.packingMethod().getText().strip('"')
        self.bed_params.packing.method = method
    
    def exitPackingGravity(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.packing.gravity = self._parse_number_with_unit(number, unit)
    
    def exitPackingSubsteps(self, ctx):
        self.bed_params.packing.substeps = int(float(ctx.NUMBER().getText()))
    
    def exitPackingIterations(self, ctx):
        self.bed_params.packing.iterations = int(float(ctx.NUMBER().getText()))
    
    def exitPackingDamping(self, ctx):
        self.bed_params.packing.damping = float(ctx.NUMBER().getText())
    
    def exitPackingRestVelocity(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.packing.rest_velocity = self._parse_number_with_unit(number, unit)
    
    def exitPackingMaxTime(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.packing.max_time = self._parse_number_with_unit(number, unit)
    
    def exitPackingCollisionMargin(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.packing.collision_margin = self._parse_number_with_unit(number, unit)
    
    # export section
    def exitExportFormats(self, ctx):
        format_list = ctx.formatList()
        formats = []
        for string_node in format_list.STRING():
            format_name = string_node.getText().strip('"')
            formats.append(format_name)
        self.bed_params.export.formats = formats
    
    def exitExportUnits(self, ctx):
        units = ctx.STRING().getText().strip('"')
        self.bed_params.export.units = units
    
    def exitExportScale(self, ctx):
        self.bed_params.export.scale = float(ctx.NUMBER().getText())
    
    def exitExportWallMode(self, ctx):
        wall_mode = ctx.wallMode().getText().strip('"')
        self.bed_params.export.wall_mode = wall_mode
    
    def exitExportFluidMode(self, ctx):
        fluid_mode = ctx.fluidMode().getText().strip('"')
        self.bed_params.export.fluid_mode = fluid_mode
    
    def exitExportManifoldCheck(self, ctx):
        boolean_val = ctx.BOOLEAN().getText().lower() == 'true'
        self.bed_params.export.manifold_check = boolean_val
    
    def exitExportMergeDistance(self, ctx):
        number = ctx.NUMBER().getText()
        unit = ctx.UNIT().getText() if ctx.UNIT() else ""
        self.bed_params.export.merge_distance = self._parse_number_with_unit(number, unit)
    
    # cfd section (opcional)
    def enterCfdSection(self, ctx):
        # criar objeto cfd quando entrar na secao
        if self.bed_params.cfd is None:
            self.bed_params.cfd = CFD()
    
    def exitCfdRegimeProp(self, ctx):
        if self.bed_params.cfd:
            regime = ctx.cfdRegime().getText().strip('"')
            self.bed_params.cfd.regime = regime
    
    def exitCfdInletVelocity(self, ctx):
        if self.bed_params.cfd:
            number = ctx.NUMBER().getText()
            unit = ctx.UNIT().getText() if ctx.UNIT() else ""
            self.bed_params.cfd.inlet_velocity = self._parse_number_with_unit(number, unit)
    
    def exitCfdFluidDensity(self, ctx):
        if self.bed_params.cfd:
            number = ctx.NUMBER().getText()
            unit = ctx.UNIT().getText() if ctx.UNIT() else ""
            self.bed_params.cfd.fluid_density = self._parse_number_with_unit(number, unit)
    
    def exitCfdFluidViscosity(self, ctx):
        if self.bed_params.cfd:
            number = ctx.NUMBER().getText()
            unit = ctx.UNIT().getText() if ctx.UNIT() else ""
            self.bed_params.cfd.fluid_viscosity = self._parse_number_with_unit(number, unit)
    
    def exitCfdMaxIterations(self, ctx):
        if self.bed_params.cfd:
            self.bed_params.cfd.max_iterations = int(float(ctx.NUMBER().getText()))
    
    def exitCfdConvergenceCriteria(self, ctx):
        if self.bed_params.cfd:
            self.bed_params.cfd.convergence_criteria = float(ctx.NUMBER().getText())
    
    def exitCfdWriteFields(self, ctx):
        if self.bed_params.cfd:
            boolean_val = ctx.BOOLEAN().getText().lower() == 'true'
            self.bed_params.cfd.write_fields = boolean_val

class BedCompilerAntlr:
    """compilador que usa antlr para parsing"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def parse_bed_file(self, filepath: str) -> Optional[BedParameters]:
        """faz parsing de arquivo .bed usando antlr"""
        if not ANTLR_AVAILABLE:
            self.errors.append("antlr nao disponivel - execute setup_antlr.py")
            return None
        
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
        """faz parsing do conteudo usando antlr"""
        if not ANTLR_AVAILABLE:
            self.errors.append("antlr nao disponivel")
            return None
        
        try:
            # criar lexer e parser
            input_stream = InputStream(content)
            lexer = BedLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = BedParser(token_stream)
            
            # configurar error listener
            error_listener = BedErrorListener()
            parser.removeErrorListeners()
            parser.addErrorListener(error_listener)
            
            # fazer parsing
            tree = parser.bedFile()
            
            # verificar erros de sintaxe
            if error_listener.errors:
                self.errors.extend(error_listener.errors)
                return None
            
            # processar arvore com listener
            listener = BedCompilerListener()
            walker = ParseTreeWalker()
            walker.walk(listener, tree)
            
            # verificar erros do listener
            if listener.errors:
                self.errors.extend(listener.errors)
                return None
            
            # validar parametros
            if not self._validate_parameters(listener.bed_params):
                return None
            
            # calcular hash
            listener.bed_params.hash = listener.bed_params.calculate_hash()
            
            return listener.bed_params
            
        except Exception as e:
            self.errors.append(f"erro no parsing antlr: {e}")
            return None
    
    def _validate_parameters(self, params: BedParameters) -> bool:
        """valida parametros (mesma validacao do compilador original)"""
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
            
        # validar count xor target_porosity
        if params.particles.count is not None and params.particles.target_porosity is not None:
            self.errors.append("especifique count ou target_porosity, nao ambos")
            valid = False
            
        if params.particles.count is None and params.particles.target_porosity is None:
            self.errors.append("especifique count ou target_porosity")
            valid = False
        
        return valid
    
    def compile_to_json(self, params: BedParameters, output_path: str) -> bool:
        """compila para json (mesmo metodo do compilador original)"""
        try:
            data = asdict(params)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.errors.append(f"erro ao escrever json: {e}")
            return False

def main():
    """funcao principal"""
    if not ANTLR_AVAILABLE:
        print("erro: antlr nao disponivel")
        print("execute: python setup_antlr.py para configurar")
        return 1
    
    parser = argparse.ArgumentParser(description='compilador .bed usando antlr')
    parser.add_argument('input', help='arquivo .bed de entrada')
    parser.add_argument('-o', '--output', default='params.json', help='arquivo params.json de saida')
    parser.add_argument('-v', '--verbose', action='store_true', help='saida detalhada')
    
    args = parser.parse_args()
    
    # compilar
    compiler = BedCompilerAntlr()
    params = compiler.parse_bed_file(args.input)
    
    if not params:
        print("erro na compilacao:")
        for error in compiler.errors:
            print(f"  - {error}")
        return 1
    
    # salvar params.json
    if compiler.compile_to_json(params, args.output):
        print(f"compilacao bem-sucedida (antlr): {args.output}")
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
