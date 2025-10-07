#!/usr/bin/env python3
"""
script para configurar e executar simulacao cfd com openfoam
a partir do modelo 3d gerado pelo blender

workflow:
1. ler parametros do leito (bed.json)
2. exportar geometria do blender para stl
3. criar caso openfoam
4. gerar malha com snappyhexmesh
5. configurar condicoes de contorno
6. executar simulacao
7. pos-processar resultados
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Tuple
import sys


class OpenFOAMCaseGenerator:
    """classe para gerar e executar caso openfoam"""
    
    def __init__(self, bed_json_path: Path, output_dir: Path):
        """
        inicializar gerador de caso openfoam
        
        args:
            bed_json_path: caminho para arquivo.bed.json
            output_dir: diretorio para caso openfoam
        """
        self.bed_json_path = Path(bed_json_path)
        self.output_dir = Path(output_dir)
        self.params = self._load_params()
        self.case_name = self.bed_json_path.stem.replace('.bed', '')
        self.case_dir = self.output_dir / self.case_name
        
    def _load_params(self) -> Dict[str, Any]:
        """carregar parametros do arquivo json"""
        print(f"\n[1/8] carregando parametros de {self.bed_json_path}")
        
        if not self.bed_json_path.exists():
            raise FileNotFoundError(f"arquivo nao encontrado: {self.bed_json_path}")
        
        with open(self.bed_json_path, 'r', encoding='utf-8') as f:
            params = json.load(f)
        
        print(f"  ✓ parametros carregados")
        print(f"    - leito: {params['bed']['diameter']}m x {params['bed']['height']}m")
        print(f"    - particulas: {params['particles']['count']}")
        
        return params
    
    def export_stl_from_blender(self, blend_file: Path) -> Path:
        """
        exportar geometria do blender para stl
        
        args:
            blend_file: arquivo .blend gerado
            
        returns:
            caminho do arquivo stl gerado
        """
        print(f"\n[2/8] exportando stl do blender")
        
        if not blend_file.exists():
            raise FileNotFoundError(f"arquivo blend nao encontrado: {blend_file}")
        
        # criar script python para executar no blender
        export_script = f"""
import bpy
import os

# limpar selecao
bpy.ops.object.select_all(action='DESELECT')

# selecionar todos objetos
bpy.ops.object.select_all(action='SELECT')

# exportar para stl
output_path = "{self.output_dir / f'{self.case_name}.stl'}"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

bpy.ops.export_mesh.stl(
    filepath=output_path,
    use_selection=True,
    ascii=False,  # binario e menor
    use_mesh_modifiers=True
)

