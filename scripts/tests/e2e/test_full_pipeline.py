#!/usr/bin/env python3
# testes end-to-end completos do pipeline cfd
# testa desde a geracao de leitos ate a simulacao openfoam
import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
import shutil

class E2ETestSuite:
    """suite de testes end-to-end do pipeline completo"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_dir = Path(__file__).parent
        self.output_dir = self.test_dir / "outputs"
        self.results_dir = self.test_dir / "results"
        self.logs_dir = self.test_dir / "logs"
        
        # criar estrutura
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # resultados dos testes
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
        }
        
    def log(self, message, level="info"):
        """registra mensagem no log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            'info': '[info]',
            'success': '[ok]',
            'error': '[erro]',
            'warning': '[aviso]'
        }.get(level, '[info]')
        
        print(f"{timestamp} {prefix} {message}")
        
        # salvar em arquivo
        log_file = self.logs_dir / f"test_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} {prefix} {message}\n")
    
    def create_test_bed_file(self, test_name, params):
        """cria arquivo .bed para teste"""
        bed_content = f"""bed {{
    diameter = {params['diameter']}m
    height = {params['height']}m
    wall_thickness = {params.get('wall_thickness', 0.002)}m
    shape = "cylinder"
}}

lids {{
    top_type = "flat"
    bottom_type = "flat"
    thickness = 0.003m
}}

particles {{
    count = {params['particle_count']}
    kind = "sphere"
    diameter = {params['particle_diameter']}m
    mass = {params.get('particle_mass', 0.1)}kg
    friction = 0.5
    restitution = 0.3
}}

packing {{
    method = "rigid_body"
    seed = {params.get('seed', 42)}
    substeps = 10
    iterations = {params.get('packing_iterations', 50)}
    gravity = (0, 0, -9.81) m/s2
}}

export {{
    formats = ["blend", "stl"]
    output_dir = "scripts/tests/e2e/outputs/{test_name}"
}}

cfd {{
    regime = "laminar"
    inlet_velocity = {params.get('inlet_velocity', 0.1)} m/s
    outlet_pressure = 0 Pa
    fluid_density = {params.get('fluid_density', 1000)} kg/m3
    fluid_viscosity = {params.get('fluid_viscosity', 0.001)} Pa.s
    max_iterations = {params.get('max_iterations', 100)}
    convergence_criteria = 1e-4
}}
"""
        
        bed_file = self.output_dir / f"{test_name}.bed"
        with open(bed_file, 'w', encoding='utf-8') as f:
            f.write(bed_content)
        
        self.log(f"arquivo .bed criado: {bed_file.name}")
        return bed_file
    
    def compile_bed_file(self, bed_file):
        """compila arquivo .bed para json"""
        self.log(f"compilando {bed_file.name}...")
        
        compiler = self.project_root / "dsl" / "compiler" / "bed_compiler_antlr_standalone.py"
        
        try:
            result = subprocess.run(
                [sys.executable, str(compiler), str(bed_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            json_file = bed_file.with_suffix('.bed.json')
            
            if json_file.exists():
                self.log(f"compilacao bem-sucedida: {json_file.name}", "success")
                return json_file
            else:
                self.log(f"compilacao falhou: json nao gerado", "error")
                self.log(f"stderr: {result.stderr}", "error")
                return None
                
        except Exception as e:
            self.log(f"erro ao compilar: {e}", "error")
            return None
    
    def generate_3d_model(self, json_file, test_name):
        """gera modelo 3d no blender"""
        self.log(f"gerando modelo 3d para {test_name}...")
        
        blender_script = self.project_root / "scripts" / "blender_scripts" / "leito_extracao.py"
        output_blend = self.output_dir / f"{test_name}.blend"
        
        # encontrar blender
        blender_paths = ["blender"]
        if sys.platform == "win32":
            blender_paths.extend([
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            ])
        
        blender_exe = None
        for path in blender_paths:
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    blender_exe = path
                    break
            except:
                continue
        
        if not blender_exe:
            self.log("blender nao encontrado", "error")
            return None
        
        # executar blender headless
        try:
            cmd = [
                blender_exe,
                "--background",
                "--python", str(blender_script),
                "--",
                "--params", str(json_file),
                "--output", str(output_blend)
            ]
            
            self.log(f"executando blender headless...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            # salvar log do blender
            blender_log = self.logs_dir / f"{test_name}_blender.log"
            with open(blender_log, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
                f.write("\n--- STDERR ---\n")
                f.write(result.stderr)
            
            if output_blend.exists():
                size_mb = output_blend.stat().st_size / (1024 * 1024)
                self.log(f"modelo 3d gerado: {output_blend.name} ({size_mb:.2f} mb)", "success")
                return output_blend
            else:
                self.log(f"modelo 3d nao foi gerado", "error")
                self.log(f"veja log em: {blender_log}", "warning")
                return None
                
        except subprocess.TimeoutExpired:
            self.log("timeout ao gerar modelo 3d (>5 min)", "error")
            return None
        except Exception as e:
            self.log(f"erro ao gerar modelo 3d: {e}", "error")
            return None
    
    def open_model_in_blender(self, blend_file):
        """abre modelo no blender (gui)"""
        self.log(f"abrindo {blend_file.name} no blender...")
        
        blender_paths = ["blender"]
        if sys.platform == "win32":
            blender_paths.extend([
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            ])
        
        for blender_exe in blender_paths:
            try:
                subprocess.Popen([blender_exe, str(blend_file)])
                self.log("blender aberto (gui)", "success")
                return True
            except:
                continue
        
        self.log("nao foi possivel abrir blender", "warning")
        return False
    
    def setup_openfoam_case(self, json_file, blend_file, test_name):
        """configura caso openfoam"""
        self.log(f"configurando caso openfoam para {test_name}...")
        
        setup_script = self.project_root / "scripts" / "openfoam_scripts" / "setup_openfoam_case.py"
        cfd_output = self.output_dir / f"{test_name}_cfd"
        
        try:
            cmd = [
                sys.executable,
                str(setup_script),
                str(json_file),
                str(blend_file),
                "--output-dir", str(cfd_output)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # salvar log
            setup_log = self.logs_dir / f"{test_name}_openfoam_setup.log"
            with open(setup_log, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
                f.write("\n--- STDERR ---\n")
                f.write(result.stderr)
            
            if cfd_output.exists():
                self.log(f"caso openfoam criado: {cfd_output.name}", "success")
                return cfd_output
            else:
                self.log(f"caso openfoam nao foi criado", "error")
                return None
                
        except Exception as e:
            self.log(f"erro ao configurar openfoam: {e}", "error")
            return None
    
    def run_openfoam_simulation(self, case_dir, test_name, quick=True):
        """executa simulacao openfoam"""
        self.log(f"executando simulacao openfoam para {test_name}...")
        
        if sys.platform != "win32":
            self.log("simulacao openfoam apenas para windows com wsl", "warning")
            return False
        
        # verificar wsl
        try:
            subprocess.run(["wsl", "--status"], capture_output=True, timeout=5)
        except:
            self.log("wsl nao disponivel", "error")
            return False
        
        # converter caminho para wsl
        wsl_path = str(case_dir).replace('\\', '/').replace('C:', '/mnt/c')
        
        # comandos openfoam
        commands = [
            f"cd {wsl_path}",
            "source /opt/openfoam11/etc/bashrc",
            "blockMesh > log.blockMesh 2>&1"
        ]
        
        if not quick:
            commands.extend([
                "snappyHexMesh -overwrite > log.snappyHexMesh 2>&1",
                "checkMesh > log.checkMesh 2>&1",
                "simpleFoam > log.simpleFoam 2>&1"
            ])
        
        full_cmd = " && ".join(commands)
        
        try:
            self.log("executando comandos openfoam no wsl...")
            
            result = subprocess.run(
                ["wsl", "-e", "bash", "-c", full_cmd],
                capture_output=True,
                text=True,
                timeout=600 if quick else 3600
            )
            
            # salvar log
            sim_log = self.logs_dir / f"{test_name}_openfoam_run.log"
            with open(sim_log, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
                f.write("\n--- STDERR ---\n")
                f.write(result.stderr)
            
            if result.returncode == 0:
                self.log("simulacao concluida", "success")
                return True
            else:
                self.log(f"simulacao com erros (codigo {result.returncode})", "warning")
                self.log(f"veja log em: {sim_log}", "warning")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("timeout na simulacao", "error")
            return False
        except Exception as e:
            self.log(f"erro ao executar simulacao: {e}", "error")
            return False
    
    def record_test_result(self, test_name, test_type, success, duration, details=None):
        """registra resultado do teste"""
        result = {
            'name': test_name,
            'type': test_type,
            'success': success,
            'duration': duration,
            'details': details or {}
        }
        
        self.test_results['tests'].append(result)
        self.test_results['summary']['total'] += 1
        
        if success:
            self.test_results['summary']['passed'] += 1
        else:
            self.test_results['summary']['failed'] += 1
    
    def test_basic_generation(self):
        """teste 1: geracao basica de leito"""
        test_name = "test01_basic_generation"
        self.log(f"\n{'='*70}")
        self.log(f"TESTE 1: geracao basica de leito")
        self.log(f"{'='*70}")
        
        start_time = time.time()
        
        # parametros simples
        params = {
            'diameter': 0.05,
            'height': 0.1,
            'particle_count': 20,
            'particle_diameter': 0.005,
            'packing_iterations': 30
        }
        
        # criar e compilar
        bed_file = self.create_test_bed_file(test_name, params)
        json_file = self.compile_bed_file(bed_file)
        
        success = json_file is not None
        duration = time.time() - start_time
        
        self.record_test_result(
            test_name,
            "basic_generation",
            success,
            duration,
            {'params': params, 'files_created': success}
        )
        
        return success
    
    def test_3d_generation(self):
        """teste 2: geracao 3d completa"""
        test_name = "test02_3d_generation"
        self.log(f"\n{'='*70}")
        self.log(f"TESTE 2: geracao 3d completa")
        self.log(f"{'='*70}")
        
        start_time = time.time()
        
        params = {
            'diameter': 0.05,
            'height': 0.1,
            'particle_count': 30,
            'particle_diameter': 0.005,
            'packing_iterations': 50
        }
        
        # pipeline completo
        bed_file = self.create_test_bed_file(test_name, params)
        json_file = self.compile_bed_file(bed_file)
        
        if not json_file:
            duration = time.time() - start_time
            self.record_test_result(test_name, "3d_generation", False, duration)
            return False
        
        blend_file = self.generate_3d_model(json_file, test_name)
        
        success = blend_file is not None
        duration = time.time() - start_time
        
        self.record_test_result(
            test_name,
            "3d_generation",
            success,
            duration,
            {
                'params': params,
                'blend_size_mb': blend_file.stat().st_size / (1024*1024) if success else 0
            }
        )
        
        return success
    
    def test_3d_and_open_blender(self):
        """teste 3: gerar 3d e abrir no blender"""
        test_name = "test03_3d_open_blender"
        self.log(f"\n{'='*70}")
        self.log(f"TESTE 3: gerar 3d e abrir no blender")
        self.log(f"{'='*70}")
        
        start_time = time.time()
        
        params = {
            'diameter': 0.08,
            'height': 0.15,
            'particle_count': 50,
            'particle_diameter': 0.006,
            'packing_iterations': 50
        }
        
        # gerar modelo
        bed_file = self.create_test_bed_file(test_name, params)
        json_file = self.compile_bed_file(bed_file)
        
        if not json_file:
            duration = time.time() - start_time
            self.record_test_result(test_name, "3d_open_blender", False, duration)
            return False
        
        blend_file = self.generate_3d_model(json_file, test_name)
        
        if not blend_file:
            duration = time.time() - start_time
            self.record_test_result(test_name, "3d_open_blender", False, duration)
            return False
        
        # abrir no blender
        opened = self.open_model_in_blender(blend_file)
        
        duration = time.time() - start_time
        
        self.record_test_result(
            test_name,
            "3d_open_blender",
            opened,
            duration,
            {'params': params, 'blender_opened': opened}
        )
        
        if opened:
            self.log("blender aberto - feche manualmente para continuar", "warning")
            input("pressione enter para continuar os testes...")
        
        return opened
    
    def test_openfoam_setup(self):
        """teste 4: configuracao openfoam"""
        test_name = "test04_openfoam_setup"
        self.log(f"\n{'='*70}")
        self.log(f"TESTE 4: configuracao openfoam")
        self.log(f"{'='*70}")
        
        start_time = time.time()
        
        params = {
            'diameter': 0.05,
            'height': 0.1,
            'particle_count': 20,
            'particle_diameter': 0.005,
            'packing_iterations': 30
        }
        
        # gerar modelo
        bed_file = self.create_test_bed_file(test_name, params)
        json_file = self.compile_bed_file(bed_file)
        
        if not json_file:
            duration = time.time() - start_time
            self.record_test_result(test_name, "openfoam_setup", False, duration)
            return False
        
        blend_file = self.generate_3d_model(json_file, test_name)
        
        if not blend_file:
            duration = time.time() - start_time
            self.record_test_result(test_name, "openfoam_setup", False, duration)
            return False
        
        # configurar openfoam
        case_dir = self.setup_openfoam_case(json_file, blend_file, test_name)
        
        success = case_dir is not None
        duration = time.time() - start_time
        
        self.record_test_result(
            test_name,
            "openfoam_setup",
            success,
            duration,
            {'params': params, 'case_created': success}
        )
        
        return success
    
    def test_full_simulation_quick(self):
        """teste 5: simulacao completa rapida (apenas blockmesh)"""
        test_name = "test05_full_simulation_quick"
        self.log(f"\n{'='*70}")
        self.log(f"TESTE 5: simulacao completa rapida")
        self.log(f"{'='*70}")
        
        start_time = time.time()
        
        params = {
            'diameter': 0.05,
            'height': 0.1,
            'particle_count': 15,
            'particle_diameter': 0.005,
            'packing_iterations': 30,
            'max_iterations': 50
        }
        
        # pipeline completo
        bed_file = self.create_test_bed_file(test_name, params)
        json_file = self.compile_bed_file(bed_file)
        
        if not json_file:
            duration = time.time() - start_time
            self.record_test_result(test_name, "full_simulation_quick", False, duration)
            return False
        
        blend_file = self.generate_3d_model(json_file, test_name)
        
        if not blend_file:
            duration = time.time() - start_time
            self.record_test_result(test_name, "full_simulation_quick", False, duration)
            return False
        
        case_dir = self.setup_openfoam_case(json_file, blend_file, test_name)
        
        if not case_dir:
            duration = time.time() - start_time
            self.record_test_result(test_name, "full_simulation_quick", False, duration)
            return False
        
        # executar simulacao rapida
        sim_success = self.run_openfoam_simulation(case_dir, test_name, quick=True)
        
        duration = time.time() - start_time
        
        self.record_test_result(
            test_name,
            "full_simulation_quick",
            sim_success,
            duration,
            {'params': params, 'simulation_completed': sim_success}
        )
        
        return sim_success
    
    def test_parametric_study(self):
        """teste 6: estudo parametrico (multiplos leitos)"""
        test_name_base = "test06_parametric"
        self.log(f"\n{'='*70}")
        self.log(f"TESTE 6: estudo parametrico")
        self.log(f"{'='*70}")
        
        start_time = time.time()
        
        # variacoes
        diameters = [0.05, 0.08]
        particle_counts = [20, 30]
        
        total = len(diameters) * len(particle_counts)
        self.log(f"gerando {total} leitos...")
        
        success_count = 0
        
        for i, diameter in enumerate(diameters):
            for j, count in enumerate(particle_counts):
                test_name = f"{test_name_base}_d{i}_c{j}"
                
                params = {
                    'diameter': diameter,
                    'height': 0.1,
                    'particle_count': count,
                    'particle_diameter': 0.005,
                    'packing_iterations': 30
                }
                
                self.log(f"  variacao {i*len(particle_counts)+j+1}/{total}: d={diameter}, c={count}")
                
                bed_file = self.create_test_bed_file(test_name, params)
                json_file = self.compile_bed_file(bed_file)
                
                if json_file:
                    success_count += 1
        
        duration = time.time() - start_time
        success = success_count == total
        
        self.record_test_result(
            test_name_base,
            "parametric_study",
            success,
            duration,
            {
                'total_variations': total,
                'successful': success_count,
                'variations': {'diameters': diameters, 'particle_counts': particle_counts}
            }
        )
        
        return success
    
    def generate_report(self):
        """gera relatorio final dos testes"""
        self.log(f"\n{'='*70}")
        self.log(f"RELATORIO FINAL DOS TESTES E2E")
        self.log(f"{'='*70}")
        
        summary = self.test_results['summary']
        
        self.log(f"\ntotal de testes: {summary['total']}")
        self.log(f"[ok] passou: {summary['passed']}")
        self.log(f"[erro] falhou: {summary['failed']}")
        self.log(f"[skip] pulados: {summary['skipped']}")
        
        if summary['total'] > 0:
            success_rate = (summary['passed'] / summary['total']) * 100
            self.log(f"\ntaxa de sucesso: {success_rate:.1f}%")
        
        # detalhes por teste
        self.log(f"\ndetalhes dos testes:")
        for test in self.test_results['tests']:
            status = "[ok]" if test['success'] else "[falha]"
            self.log(f"  {status} {test['name']} ({test['duration']:.2f}s)")
        
        # salvar relatorio json
        report_file = self.results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        self.log(f"\nrelatorio salvo: {report_file}")
        
        # resumo de arquivos gerados
        self.log(f"\narquivos gerados em: {self.output_dir}")
        bed_files = list(self.output_dir.glob("*.bed"))
        json_files = list(self.output_dir.glob("*.bed.json"))
        blend_files = list(self.output_dir.glob("*.blend"))
        
        self.log(f"  arquivos .bed: {len(bed_files)}")
        self.log(f"  arquivos .bed.json: {len(json_files)}")
        self.log(f"  arquivos .blend: {len(blend_files)}")
        
        return summary['failed'] == 0
    
    def run_all_tests(self, skip_interactive=False):
        """executa todos os testes"""
        self.log("="*70)
        self.log("INICIANDO SUITE DE TESTES E2E")
        self.log("="*70)
        self.log(f"diretorio de saida: {self.output_dir}")
        self.log(f"diretorio de resultados: {self.results_dir}")
        self.log(f"diretorio de logs: {self.logs_dir}")
        
        # executar testes
        self.test_basic_generation()
        self.test_3d_generation()
        
        if not skip_interactive:
            self.test_3d_and_open_blender()
        else:
            self.log("\nteste 3 (abrir blender) pulado (modo nao-interativo)", "warning")
            self.test_results['summary']['skipped'] += 1
        
        self.test_openfoam_setup()
        self.test_full_simulation_quick()
        self.test_parametric_study()
        
        # relatorio final
        all_passed = self.generate_report()
        
        return all_passed

def main():
    """funcao principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='testes end-to-end do pipeline cfd')
    parser.add_argument('--skip-interactive', action='store_true',
                       help='pular testes interativos (abrir blender)')
    parser.add_argument('--test', type=str,
                       help='executar teste especifico (ex: test_3d_generation)')
    
    args = parser.parse_args()
    
    # criar suite
    suite = E2ETestSuite()
    
    if args.test:
        # executar teste especifico
        test_method = getattr(suite, args.test, None)
        if test_method:
            test_method()
            suite.generate_report()
        else:
            print(f"[erro] teste nao encontrado: {args.test}")
            sys.exit(1)
    else:
        # executar todos
        success = suite.run_all_tests(skip_interactive=args.skip_interactive)
        
        if success:
            print("\n[sucesso] todos os testes passaram!")
            sys.exit(0)
        else:
            print("\n[falha] alguns testes falharam")
            sys.exit(1)

if __name__ == "__main__":
    main()

