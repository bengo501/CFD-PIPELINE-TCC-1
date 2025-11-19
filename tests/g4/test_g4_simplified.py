"""
Versão Simplificada dos Testes G4
Usa a API do pipeline completo diretamente
"""

import asyncio
import json
import time
import hashlib
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import requests
import sys

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class G4TestSimplified:
    """Versão simplificada dos testes G4 usando API do pipeline completo"""
    
    def __init__(self, api_url: str = "http://localhost:8000", output_dir: Path = None):
        self.api_url = api_url
        self.output_dir = output_dir or project_root / "tests" / "g4" / "results"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_dir = self.output_dir / "runs"
        self.results_dir.mkdir(exist_ok=True)
        
        self.metrics_file = self.output_dir / "g4_metrics.csv"
        self.report_file = self.output_dir / "g4_report.txt"
        
        self.results: List[Dict] = []
        
    def generate_hash(self, case_name: str, params: dict) -> str:
        """Gera hash único para execução"""
        params_str = json.dumps(params, sort_keys=True)
        hash_input = f"{case_name}_{params_str}_{datetime.now().isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def bed_to_params(self, bed_content: str) -> dict:
        """Converte conteúdo .bed para formato BedParametersNested da API"""
        # Formato esperado: estrutura aninhada conforme BedParametersNested
        # Valores devem ser números (não strings)
        
        # Valores padrão
        params = {
            "bed": {
                "diameter": 0.05,
                "height": 0.1,
                "wall_thickness": 0.002
            },
            "lids": {
                "lid_top": "flat",
                "lid_bottom": "flat",
                "lid_thickness": 0.003
            },
            "particles": {
                "particle_count": 100,
                "particle_type": "sphere",
                "particle_diameter": 0.005
            },
            "packing": {
                "packing_method": "rigid_body",
                "gravity": -9.81,
                "friction": 0.5,
                "substeps": 10
            },
            "export": {
                "formats": ["blend", "stl"]
            },
            "cfd": {
                "cfd_regime": "laminar",
                "inlet_velocity": 0.1,
                "fluid_density": 1000.0,
                "fluid_viscosity": 0.001
            },
        }
        
        # Parsear valores do bed_content
        lines = bed_content.split('\n')
        current_section = None
        
        for line in lines:
            line_orig = line
            line = line.strip()
            
            # Detectar seção
            if line.startswith('bed {'):
                current_section = 'bed'
                continue
            elif line.startswith('lids {'):
                current_section = 'lids'
                continue
            elif line.startswith('particles {'):
                current_section = 'particles'
                continue
            elif line.startswith('packing {'):
                current_section = 'packing'
                continue
            elif line.startswith('export {'):
                current_section = 'export'
                continue
            elif line.startswith('cfd {'):
                current_section = 'cfd'
                continue
            elif line == '}' or line.endswith(';}'):
                current_section = None
                continue
            
            # Parsear valores
            if '=' in line and not line.startswith('//') and current_section:
                try:
                    # Remover comentários da linha antes de processar
                    if '//' in line:
                        line = line[:line.index('//')]
                    
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().rstrip(';').strip()
                    
                    # Remover comentários do valor (caso ainda existam)
                    if '//' in value:
                        value = value[:value.index('//')].strip()
                    
                    # Remover unidades (cuidado com ordem: m/s2 antes de m/s antes de m)
                    value_clean = value
                    # Remover unidades na ordem correta (mais específicas primeiro)
                    units_to_remove = ['kg/m3', 'm/s2', 'Pa.s', 'm/s', 'm']
                    for unit in units_to_remove:
                        if unit in value_clean:
                            value_clean = value_clean.replace(unit, '').strip()
                    
                    # Remover aspas
                    value_clean = value_clean.replace('"', '').replace("'", '').strip()
                    
                    # Se ainda tiver comentário, remover
                    if '//' in value_clean:
                        value_clean = value_clean[:value_clean.index('//')].strip()
                    
                    # Converter para número
                    try:
                        # Tentar converter para número
                        if '.' in value_clean or 'e' in value_clean.lower() or 'E' in value_clean:
                            value_num = float(value_clean)
                        elif value_clean.startswith('-') and len(value_clean) > 1:
                            # Número negativo
                            if '.' in value_clean:
                                value_num = float(value_clean)
                            else:
                                value_num = int(value_clean)
                        else:
                            value_num = int(value_clean)
                        value_final = value_num
                    except (ValueError, AttributeError):
                        # Se não conseguir converter, manter como string
                        value_final = value_clean
                    
                    # Mapear para estrutura
                    if current_section == 'bed':
                        if 'diameter' in key:
                            params["bed"]["diameter"] = value_final
                        elif 'height' in key:
                            params["bed"]["height"] = value_final
                        elif 'wall_thickness' in key:
                            params["bed"]["wall_thickness"] = value_final
                    elif current_section == 'lids':
                        if 'top_type' in key:
                            params["lids"]["lid_top"] = value_final
                        elif 'bottom_type' in key:
                            params["lids"]["lid_bottom"] = value_final
                        elif 'thickness' in key:
                            params["lids"]["lid_thickness"] = value_final
                    elif current_section == 'particles':
                        if 'kind' in key or 'type' in key:
                            params["particles"]["particle_type"] = value_final
                        elif 'diameter' in key:
                            params["particles"]["particle_diameter"] = value_final
                        elif 'count' in key and 'target' not in key:
                            params["particles"]["particle_count"] = value_final
                        elif 'target_porosity' in key:
                            # Para G4-3: remover count se target_porosity presente
                            params["particles"].pop("particle_count", None)
                            params["particles"]["target_porosity"] = value_final
                    elif current_section == 'packing':
                        if 'method' in key:
                            params["packing"]["packing_method"] = value_final
                        elif 'gravity' in key:
                            params["packing"]["gravity"] = value_final
                        elif 'friction' in key and 'rolling' not in key:
                            params["packing"]["friction"] = value_final
                        elif 'substeps' in key:
                            params["packing"]["substeps"] = value_final
                    elif current_section == 'export':
                        if 'formats' in key:
                            # Parsear lista: ["blend", "stl"]
                            formats_str = value_clean.replace('[', '').replace(']', '')
                            formats = [f.strip().replace('"', '').replace("'", '') 
                                     for f in formats_str.split(',')]
                            params["export"]["formats"] = formats
                    elif current_section == 'cfd':
                        if 'regime' in key:
                            params["cfd"]["cfd_regime"] = value_final
                            params["cfd_regime"] = value_final  # Também no nível raiz (bed_service espera aqui)
                        elif 'inlet_velocity' in key:
                            params["cfd"]["inlet_velocity"] = value_final
                            params["inlet_velocity"] = value_final  # Também no nível raiz
                        elif 'fluid_density' in key:
                            params["cfd"]["fluid_density"] = value_final
                            params["fluid_density"] = value_final  # Também no nível raiz
                        elif 'fluid_viscosity' in key:
                            params["cfd"]["fluid_viscosity"] = value_final
                            params["fluid_viscosity"] = value_final  # Também no nível raiz
                except Exception as e:
                    # Ignorar erros de parsing silenciosamente
                    pass
        
        # Adicionar parâmetros CFD no nível raiz se não existirem (bed_service espera aqui)
        if "cfd" in params and "cfd_regime" not in params:
            params["cfd_regime"] = params["cfd"].get("cfd_regime", "laminar")
            params["inlet_velocity"] = params["cfd"].get("inlet_velocity", 0.1)
            params["fluid_density"] = params["cfd"].get("fluid_density", 1000.0)
            params["fluid_viscosity"] = params["cfd"].get("fluid_viscosity", 0.001)
        
        return params
    
    async def execute_pipeline_via_api(
        self,
        case_name: str,
        bed_content: str,
        hash_id: str
    ) -> Dict:
        """Executa pipeline completo via API"""
        
        result = {
            "case": case_name,
            "hash": hash_id,
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "errors": [],
            "warnings": [],
            "times": {},
            "metrics": {},
            "artifacts": {}
        }
        
        run_dir = self.results_dir / hash_id
        run_dir.mkdir(exist_ok=True)
        
        try:
            # Converter .bed para parâmetros
            params = self.bed_to_params(bed_content)
            
            # Salvar .bed original
            bed_file = run_dir / f"{case_name}.bed"
            bed_file.write_text(bed_content, encoding='utf-8')
            
            # ===== ETAPA 1-5: Pipeline Completo via API =====
            pipeline_start = time.time()
            result["times"]["pipeline_start"] = pipeline_start
            
            # Chamar endpoint do pipeline completo
            print(f"  Iniciando pipeline para {case_name}...")
            print(f"  Enviando parâmetros: {json.dumps(params, indent=2)[:200]}...")  # Debug
            
            try:
                pipeline_response = requests.post(
                    f"{self.api_url}/api/pipeline/full-simulation",
                    json=params,
                    timeout=10
                )
                
                if pipeline_response.status_code != 200:
                    error_detail = pipeline_response.text
                    try:
                        error_json = pipeline_response.json()
                        error_detail = error_json.get("detail", error_detail)
                    except:
                        pass
                    raise Exception(f"Erro ao iniciar pipeline (status {pipeline_response.status_code}): {error_detail}")
            except requests.exceptions.RequestException as e:
                raise Exception(f"Erro de conexão ao iniciar pipeline: {str(e)}")
            
            pipeline_data = pipeline_response.json()
            job_id = pipeline_data.get("job_id")
            
            if not job_id:
                raise Exception("Job ID não retornado")
            
            print(f"  Job ID: {job_id}")
            
            # Aguardar conclusão do pipeline
            print(f"  Aguardando conclusão...")
            job_result = await self._wait_for_pipeline_job(job_id, timeout=3600)
            
            # Extrair resultados
            result["artifacts"] = job_result.get("metadata", {})
            result["artifacts"]["job_id"] = job_id
            result["artifacts"]["output_files"] = job_result.get("output_files", [])
            
            # Extrair tempos dos logs
            logs = job_result.get("logs", [])
            result["warnings"] = [log for log in logs if "warning" in log.lower() or "⚠" in log]
            
            # Calcular tempos (aproximado baseado no progresso)
            progress = job_result.get("progress", 0)
            elapsed = time.time() - pipeline_start
            
            # Distribuir tempo baseado em progresso
            if progress >= 15:
                result["times"]["compile"] = elapsed * 0.15
            if progress >= 40:
                result["times"]["geom"] = elapsed * 0.25
            if progress >= 50:
                result["times"]["mesh"] = elapsed * 0.10
            if progress >= 100:
                result["times"]["solver"] = elapsed * 0.50
            
            result["times"]["total"] = elapsed
            
            # Extrair métricas básicas
            result["metrics"]["progress"] = progress
            result["metrics"]["status"] = job_result.get("status")
            
            # Salvar params.json
            params_file = run_dir / "params.json"
            params_file.write_text(json.dumps(params, indent=2))
            
            # Gerar manifest.json
            manifest = {
                "hash": hash_id,
                "case": case_name,
                "timestamp": result["timestamp"],
                "artifacts": result["artifacts"],
                "metrics": result["metrics"],
                "times": result["times"]
            }
            
            manifest_file = run_dir / "manifest.json"
            manifest_file.write_text(json.dumps(manifest, indent=2))
            
            result["status"] = "completed" if job_result.get("status") == "completed" else "failed"
            
            if result["status"] == "failed":
                result["errors"].append(job_result.get("error_message", "Erro desconhecido"))
            
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            import traceback
            result["errors"].append(traceback.format_exc())
        
        return result
    
    async def _wait_for_pipeline_job(self, job_id: str, timeout: int = 3600) -> Dict:
        """Aguarda conclusão de um job do pipeline completo"""
        start_time = time.time()
        last_progress = 0
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f"{self.api_url}/api/pipeline/job/{job_id}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    job = response.json()
                    status = job.get("status")
                    progress = job.get("progress", 0)
                    
                    # Mostrar progresso
                    if progress != last_progress:
                        print(f"    Progresso: {progress}%")
                        last_progress = progress
                    
                    if status in ["completed", "failed"]:
                        return job
                elif response.status_code == 404:
                    # Tentar endpoint alternativo
                    response = requests.get(
                        f"{self.api_url}/api/job/{job_id}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        job = response.json()
                        if job.get("status") in ["completed", "failed"]:
                            return job
                
            except requests.exceptions.RequestException:
                pass
            
            await asyncio.sleep(3)
        
        raise TimeoutError(f"Job {job_id} não concluiu em {timeout}s")
    
    def save_metrics(self, result: Dict):
        """Salva métricas no CSV"""
        row = {
            "Caso": result["case"],
            "Hash": result["hash"],
            "Data/Hora": result["timestamp"],
            "Status": result["status"],
            "Tempo_Compile": result["times"].get("compile", 0),
            "Tempo_Geom": result["times"].get("geom", 0),
            "Tempo_Mesh": result["times"].get("mesh", 0),
            "Tempo_Solver": result["times"].get("solver", 0),
            "Tempo_Total": result["times"].get("total", 0),
            "Progresso": result["metrics"].get("progress", 0),
            "Erros": len(result.get("errors", [])),
            "Avisos": len(result.get("warnings", []))
        }
        
        # Adicionar ao CSV
        file_exists = self.metrics_file.exists()
        with open(self.metrics_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    
    def generate_report(self):
        """Gera relatório final"""
        report = []
        report.append("=" * 80)
        report.append("CONJUNTO G4 - RELATÓRIO DE TESTES")
        report.append("=" * 80)
        report.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for result in self.results:
            report.append(f"\nCaso: {result['case']}")
            report.append(f"Hash: {result['hash']}")
            report.append(f"Status: {result['status']}")
            report.append(f"Tempo Total: {result['times'].get('total', 0):.2f}s")
            report.append(f"Progresso: {result['metrics'].get('progress', 0)}%")
            
            if result['errors']:
                report.append(f"Erros: {len(result['errors'])}")
                for error in result['errors'][:3]:  # Mostrar apenas 3 primeiros
                    report.append(f"  - {error[:100]}...")
            
            if result['warnings']:
                report.append(f"Avisos: {len(result['warnings'])}")
            
            report.append("-" * 80)
        
        report_text = "\n".join(report)
        self.report_file.write_text(report_text, encoding='utf-8')
        print("\n" + report_text)


async def main():
    """Executa suite completa de testes G4"""
    suite = G4TestSimplified()
    
    print("=" * 80)
    print("CONJUNTO G4 - TESTES AUTOMATIZADOS (Versão Simplificada)")
    print("=" * 80)
    print()
    
    # Verificar se API está online
    try:
        # Tentar vários endpoints possíveis
        endpoints_to_try = [
            f"{suite.api_url}/health",
            f"{suite.api_url}/api/status",
            f"{suite.api_url}/docs"  # Swagger sempre existe
        ]
        
        backend_online = False
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(endpoint, timeout=2)
                if response.status_code in [200, 404]:  # 404 também indica que servidor está rodando
                    backend_online = True
                    break
            except:
                continue
        
        if not backend_online:
            print("❌ Backend não está respondendo!")
            print(f"   Certifique-se de que o backend está rodando em {suite.api_url}")
            print(f"   Tente: cd backend && .\\EXECUTAR.bat")
            return
        print("✓ Backend está online")
    except Exception as e:
        print("❌ Não foi possível conectar ao backend!")
        print(f"   Certifique-se de que o backend está rodando em {suite.api_url}")
        print(f"   Erro: {e}")
        return
    
    # Carregar casos de teste
    cases_dir = Path(__file__).parent / "cases"
    
    # G4-1: Caso base
    print("\n[G4-1] Executando caso base monodisperso laminar...")
    g4_1_bed = (cases_dir / "g4_1_base.bed").read_text(encoding='utf-8')
    hash_1 = suite.generate_hash("G4-1", {"inlet_U": 0.1})
    result_1 = await suite.execute_pipeline_via_api("G4-1", g4_1_bed, hash_1)
    suite.results.append(result_1)
    suite.save_metrics(result_1)
    print(f"  ✓ Hash: {hash_1}, Status: {result_1['status']}")
    
    # G4-2: Varredura de velocidade (executar 3 vezes)
    print("\n[G4-2] Executando varredura de velocidade...")
    velocities = [0.05, 0.10, 0.15]
    for v in velocities:
        g4_2_bed = (cases_dir / "g4_2_velocity_sweep.bed").read_text(encoding='utf-8')
        g4_2_bed = g4_2_bed.replace("{{INLET_U}}", str(v))
        hash_2 = suite.generate_hash("G4-2", {"inlet_U": v})
        result_2 = await suite.execute_pipeline_via_api("G4-2", g4_2_bed, hash_2)
        suite.results.append(result_2)
        suite.save_metrics(result_2)
        print(f"  ✓ Velocidade: {v} m/s, Hash: {hash_2}, Status: {result_2['status']}")
    
    # G4-3: Exclusividade
    print("\n[G4-3] Executando teste de exclusividade...")
    g4_3_bed = (cases_dir / "g4_3_porosity.bed").read_text(encoding='utf-8')
    hash_3 = suite.generate_hash("G4-3", {"target_porosity": 0.40})
    result_3 = await suite.execute_pipeline_via_api("G4-3", g4_3_bed, hash_3)
    suite.results.append(result_3)
    suite.save_metrics(result_3)
    print(f"  ✓ Hash: {hash_3}, Status: {result_3['status']}")
    
    # G4-4: RANS
    print("\n[G4-4] Executando teste RANS com y+...")
    g4_4_bed = (cases_dir / "g4_4_rans.bed").read_text(encoding='utf-8')
    hash_4 = suite.generate_hash("G4-4", {"regime": "turbulent_rans", "yplus_target": 30})
    result_4 = await suite.execute_pipeline_via_api("G4-4", g4_4_bed, hash_4)
    suite.results.append(result_4)
    suite.save_metrics(result_4)
    print(f"  ✓ Hash: {hash_4}, Status: {result_4['status']}")
    
    # Gerar relatório
    print("\n" + "=" * 80)
    print("Gerando relatório final...")
    suite.generate_report()
    
    print(f"\n✓ Métricas salvas em: {suite.metrics_file}")
    print(f"✓ Relatório salvo em: {suite.report_file}")
    print(f"✓ Resultados em: {suite.results_dir}")


if __name__ == "__main__":
    asyncio.run(main())

