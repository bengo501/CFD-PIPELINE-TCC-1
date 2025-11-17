#!/usr/bin/env python3
"""
teste do pipeline completo
"""
import requests
import json

# dados de teste
test_data = {
    "bed": {
        "diameter": "0.05",
        "height": "0.1", 
        "wall_thickness": "0.002",
        "clearance": "0.01",
        "material": "steel",
        "roughness": "0.0"
    },
    "lids": {
        "top_type": "flat",
        "bottom_type": "flat",
        "top_thickness": "0.003",
        "bottom_thickness": "0.003",
        "seal_clearance": "0.001"
    },
    "particles": {
        "kind": "sphere",
        "diameter": "0.005",
        "count": "100",
        "target_porosity": "0.4",
        "density": "2500.0",
        "mass": "0.0",
        "restitution": "0.3",
        "friction": "0.5",
        "rolling_friction": "0.1",
        "linear_damping": "0.1",
        "angular_damping": "0.1",
        "seed": "42"
    },
    "packing": {
        "method": "rigid_body",
        "gravity": "-9.81",
        "substeps": "10",
        "iterations": "10",
        "damping": "0.1",
        "rest_velocity": "0.01",
        "max_time": "5.0",
        "collision_margin": "0.001"
    },
    "export": {
        "formats": ["stl_binary", "blend"],
        "units": "m",
        "scale": "1.0",
        "wall_mode": "surface",
        "fluid_mode": "none",
        "manifold_check": True,
        "merge_distance": "0.001"
    },
    "cfd": {
        "solver": "simpleFoam",
        "turbulence": "kEpsilon",
        "convergence": 1e-6,
        "max_iterations": 1000
    }
}

def test_pipeline():
    """testar pipeline completo"""
    print("🧪 testando pipeline completo...")
    
    # 1. verificar status da api
    print("\n1. verificando status da api...")
    try:
        response = requests.get("http://localhost:3000/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ api: {status['api']}")
            print(f"✅ bed_compiler: {status['services']['bed_compiler']}")
            print(f"✅ blender: {status['services']['blender']}")
            print(f"✅ openfoam: {status['services']['openfoam']}")
        else:
            print(f"❌ erro ao verificar status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ erro de conexão: {e}")
        return False
    
    # 2. testar endpoint do pipeline
    print("\n2. testando endpoint /pipeline/full-simulation...")
    try:
        response = requests.post(
            "http://localhost:3000/api/pipeline/full-simulation",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ pipeline iniciado com sucesso!")
            print(f"✅ job_id: {result['job_id']}")
            print(f"✅ status: {result['status']}")
            print(f"✅ mensagem: {result['message']}")
            return True
        else:
            print(f"❌ erro no endpoint: {response.status_code}")
            print(f"❌ resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ erro ao chamar endpoint: {e}")
        return False

if __name__ == "__main__":
    success = test_pipeline()
    if success:
        print("\n🎉 teste do pipeline concluído com sucesso!")
    else:
        print("\n💥 teste do pipeline falhou!")