print(f"STL exportado: {{output_path}}")
"""
        
        # salvar script temporario
        script_path = self.output_dir / "export_stl.py"
        with open(script_path, 'w') as f:
            f.write(export_script)
        
        # encontrar blender
        blender_paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            "blender"
        ]
        
        blender_exe = None
        for path in blender_paths:
            if Path(path).exists() if path.startswith("C:") else True:
                blender_exe = path
                break
        
        if not blender_exe:
            raise FileNotFoundError("blender nao encontrado no sistema")
        
        # executar blender para exportar
        print(f"  executando blender...")
        result = subprocess.run([
            blender_exe,
            "--background",
            str(blend_file),
            "--python", str(script_path)
        ], capture_output=True, text=True)
        
        # limpar script temporario
        script_path.unlink()
        
        stl_path = self.output_dir / f'{self.case_name}.stl'
        
        if result.returncode == 0 and stl_path.exists():
            size_mb = stl_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ stl exportado: {stl_path}")
            print(f"    tamanho: {size_mb:.2f} mb")
            return stl_path
        else:
            print(f"  ✗ erro ao exportar stl:")
            print(result.stderr)
            raise RuntimeError("falha ao exportar stl")
    
    def create_case_structure(self):
        """criar estrutura de diretorios do caso openfoam"""
        print(f"\n[3/8] criando estrutura do caso openfoam")
        
        # criar diretorios
        dirs = [
            self.case_dir / "0",
            self.case_dir / "constant" / "triSurface",
            self.case_dir / "constant" / "polyMesh",
            self.case_dir / "system"
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        print(f"  ✓ caso criado em: {self.case_dir}")
    
    def copy_stl_to_case(self, stl_path: Path):
        """copiar arquivo stl para o caso"""
        print(f"\n[4/8] copiando stl para caso")
        
        dest = self.case_dir / "constant" / "triSurface" / "leito.stl"
        shutil.copy(stl_path, dest)
        
        print(f"  ✓ stl copiado para: {dest}")
    
    def create_mesh_dict(self):
        """criar dicionarios de geracao de malha"""
        print(f"\n[5/8] criando configuracao de malha")
        
        # obter dimensoes do leito
        diameter = self.params['bed']['diameter']
        height = self.params['bed']['height']
        
        # criar blockmeshdict (malha de fundo)
        blockmesh = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  11                                    |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// criar caixa ao redor do leito (20% maior)
xMin {-diameter * 0.6};
xMax {diameter * 0.6};
yMin {-diameter * 0.6};
yMax {diameter * 0.6};
zMin {-height * 0.1};
zMax {height * 1.1};

vertices
(
    ($xMin $yMin $zMin)
    ($xMax $yMin $zMin)
    ($xMax $yMax $zMin)
    ($xMin $yMax $zMin)
    ($xMin $yMin $zMax)
    ($xMax $yMin $zMax)
    ($xMax $yMax $zMax)
    ($xMin $yMax $zMax)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (40 40 60) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    walls
    {{
        type wall;
        faces
        (
            (0 3 2 1)  // bottom
            (4 5 6 7)  // top
            (0 4 7 3)  // left
            (2 6 5 1)  // right
            (1 5 4 0)  // front
            (3 7 6 2)  // back
        );
    }}
);

mergePatchPairs
(
);

// ************************************************************************* //
"""
        
        # salvar blockmeshdict
        with open(self.case_dir / "system" / "blockMeshDict", 'w') as f:
            f.write(blockmesh)
        
        print(f"  ✓ blockMeshDict criado")
        
        # criar snappyhexmeshdict
        snappy = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  11                                    |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

castellatedMesh true;
snap            true;
addLayers       false;

geometry
{{
    leito.stl
    {{
        type triSurfaceMesh;
        name leito;
    }}
}}

castellatedMeshControls
{{
    maxLocalCells 1000000;
    maxGlobalCells 2000000;
    minRefinementCells 10;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;
    
    features
    (
    );
    
    refinementSurfaces
    {{
        leito
        {{
            level (2 3);
            patchInfo
            {{
                type wall;
            }}
        }}
    }}
    
    resolveFeatureAngle 30;
    
    refinementRegions
    {{
    }}
    
    locationInMesh ({diameter * 0.5} {diameter * 0.5} {height * 0.5});
    allowFreeStandingZoneFaces true;
}}

snapControls
{{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolveIter 30;
    nRelaxIter 5;
}}

addLayersControls
{{
    relativeSizes true;
    layers
    {{
    }}
    expansionRatio 1.0;
    finalLayerThickness 0.3;
    minThickness 0.1;
    nGrow 0;
    featureAngle 60;
    slipFeatureAngle 30;
    nRelaxIter 3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedianAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 50;
}}

meshQualityControls
{{
    maxNonOrtho 65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave 80;
    minVol 1e-13;
    minTetQuality 1e-30;
    minArea -1;
    minTwist 0.02;
    minDeterminant 0.001;
    minFaceWeight 0.02;
    minVolRatio 0.01;
    minTriangleTwist -1;
    nSmoothScale 4;
    errorReduction 0.75;
}}

mergeTolerance 1e-6;

// ************************************************************************* //
"""
        
        with open(self.case_dir / "system" / "snappyHexMeshDict", 'w') as f:
            f.write(snappy)
        
        print(f"  ✓ snappyHexMeshDict criado")
    
    def create_control_dicts(self):
        """criar dicionarios de controle da simulacao"""
        print(f"\n[6/8] criando configuracao de simulacao")
        
        # obter parametros cfd
        cfd = self.params.get('cfd', {})
        
        # valores padrao se nao especificados
        inlet_velocity = float(cfd.get('inlet_velocity', 0.1))
        max_iterations = int(cfd.get('max_iterations', 1000))
        
        # controlDict
        control = f"""/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     simpleFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         {max_iterations};

