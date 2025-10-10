#!/usr/bin/env python3
"""
teste de integração backend + postgresql

testa fluxo completo:
1. criar leito no banco
2. listar leitos
3. criar simulação
4. atualizar simulação
5. criar resultados
6. consultar estatísticas
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"


def test_connection():
    """testa se api está rodando"""
    print("1. testando conexão com api...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        health = response.json()
        
        print(f"   status: {health['status']}")
        print(f"   database: {health['services'].get('database', 'unknown')}")
        
        if health['services'].get('database') != 'connected':
            print("   [AVISO] banco de dados não está conectado!")
            return False
        
        print("   [OK] api está rodando e banco conectado!\n")
        return True
    except Exception as e:
        print(f"   [ERRO] não foi possível conectar: {e}\n")
        return False


def test_create_bed():
    """testa criação de leito"""
    print("2. criando leito no banco de dados...")
    
    bed_data = {
        "name": "leito_teste_integracao",
        "description": "leito criado durante teste de integração",
        "diameter": 0.05,
        "height": 0.1,
        "wall_thickness": 0.002,
        "particle_count": 500,
        "particle_diameter": 0.005,
        "particle_kind": "sphere",
        "packing_method": "rigid_body",
        "porosity": 0.42,
        "parameters_json": {
            "diameter": 0.05,
            "height": 0.1,
            "particle_count": 500
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/beds", json=bed_data)
        response.raise_for_status()
        bed = response.json()
        
        print(f"   [OK] leito criado!")
        print(f"   id: {bed['id']}")
        print(f"   nome: {bed['name']}")
        print(f"   diametro: {bed['diameter']}m")
        print(f"   altura: {bed['height']}m\n")
        
        return bed['id']
    except Exception as e:
        print(f"   [ERRO] falha ao criar leito: {e}\n")
        return None


def test_list_beds():
    """testa listagem de leitos"""
    print("3. listando leitos...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/beds", params={"per_page": 5})
        response.raise_for_status()
        result = response.json()
        
        print(f"   [OK] encontrados {result['total']} leitos")
        print(f"   pagina {result['page']} de {result['pages']}\n")
        
        for bed in result['items'][:3]:
            print(f"   - {bed['name']} (id: {bed['id']})")
        
        print()
        return True
    except Exception as e:
        print(f"   [ERRO] falha ao listar: {e}\n")
        return False


def test_create_simulation(bed_id):
    """testa criação de simulação"""
    print(f"4. criando simulação para leito {bed_id}...")
    
    sim_data = {
        "bed_id": bed_id,
        "name": f"sim_teste_{bed_id}",
        "description": "simulação de teste",
        "regime": "laminar",
        "inlet_velocity": 0.01,
        "fluid_density": 1000.0,
        "fluid_viscosity": 0.001,
        "solver": "simpleFoam",
        "max_iterations": 1000,
        "convergence_criteria": 0.0001
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/simulations", json=sim_data)
        response.raise_for_status()
        simulation = response.json()
        
        print(f"   [OK] simulação criada!")
        print(f"   id: {simulation['id']}")
        print(f"   nome: {simulation['name']}")
        print(f"   status: {simulation['status']}\n")
        
        return simulation['id']
    except Exception as e:
        print(f"   [ERRO] falha ao criar simulação: {e}\n")
        return None


def test_update_simulation(sim_id):
    """testa atualização de simulação"""
    print(f"5. atualizando simulação {sim_id} com resultados...")
    
    update_data = {
        "status": "completed",
        "progress": 100,
        "pressure_drop": 1250.5,
        "average_velocity": 0.012,
        "reynolds_number": 3542.8,
        "execution_time": 120.5
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}/api/simulations/{sim_id}",
            json=update_data
        )
        response.raise_for_status()
        simulation = response.json()
        
        print(f"   [OK] simulação atualizada!")
        print(f"   status: {simulation['status']}")
        print(f"   perda de carga: {simulation['pressure_drop']} Pa")
        print(f"   reynolds: {simulation['reynolds_number']}\n")
        
        return True
    except Exception as e:
        print(f"   [ERRO] falha ao atualizar: {e}\n")
        return False


def test_create_results(sim_id):
    """testa criação de resultados"""
    print(f"6. criando resultados para simulação {sim_id}...")
    
    results_data = [
        {
            "simulation_id": sim_id,
            "result_type": "metric",
            "name": "pressure_drop",
            "value": 1250.5,
            "unit": "Pa"
        },
        {
            "simulation_id": sim_id,
            "result_type": "metric",
            "name": "reynolds_number",
            "value": 3542.8,
            "unit": "-"
        },
        {
            "simulation_id": sim_id,
            "result_type": "validation",
            "name": "ergun_comparison",
            "value": 0.95,
            "data_json": {
                "experimental": [1200, 1350, 1500],
                "simulated": [1180, 1320, 1520],
                "deviation": 3.2
            }
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/results/bulk",
            json=results_data
        )
        response.raise_for_status()
        results = response.json()
        
        print(f"   [OK] {len(results)} resultados criados!")
        for result in results:
            print(f"   - {result['name']}: {result.get('value', 'N/A')}")
        
        print()
        return True
    except Exception as e:
        print(f"   [ERRO] falha ao criar resultados: {e}\n")
        return False


def test_statistics():
    """testa consulta de estatísticas"""
    print("7. consultando estatísticas gerais...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats/overview")
        response.raise_for_status()
        stats = response.json()
        
        print(f"   [OK] estatísticas obtidas!")
        print(f"   total leitos: {stats['total_beds']}")
        print(f"   total simulações: {stats['total_simulations']}")
        print(f"   total resultados: {stats['total_results']}")
        print(f"   por status: {stats['simulations_by_status']}\n")
        
        return True
    except Exception as e:
        print(f"   [ERRO] falha ao obter estatísticas: {e}\n")
        return False


def test_bed_summary(bed_id):
    """testa resumo de leito"""
    print(f"8. obtendo resumo do leito {bed_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/beds/{bed_id}/summary")
        response.raise_for_status()
        summary = response.json()
        
        print(f"   [OK] resumo obtido!")
        print(f"   leito: {summary['bed']['name']}")
        print(f"   total simulações: {summary['simulations_count']}")
        print(f"   por status: {summary['simulations_by_status']}")
        
        metrics = summary['average_metrics']
        if metrics['pressure_drop']:
            print(f"   perda de carga média: {metrics['pressure_drop']:.2f} Pa")
        
        print()
        return True
    except Exception as e:
        print(f"   [ERRO] falha ao obter resumo: {e}\n")
        return False


def main():
    """executa todos os testes"""
    print("="*60)
    print("teste de integração backend + postgresql")
    print("="*60)
    print()
    
    # verificar conexão
    if not test_connection():
        print("[ERRO] api não está rodando ou banco desconectado")
        print("\npara iniciar a api, execute:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload")
        print("\npara iniciar o banco, veja: backend/GUIA_SETUP_WINDOWS.md")
        sys.exit(1)
    
    # executar testes
    success = True
    
    # criar leito
    bed_id = test_create_bed()
    if not bed_id:
        success = False
    
    # listar leitos
    if not test_list_beds():
        success = False
    
    # criar simulação (se leito foi criado)
    sim_id = None
    if bed_id:
        sim_id = test_create_simulation(bed_id)
        if not sim_id:
            success = False
    
    # atualizar simulação (se foi criada)
    if sim_id:
        if not test_update_simulation(sim_id):
            success = False
        
        # criar resultados
        if not test_create_results(sim_id):
            success = False
    
    # estatísticas
    if not test_statistics():
        success = False
    
    # resumo do leito
    if bed_id:
        if not test_bed_summary(bed_id):
            success = False
    
    # resultado final
    print("="*60)
    if success:
        print("[OK] todos os testes passaram!")
        print("\nleito criado: id =", bed_id)
        if sim_id:
            print("simulação criada: id =", sim_id)
        print("\nconsulte no banco ou em:")
        print(f"  {BASE_URL}/docs")
    else:
        print("[ERRO] alguns testes falharam")
        print("\nverifique os logs acima e tente novamente")
        sys.exit(1)
    print("="*60)


if __name__ == "__main__":
    main()

