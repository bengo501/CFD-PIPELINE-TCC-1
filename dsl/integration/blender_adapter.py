#!/usr/bin/env python3
"""
adaptador para integrar params.json com scripts do blender
le params.json e converte para parametros dos scripts blender
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

class BlenderAdapter:
    """adaptador params.json -> blender scripts"""
    
    def __init__(self, params_file: str):
        """
        inicializa adaptador com arquivo params.json
        
        args:
            params_file: caminho para params.json
        """
        self.params_file = params_file
        self.params = self._load_params()
    
    def _load_params(self) -> Dict[str, Any]:
        """carrega parametros do arquivo json"""
        try:
            with open(self.params_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"erro ao carregar {self.params_file}: {e}")
    
    def get_bed_geometry(self) -> Tuple[float, float, float]:
        """
        retorna parametros da geometria do leito para blender
        
        returns:
            (altura, diametro_externo, espessura_parede)
        """
        bed = self.params['bed']
        return (
            bed['height'],
            bed['diameter'], 
            bed['wall_thickness']
        )
    
    def get_lids_config(self) -> Dict[str, Any]:
        """
        retorna configuracao das tampas
        
        returns:
            dict com configuracao das tampas
        """
        lids = self.params['lids']
        return {
            'top_type': lids['top_type'],
            'bottom_type': lids['bottom_type'],
            'top_thickness': lids['top_thickness'],
            'bottom_thickness': lids['bottom_thickness'],
            'top_position': self.params['bed']['height'] + lids['top_thickness']/2,
            'bottom_position': -lids['bottom_thickness']/2
        }
    
    def get_particles_config(self) -> Dict[str, Any]:
        """
        retorna configuracao das particulas
        
        returns:
            dict com configuracao das particulas
        """
        particles = self.params['particles']
        bed = self.params['bed']
        
        # calcular raio interno do leito
        raio_interno = (bed['diameter'] - 2 * bed['wall_thickness']) / 2
        
        config = {
            'kind': particles['kind'],
            'diameter': particles['diameter'],
            'raio_leito': raio_interno,
            'altura_leito': bed['height'],
            'density': particles['density'],
            'restitution': particles['restitution'],
            'friction': particles['friction'],
            'rolling_friction': particles.get('rolling_friction', 0.1),
            'linear_damping': particles.get('linear_damping', 0.1),
            'angular_damping': particles.get('angular_damping', 0.1),
            'seed': particles['seed']
        }
        
        # quantidade de particulas
        if particles.get('count'):
            config['quantidade'] = particles['count']
        elif particles.get('target_porosity'):
            # calcular quantidade baseada na porosidade
            config['quantidade'] = self._calculate_particle_count()
            config['target_porosity'] = particles['target_porosity']
        else:
            config['quantidade'] = 50  # padrao
        
        return config
    
    def get_packing_config(self) -> Dict[str, Any]:
        """
        retorna configuracao do empacotamento fisico
        
        returns:
            dict com configuracao do empacotamento
        """
        packing = self.params['packing']
        return {
            'method': packing['method'],
            'gravity': packing['gravity'],
            'substeps': packing['substeps'],
            'iterations': packing.get('iterations', 10),
            'damping': packing.get('damping', 0.1),
            'rest_velocity': packing['rest_velocity'],
            'max_time': packing['max_time'],
            'collision_margin': packing.get('collision_margin', 0.001)
        }
    
    def get_export_config(self) -> Dict[str, Any]:
        """
        retorna configuracao de exportacao
        
        returns:
            dict com configuracao de exportacao
        """
        export = self.params['export']
        return {
            'formats': export['formats'],
            'units': export.get('units', 'm'),
            'scale': export.get('scale', 1.0),
            'wall_mode': export.get('wall_mode', 'surface'),
            'fluid_mode': export.get('fluid_mode', 'none'),
            'manifold_check': export.get('manifold_check', True),
            'merge_distance': export.get('merge_distance', 0.0001)
        }
    
    def _calculate_particle_count(self) -> int:
        """
        calcula numero de particulas baseado na porosidade alvo
        
        returns:
            numero estimado de particulas
        """
        bed = self.params['bed']
        particles = self.params['particles']
        
        # volume interno do leito (cilindro)
        raio_interno = (bed['diameter'] - 2 * bed['wall_thickness']) / 2
        volume_leito = 3.14159 * raio_interno**2 * bed['height']
        
        # volume de uma particula (esfera)
        raio_particula = particles['diameter'] / 2
        if particles['kind'] == 'sphere':
            volume_particula = (4/3) * 3.14159 * raio_particula**3
        elif particles['kind'] == 'cube':
            volume_particula = particles['diameter']**3
        else:
            volume_particula = 3.14159 * raio_particula**2 * particles['diameter']  # cilindro
        
        # calcular numero de particulas baseado na porosidade
        porosidade = particles.get('target_porosity', 0.4)
        volume_solido = volume_leito * (1 - porosidade)
        num_particulas = int(volume_solido / volume_particula)
        
        return max(1, num_particulas)  # pelo menos 1 particula
    
    def generate_blender_script(self, template_file: str, output_file: str):
        """
        gera script blender personalizado baseado no template
        
        args:
            template_file: arquivo template do script blender
            output_file: arquivo de saida personalizado
        """
        # ler template
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # obter configuracoes
        altura, diametro, espessura = self.get_bed_geometry()
        particles_config = self.get_particles_config()
        lids_config = self.get_lids_config()
        packing_config = self.get_packing_config()
        
        # substituir parametros no template
        script = template.format(
            altura=altura,
            diametro=diametro,
            espessura_parede=espessura,
            quantidade_particulas=particles_config['quantidade'],
            raio_particula=particles_config['diameter']/2,
            seed=particles_config['seed'],
            gravity=packing_config['gravity'],
            substeps=packing_config['substeps'],
            max_time=packing_config['max_time'],
            rest_velocity=packing_config['rest_velocity']
        )
        
        # salvar script personalizado
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(script)
    
    def print_summary(self):
        """imprime resumo dos parametros carregados"""
        print("=== resumo dos parametros ===")
        
        # geometria
        altura, diametro, espessura = self.get_bed_geometry()
        print(f"leito: {diametro*100:.1f}cm x {altura*100:.1f}cm (espessura: {espessura*1000:.1f}mm)")
        
        # particulas
        particles = self.get_particles_config()
        print(f"particulas: {particles['quantidade']} {particles['kind']}")
        print(f"diametro: {particles['diameter']*1000:.1f}mm")
        print(f"seed: {particles['seed']}")
        
        # fisica
        packing = self.get_packing_config()
        print(f"fisica: {packing['substeps']} substeps, {packing['max_time']}s max")
        print(f"gravidade: {packing['gravity']} m/s²")
        
        # exportacao
        export = self.get_export_config()
        print(f"exportacao: {', '.join(export['formats'])}")
        print(f"modo: {export['wall_mode']}/{export['fluid_mode']}")

def main():
    """funcao principal de teste do adaptador"""
    if len(sys.argv) != 2:
        print("uso: python blender_adapter.py <params.json>")
        return 1
    
    params_file = sys.argv[1]
    
    try:
        # carregar adaptador
        adapter = BlenderAdapter(params_file)
        
        # mostrar resumo
        adapter.print_summary()
        
        print(f"\nadaptador carregado com sucesso: {params_file}")
        return 0
        
    except Exception as e:
        print(f"erro: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