deltaT          1;

writeControl    timeStep;

writeInterval   100;

purgeWrite      2;

writeFormat     binary;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

// ************************************************************************* //
"""
        
        with open(self.case_dir / "system" / "controlDict", 'w') as f:
            f.write(control)
        
        # fvSchemes
        schemes = """/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind grad(U);
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

// ************************************************************************* //
"""
        
        with open(self.case_dir / "system" / "fvSchemes", 'w') as f:
            f.write(schemes)
        
        # fvSolution
        solution = """/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.1;
        smoother        GaussSeidel;
    }

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    consistent      yes;

    residualControl
    {
        p               1e-4;
        U               1e-4;
    }
}

relaxationFactors
{
    fields
    {
        p               0.3;
    }
    equations
    {
        U               0.7;
    }
}

// ************************************************************************* //
"""
        
        with open(self.case_dir / "system" / "fvSolution", 'w') as f:
            f.write(solution)
        
        print(f"  ✓ arquivos de controle criados")
    
    def create_initial_conditions(self):
        """criar condicoes iniciais e de contorno"""
        print(f"\n[7/8] criando condicoes iniciais")
        
        # obter parametros
        cfd = self.params.get('cfd', {})
        inlet_velocity = float(cfd.get('inlet_velocity', 0.1))
        
        # arquivo U (velocidade)
        u_file = f"""/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 {inlet_velocity});

boundaryField
{{
    leito
    {{
        type            noSlip;
    }}
    
    walls
    {{
        type            noSlip;
    }}
}}

// ************************************************************************* //
"""
        
        with open(self.case_dir / "0" / "U", 'w') as f:
            f.write(u_file)
        
        # arquivo p (pressao)
        p_file = """/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    leito
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            zeroGradient;
    }
}

// ************************************************************************* //
"""
        
        with open(self.case_dir / "0" / "p", 'w') as f:
            f.write(p_file)
        
        # transportProperties
        fluid_viscosity = float(cfd.get('fluid_viscosity', 1.5e-5))
        
        transport = f"""/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

transportModel  Newtonian;

nu              {fluid_viscosity};

// ************************************************************************* //
"""
        
        with open(self.case_dir / "constant" / "transportProperties", 'w') as f:
            f.write(transport)
        
        # turbulenceProperties
        turbulence = """/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

simulationType laminar;

// ************************************************************************* //
"""
        
        with open(self.case_dir / "constant" / "turbulenceProperties", 'w') as f:
            f.write(turbulence)
        
        print(f"  ✓ condicoes iniciais criadas")
    
    def create_run_script(self):
        """criar script allrun para executar caso"""
        print(f"\n[8/8] criando script de execucao")
        
        allrun = """#!/bin/sh
cd "${0%/*}" || exit 1

# source openfoam
source /opt/openfoam11/etc/bashrc

echo "========================================="
echo " executando caso openfoam"
echo "========================================="

echo ""
echo "1. gerando malha de fundo (blockMesh)..."
blockMesh > log.blockMesh 2>&1
if [ $? -ne 0 ]; then
    echo "erro no blockMesh! veja log.blockMesh"
    exit 1
fi
echo "   ✓ malha de fundo criada"

echo ""
echo "2. gerando malha refinada (snappyHexMesh)..."
echo "   (isso pode demorar alguns minutos...)"
snappyHexMesh -overwrite > log.snappyHexMesh 2>&1
if [ $? -ne 0 ]; then
    echo "erro no snappyHexMesh! veja log.snappyHexMesh"
    exit 1
fi
echo "   ✓ malha refinada criada"

echo ""
echo "3. verificando qualidade da malha..."
checkMesh > log.checkMesh 2>&1
echo "   (veja log.checkMesh para detalhes)"

echo ""
echo "4. executando simulacao (simpleFoam)..."
echo "   (monitorando convergencia...)"
simpleFoam > log.simpleFoam 2>&1 &
FOAM_PID=$!

# monitorar convergencia
while kill -0 $FOAM_PID 2>/dev/null; do
    if [ -f log.simpleFoam ]; then
        LAST_TIME=$(grep "^Time = " log.simpleFoam | tail -1)
        printf "\r   %s" "$LAST_TIME"
    fi
    sleep 2
done
wait $FOAM_PID
FOAM_EXIT=$?

echo ""
if [ $FOAM_EXIT -eq 0 ]; then
    echo "   ✓ simulacao concluida!"
else
    echo "   ✗ erro na simulacao! veja log.simpleFoam"
    exit 1
fi

echo ""
echo "========================================="
echo " caso executado com sucesso!"
echo "========================================="
echo ""
echo "proximos passos:"
echo "  - visualizar: touch caso.foam && paraview caso.foam"
echo "  - pos-processar: postProcess -func sample"
echo ""

# criar arquivo .foam para paraview
touch caso.foam

exit 0
"""
        
        allrun_path = self.case_dir / "Allrun"
        with open(allrun_path, 'w') as f:
            f.write(allrun)
        
        # tornar executavel (no wsl)
        allrun_path.chmod(0o755)
        
        print(f"  ✓ script Allrun criado")
    
    def run(self, blend_file: Path, execute_simulation: bool = True):
        """
        executar todo o processo
        
        args:
            blend_file: arquivo .blend gerado pelo blender
            execute_simulation: se true, executa a simulacao apos criar o caso
        """
        print(f"\n{'='*60}")
        print(f"  configuracao de caso openfoam")
        print(f"{'='*60}")
        
        try:
            # exportar stl
            stl_path = self.export_stl_from_blender(blend_file)
            
            # criar estrutura do caso
            self.create_case_structure()
            
            # copiar stl
            self.copy_stl_to_case(stl_path)
            
            # criar dicionarios de malha
            self.create_mesh_dict()
            
            # criar dicionarios de controle
            self.create_control_dicts()
            
            # criar condicoes iniciais
            self.create_initial_conditions()
            
            # criar script de execucao
            self.create_run_script()
            
            print(f"\n{'='*60}")
            print(f"  ✓ caso openfoam configurado com sucesso!")
            print(f"{'='*60}")
            print(f"\ncaso criado em: {self.case_dir}")
            print(f"\npara executar a simulacao:")
            print(f"  cd {self.case_dir}")
            print(f"  ./Allrun")
            print(f"\nou execute este script com --run")
            
            if execute_simulation:
                self.execute_simulation()
            
            return True
            
        except Exception as e:
            print(f"\n✗ erro: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def execute_simulation(self):
        """executar simulacao openfoam"""
        print(f"\n{'='*60}")
        print(f"  executando simulacao openfoam")
        print(f"{'='*60}")
        print(f"\ndiretorio: {self.case_dir}")
        print(f"isso pode demorar varios minutos...")
        print(f"pressione ctrl+c para cancelar")
        print()
        
        try:
            # executar allrun
            result = subprocess.run(
                ["./Allrun"],
                cwd=self.case_dir,
                shell=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"\n✓ simulacao concluida com sucesso!")
                print(f"\narquivos de resultado em: {self.case_dir}")
                print(f"\nvisualizar:")
                print(f"  cd {self.case_dir}")
                print(f"  paraview caso.foam")
            else:
                print(f"\n✗ simulacao falhou com codigo {result.returncode}")
                print(f"verifique os arquivos de log em {self.case_dir}")
                
        except KeyboardInterrupt:
            print(f"\n\nsimulacao cancelada pelo usuario")
        except Exception as e:
            print(f"\n✗ erro ao executar simulacao: {e}")


def main():
    """funcao principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='configurar e executar caso openfoam a partir de modelo blender'
    )
    parser.add_argument(
        'bed_json',
        type=str,
        help='caminho para arquivo .bed.json'
    )
    parser.add_argument(
        'blend_file',
        type=str,
        help='caminho para arquivo .blend gerado'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output/cfd',
        help='diretorio de saida para caso openfoam'
    )
    parser.add_argument(
        '--run',
        action='store_true',
        help='executar simulacao apos criar caso'
    )
    
    args = parser.parse_args()
    
    # criar gerador
    generator = OpenFOAMCaseGenerator(
        bed_json_path=Path(args.bed_json),
        output_dir=Path(args.output_dir)
    )
    
    # executar
    success = generator.run(
        blend_file=Path(args.blend_file),
        execute_simulation=args.run
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

