#!/usr/bin/env python3
"""
wizard interativo para criar arquivos .bed
permite ao usuario parametrizar leitos empacotados de duas formas:
1. questionario interativo - usuario responde perguntas passo a passo
2. edicao de template padrao - usuario edita um arquivo template
este wizard gera arquivos .bed que sao compilados pelo antlr
"""

# importar bibliotecas necessarias
import os  # para operacoes do sistema operacional (limpar tela, arquivos)
import sys  # para acessar argumentos e sair do programa
import shutil
import subprocess  # para executar comandos externos (editores, compilador)
import tempfile  # para criar arquivos temporarios
from pathlib import Path  # para trabalhar com caminhos de arquivos
# dict mapeia chave string para valor qualquer
# any aceita qualquer tipo quando o valor e misto
# list sequencia ordenada por exemplo lista de strings do menu
# optional t significa valor do tipo t ou none quando algo e opcional
# tuple par ou tupla fixa por exemplo atalho titulo descricao do menu
from typing import Dict, Any, List, Optional, Tuple

# pasta onde este ficheiro bed wizard py vive normalmente dsl na raiz do repo
_DSL_DIR = Path(__file__).resolve().parent
# raiz do repositorio um nivel acima de dsl usada para achar scripts blender
_REPO_ROOT = _DSL_DIR.parent
# caminho para packed bed science e leito extracao dentro de scripts blender scripts
_BLENDER_SCRIPTS = _REPO_ROOT / "scripts" / "blender_scripts"
# inserir esse caminho no inicio de sys path para importar packed bed science como pacote
if str(_BLENDER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_BLENDER_SCRIPTS))

# ignorar aviso e402 imports apos codigo sao intencionais porque o path vem antes
from packed_bed_science.packing_modes import (
    PACKING_MODE_CHOICES,
    normalize_packing_mode,
)
# carregar json mesclar packing mode raiz e corrigir json compilado
from wizard_json_loader import (
    export_formats_for_blender,
    json_to_wizard_params,
    load_wizard_json,
    normalize_loaded_dict,
    patch_compiled_json_export,
    patch_compiled_json_packing,
)
# listar nomes de templates json e carregar um template por nome
from wizard_template_engine import list_template_names, load_template
from wizard_terminal_ui import make_terminal_ui, rich_available

# fluxo geral do wizard em memoria
# self params guarda bed particles lids packing export cfd como dicts aninhados
# generate bed content transforma self params em texto linguagem bed
# save bed file grava esse texto no disco
# verify and compile chama o antlr que produz um json ao lado do bed
# patch compiled json packing export recoloca gap e formats que a gramatica bed nao suporta
# run blender with json path chama o executavel blender com leito extracao py
# modos spherical packing e hexagonal 3d no blender usam packed bed science sem rigid body
# modo rigid body usa fisica antiga com queda e nao passa pela validacao fechada dos modos cientificos

class BedWizard:
    """classe principal do wizard para criacao de arquivos .bed"""

    # linhas do menu inicial (atalho, titulo, descricao curta)
    MENU_ROWS: List[Tuple[str, str, str]] = [
        ("1", "questionario interativo", "perguntas passo a passo; gera .bed"),
        ("2", "editor de template", "edita um modelo .bed em editor externo"),
        ("3", "modo blender", "apenas modelo 3d (sem cfd)"),
        ("4", "blender interativo", "gera e abre o blender automaticamente"),
        ("5", "pipeline completo", "modelo 3d + caso openfoam + simulacao no wsl"),
        ("6", "ajuda", "resumo dos parametros por secao"),
        ("7", "documentacao", "guia html no navegador"),
        ("8", "sair", "encerrar o wizard"),
        ("9", "testes rapidos (json)", "fixtures _test_*.json + compile / blender"),
    ]
    
    def __init__(self):
        """inicializar wizard com parametros vazios"""
        self.params = {}  # dicionario para armazenar parametros do leito
        self.output_file = None  # nome do arquivo de saida
        self.ui = make_terminal_ui()
        
        # dicionario com informacoes de ajuda para cada parametro
        self.param_help = {
            # secao bed
            'bed.diameter': {
                'desc': 'diametro interno do leito cilindrico',
                'min': 0.01, 'max': 2.0, 'unit': 'm',
                'exemplo': 'leito de 5cm = 0.05m'
            },
            'bed.height': {
                'desc': 'altura total do leito cilindrico',
                'min': 0.01, 'max': 5.0, 'unit': 'm',
                'exemplo': 'leito de 10cm = 0.1m'
            },
            'bed.wall_thickness': {
                'desc': 'espessura da parede do cilindro',
                'min': 0.0001, 'max': 0.1, 'unit': 'm',
                'exemplo': 'parede de 2mm = 0.002m'
            },
            'bed.clearance': {
                'desc': 'espaco livre acima das particulas',
                'min': 0.0, 'max': 1.0, 'unit': 'm',
                'exemplo': 'folga de 1cm = 0.01m'
            },
            'bed.material': {
                'desc': 'material da parede do leito',
                'exemplo': 'steel, aluminum, glass, plastic'
            },
            'bed.roughness': {
                'desc': 'rugosidade da superficie interna',
                'min': 0.0, 'max': 0.01, 'unit': 'm',
                'exemplo': 'superficie lisa = 0.0m'
            },
            # secao lids
            'lids.top_type': {
                'desc': 'formato da tampa superior',
                'exemplo': 'flat (plana), hemispherical (semiesferica), none (sem tampa)'
            },
            'lids.bottom_type': {
                'desc': 'formato da tampa inferior',
                'exemplo': 'flat (plana), hemispherical (semiesferica), none (sem tampa)'
            },
            'lids.top_thickness': {
                'desc': 'espessura da tampa superior',
                'min': 0.0001, 'max': 0.1, 'unit': 'm',
                'exemplo': 'tampa de 3mm = 0.003m'
            },
            'lids.bottom_thickness': {
                'desc': 'espessura da tampa inferior',
                'min': 0.0001, 'max': 0.1, 'unit': 'm',
                'exemplo': 'tampa de 3mm = 0.003m'
            },
            'lids.seal_clearance': {
                'desc': 'folga entre tampa e parede',
                'min': 0.0, 'max': 0.01, 'unit': 'm',
                'exemplo': 'folga de 1mm = 0.001m'
            },
            # secao particles
            'particles.kind': {
                'desc': 'formato geometrico das particulas',
                'exemplo': 'sphere (esfera), cube (cubo), cylinder (cilindro)'
            },
            'particles.diameter': {
                'desc': 'diametro das particulas esfericas',
                'min': 0.0001, 'max': 0.5, 'unit': 'm',
                'exemplo': 'particula de 5mm = 0.005m'
            },
            'particles.count': {
                'desc': 'quantidade total de particulas',
                'min': 1, 'max': 10000, 'unit': '',
                'exemplo': '100 particulas = empacotamento rapido'
            },
            'particles.target_porosity': {
                'desc': 'porosidade desejada (0-1)',
                'min': 0.1, 'max': 0.9, 'unit': '',
                'exemplo': '0.4 = 40% de vazios'
            },
            'particles.density': {
                'desc': 'densidade do material das particulas',
                'min': 100.0, 'max': 20000.0, 'unit': 'kg/m3',
                'exemplo': 'vidro = 2500 kg/m3, aco = 7850 kg/m3'
            },
            'particles.mass': {
                'desc': 'massa individual de cada particula',
                'min': 0.0, 'max': 1000.0, 'unit': 'g',
                'exemplo': '0.0 = calculado automaticamente'
            },
            'particles.restitution': {
                'desc': 'coeficiente de restituicao (quique)',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.0 = sem quique, 1.0 = quique total'
            },
            'particles.friction': {
                'desc': 'coeficiente de atrito entre particulas',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.5 = atrito moderado'
            },
            'particles.rolling_friction': {
                'desc': 'resistencia ao rolamento',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.1 = rolamento facil'
            },
            'particles.linear_damping': {
                'desc': 'amortecimento do movimento linear',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.1 = amortecimento leve'
            },
            'particles.angular_damping': {
                'desc': 'amortecimento da rotacao',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.1 = rotacao com leve resistencia'
            },
            'particles.seed': {
                'desc': 'semente para geracao aleatoria',
                'min': 0, 'max': 99999, 'unit': '',
                'exemplo': '42 = resultado reproduzivel'
            },
            # secao packing
            'packing.method': {
                'desc': 'metodo de simulacao do empacotamento',
                'exemplo': 'rigid_body (corpo rigido com fisica)'
            },
            'packing.gravity': {
                'desc': 'aceleracao da gravidade',
                'min': -50.0, 'max': 50.0, 'unit': 'm/s2',
                'exemplo': 'terra = -9.81 m/s2, lua = -1.62 m/s2'
            },
            'packing.substeps': {
                'desc': 'subdivisoes de cada frame',
                'min': 1, 'max': 100, 'unit': '',
                'exemplo': '10 = boa precisao, 50 = alta precisao'
            },
            'packing.iterations': {
                'desc': 'iteracoes do solver por substep',
                'min': 1, 'max': 100, 'unit': '',
                'exemplo': '10 = boa convergencia'
            },
            'packing.damping': {
                'desc': 'amortecimento global da simulacao',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.1 = sistema estabiliza rapido'
            },
            'packing.rest_velocity': {
                'desc': 'velocidade considerada repouso',
                'min': 0.0001, 'max': 1.0, 'unit': 'm/s',
                'exemplo': '0.01 = particula parada se < 1cm/s'
            },
            'packing.max_time': {
                'desc': 'tempo maximo de simulacao',
                'min': 0.1, 'max': 60.0, 'unit': 's',
                'exemplo': '5.0s = suficiente para empacotamento'
            },
            'packing.collision_margin': {
                'desc': 'margem de deteccao de colisao',
                'min': 0.00001, 'max': 0.01, 'unit': 'm',
                'exemplo': '0.001m = 1mm de margem'
            },
            'packing.gap': {
                'desc': 'folga minima entre superficies das esferas (modos cientificos)',
                'min': 0.0, 'max': 0.01, 'unit': 'm',
                'exemplo': '0.0001m = 0.1 mm entre esferas'
            },
            'packing.random_seed': {
                'desc': 'seed para spherical_packing',
                'min': 0, 'max': 999999, 'unit': '',
                'exemplo': '7 = colocacao reproduzivel'
            },
            'packing.max_placement_attempts': {
                'desc': 'tentativas max. de colocacao aleatoria (spherical_packing)',
                'min': 1000, 'max': 5000000, 'unit': '',
                'exemplo': '200000'
            },
            'packing.strict_validation': {
                'desc': 'se true, falha se geometria invalida ou faltam esferas',
                'exemplo': 'true recomendado para cfd'
            },
            'packing.step_x': {
                'desc': 'passo horizontal da grade hexagonal (vazio = 2*r+gap)',
                'min': 0.00001, 'max': 0.5, 'unit': 'm',
                'exemplo': 'deixe vazio para automatico'
            },
            # secao export
            'export.formats': {
                'desc': 'formatos de arquivo para exportar',
                'exemplo': 'stl_binary, stl_ascii, obj, blend'
            },
            'export.units': {
                'desc': 'unidade de medida na exportacao',
                'exemplo': 'm (metros), cm (centimetros), mm (milimetros)'
            },
            'export.scale': {
                'desc': 'fator de escala na exportacao',
                'min': 0.001, 'max': 1000.0, 'unit': '',
                'exemplo': '1.0 = tamanho original, 1000 = mm para m'
            },
            'export.wall_mode': {
                'desc': 'modo de exportacao da parede',
                'exemplo': 'surface (superficie), solid (solido)'
            },
            'export.fluid_mode': {
                'desc': 'modo de exportacao do fluido',
                'exemplo': 'none (sem fluido), cavity (com cavidade)'
            },
            'export.manifold_check': {
                'desc': 'verificar se malha e manifold',
                'exemplo': 'true = verifica integridade da malha'
            },
            'export.merge_distance': {
                'desc': 'distancia para mesclar vertices',
                'min': 0.0, 'max': 0.1, 'unit': 'm',
                'exemplo': '0.001m = mescla vertices proximos'
            },
            # secao cfd
            'cfd.regime': {
                'desc': 'regime de escoamento do fluido',
                'exemplo': 'laminar (baixa velocidade), turbulent_rans (alta velocidade)'
            },
            'cfd.inlet_velocity': {
                'desc': 'velocidade do fluido na entrada',
                'min': 0.001, 'max': 100.0, 'unit': 'm/s',
                'exemplo': '0.1 m/s = escoamento lento'
            },
            'cfd.fluid_density': {
                'desc': 'densidade do fluido',
                'min': 0.1, 'max': 2000.0, 'unit': 'kg/m3',
                'exemplo': 'ar = 1.225 kg/m3, agua = 1000 kg/m3'
            },
            'cfd.fluid_viscosity': {
                'desc': 'viscosidade dinamica do fluido',
                'min': 1e-6, 'max': 1.0, 'unit': 'Pa.s',
                'exemplo': 'ar = 1.8e-5 Pa.s, agua = 1e-3 Pa.s'
            },
            'cfd.max_iterations': {
                'desc': 'numero maximo de iteracoes',
                'min': 10, 'max': 100000, 'unit': '',
                'exemplo': '1000 = simulacao rapida, 10000 = precisa'
            },
            'cfd.convergence_criteria': {
                'desc': 'criterio de convergencia (residuo)',
                'min': 1e-10, 'max': 1e-2, 'unit': '',
                'exemplo': '1e-6 = convergencia boa'
            },
            'cfd.write_fields': {
                'desc': 'salvar campos de velocidade/pressao',
                'exemplo': 'true = salva resultados, false = nao salva'
            }
        }
        
    def clear_screen(self):
        """limpar tela do terminal para melhor visualizacao"""
        self.ui.clear()
    
    def print_header(self, title: str, subtitle: str = ""):
        """imprimir cabecalho formatado com titulo"""
        self.ui.header(title, subtitle)
    
    def print_section(self, title: str):
        """imprimir titulo de secao formatado"""
        self.ui.section(title)
    
    def show_param_help(self, param_key: str):
        """mostrar ajuda detalhada sobre um parametro"""
        if param_key in self.param_help:
            info = self.param_help[param_key]
            lines = [f"descricao: {info['desc']}"]
            if 'min' in info and 'max' in info:
                unit = info.get('unit', '')
                lines.append(f"range: minimo {info['min']}{unit} — maximo {info['max']}{unit}")
            if 'exemplo' in info:
                lines.append(f"exemplo: {info['exemplo']}")
            self.ui.param_help(lines)
    
    def get_input(self, prompt: str, default: str = "", required: bool = True) -> str:
        """obter entrada de texto do usuario com validacao"""
        while True:
            # formatar prompt com valor padrao se disponivel
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "
            
            # obter entrada do usuario (nao remover espacos ainda)
            value = self.ui.ask_line(full_prompt)
            
            # se for apenas espacos ou vazio e houver padrao, usar padrao
            if not value.strip() and default:
                return default
            
            # remover espacos para validacao
            value = value.strip()
            
            # validar entrada
            if value:
                return value  # retornar valor se fornecido
            elif default and not required:
                return default  # retornar padrao se nao obrigatorio
            elif not required:
                return ""  # retornar vazio se nao obrigatorio
            else:
                self.ui.warn("campo obrigatorio!")
    
    def get_number_input(self, prompt: str, default: str = "", unit: str = "", required: bool = True, param_key: str = "") -> str:
        """obter entrada numerica com unidade e validacao"""
        # mostrar ajuda se disponivel
        if param_key and param_key in self.param_help:
            self.show_param_help(param_key)
        
        # obter limites se disponivel
        min_val = None
        max_val = None
        if param_key and param_key in self.param_help:
            info = self.param_help[param_key]
            min_val = info.get('min')
            max_val = info.get('max')
        
        while True:
            # formatar prompt com valor padrao e unidade se disponivel
            if default:
                full_prompt = f"{prompt} [{default} {unit}] (? para ajuda): "
            else:
                full_prompt = f"{prompt} ({unit}) (? para ajuda): "
            
            # obter entrada do usuario (nao remover espacos ainda)
            value = self.ui.ask_line(full_prompt)
            
            # verificar se usuario quer ajuda
            if value.strip() == '?':
                if param_key:
                    self.show_param_help(param_key)
                else:
                    self.ui.hint("ajuda nao disponivel para este parametro")
                continue
            
            # se for apenas espacos ou vazio e houver padrao, usar padrao
            if not value.strip() and default:
                return default
            
            # remover espacos para validacao
            value = value.strip()
            
            # validar entrada
            if value:
                try:
                    # tentar converter para float para validar se e numero
                    num_value = float(value)
                    
                    # validar limites se especificados
                    if min_val is not None and num_value < min_val:
                        self.ui.warn(f"valor muito baixo! minimo: {min_val}{unit}")
                        continue
                    if max_val is not None and num_value > max_val:
                        self.ui.warn(f"valor muito alto! maximo: {max_val}{unit}")
                        continue
                    
                    return value  # retornar valor se valido
                except ValueError:
                    self.ui.warn("digite um numero valido!")
                    continue
            elif default and not required:
                return default  # retornar padrao se nao obrigatorio
            elif not required:
                return ""  # retornar vazio se nao obrigatorio
            else:
                self.ui.warn("campo obrigatorio!")
    
    def get_choice(self, prompt: str, options: List[str], default: int = 0) -> str:
        """obter escolha do usuario de uma lista de opcoes"""
        return self.ui.pick_from_list(prompt, options, default)
    
    def get_boolean(self, prompt: str, default: bool = True) -> bool:
        """obter entrada booleana (sim/nao) do usuario"""
        return self.ui.confirm(prompt, default)
    
    def get_list_input(self, prompt: str, separator: str = ",") -> List[str]:
        """obter entrada de lista separada por delimitador"""
        value = self.ui.ask_line(f"{prompt} (separado por '{separator}'): ").strip()
        if value:
            # dividir string pelo separador e remover espacos de cada item
            return [item.strip() for item in value.split(separator)]
        return []  # retornar lista vazia se nao digitou nada
    
    def _collect_packing_params(self, with_param_help: bool = False) -> Dict[str, Any]:
        # pergunta ao utilizador qual dos tres modos usar e recolhe campos extra
        # with param help true liga textos de ajuda ricos nos campos numericos do modo blender
        # with param help false usa questionario simples sem chaves param help
        # ph e uma funcao que ou devolve a chave de ajuda ou string vazia
        # primeiro bloco gravidade substeps etc serve para rigid body e fica no dict mesmo nos modos cientificos
        # segundo bloco gap random seed tentativas strict so para spherical packing
        # terceiro bloco gap step x strict so para hexagonal 3d
        opts = list(PACKING_MODE_CHOICES)
        ph = (lambda k: k) if with_param_help else (lambda _k: "")
        self.print_section("empacotamento")
        method_raw = self.get_choice("metodo de empacotamento", opts, 0)
        method = normalize_packing_mode(method_raw)
        pack: Dict[str, Any] = {
            "method": method,
            "gravity": self.get_number_input("gravidade", "-9.81", "m/s2", True, ph("packing.gravity")),
            "substeps": int(self.get_number_input("sub-passos de simulacao", "10", "", False, ph("packing.substeps"))),
            "iterations": int(self.get_number_input("iteracoes", "10", "", False, ph("packing.iterations"))),
            "damping": self.get_number_input("amortecimento", "0.1", "", False, ph("packing.damping")),
            "rest_velocity": self.get_number_input("velocidade de repouso", "0.01", "m/s", False, ph("packing.rest_velocity")),
            "max_time": self.get_number_input("tempo maximo", "5.0", "s", False, ph("packing.max_time")),
            "collision_margin": self.get_number_input("margem de colisao", "0.001", "m", False, ph("packing.collision_margin")),
        }
        if method == "spherical_packing":
            pack["gap"] = float(self.get_number_input("gap entre esferas", "0.0001", "m", False, ph("packing.gap")))
            pack["random_seed"] = int(self.get_number_input("random_seed", "42", "", False, ph("packing.random_seed")))
            pack["max_placement_attempts"] = int(self.get_number_input("max tentativas colocacao", "500000", "", False, ph("packing.max_placement_attempts")))
            sv = self.get_boolean("strict_validation (falhar se invalido)?", True)
            pack["strict_validation"] = sv
        elif method == "hexagonal_3d":
            pack["gap"] = float(self.get_number_input("gap entre esferas", "0.0001", "m", False, ph("packing.gap")))
            step_raw = self.get_number_input("step_x grade hex (vazio=auto)", "", "m", False, ph("packing.step_x"))
            if step_raw.strip():
                pack["step_x"] = float(step_raw)
            sv = self.get_boolean("strict_validation (falhar se invalido)?", True)
            pack["strict_validation"] = sv
        return pack
    
    def _fill_params_from_questionnaire(self) -> None:
        """preenche self.params com todas as secoes do questionario (sem nome de arquivo nem salvar)."""
        # secao bed - parametros geometricos do leito
        self.print_section("geometria do leito")
        self.params['bed'] = {
            'diameter': self.get_number_input("diametro do leito", "0.05", "m"),
            'height': self.get_number_input("altura do leito", "0.1", "m"),
            'wall_thickness': self.get_number_input("espessura da parede", "0.002", "m"),
            'clearance': self.get_number_input("folga superior", "0.01", "m"),
            'material': self.get_input("material da parede", "steel"),
            'roughness': self.get_number_input("rugosidade", "0.0", "m", False)
        }
        
        # secao lids - parametros das tampas do leito
        self.print_section("tampas")
        lid_types = ["flat", "hemispherical", "none"]  # tipos de tampa disponiveis
        self.params['lids'] = {
            'top_type': self.get_choice("tipo da tampa superior", lid_types),
            'bottom_type': self.get_choice("tipo da tampa inferior", lid_types),
            'top_thickness': self.get_number_input("espessura tampa superior", "0.003", "m"),
            'bottom_thickness': self.get_number_input("espessura tampa inferior", "0.003", "m"),
            'seal_clearance': self.get_number_input("folga do selo", "0.001", "m", False)
        }
        
        # secao particles - parametros das particulas do leito
        self.print_section("particulas")
        particle_kinds = ["sphere", "cube", "cylinder"]  # formas de particulas disponiveis
        self.params['particles'] = {
            'kind': self.get_choice("tipo de particula", particle_kinds),
            'diameter': self.get_number_input("diametro das particulas", "0.005", "m"),
            'count': int(self.get_number_input("numero de particulas", "100", "", True)),
            'target_porosity': self.get_number_input("porosidade alvo", "0.4", "", False),
            'density': self.get_number_input("densidade do material", "2500.0", "kg/m3"),
            'mass': self.get_number_input("massa das particulas", "0.0", "g", False),
            'restitution': self.get_number_input("coeficiente de restituicao", "0.3", "", False),
            'friction': self.get_number_input("coeficiente de atrito", "0.5", "", False),
            'rolling_friction': self.get_number_input("atrito de rolamento", "0.1", "", False),
            'linear_damping': self.get_number_input("amortecimento linear", "0.1", "", False),
            'angular_damping': self.get_number_input("amortecimento angular", "0.1", "", False),
            'seed': int(self.get_number_input("seed para reproducibilidade", "42", "", False))
        }
        
        self.params['packing'] = self._collect_packing_params(with_param_help=False)
        
        # secao export - parametros de exportacao da geometria
        self.print_section("exportacao")
        wall_modes = ["surface", "solid"]  # modos de parede disponiveis
        fluid_modes = ["none", "cavity"]  # modos de fluido disponiveis
        self.params['export'] = {
            'formats': self.get_list_input("formatos de exportacao", ",") or ["stl_binary", "obj"],
            'units': self.get_input("unidades de saida", "m", False),
            'scale': self.get_number_input("escala", "1.0", "", False),
            'wall_mode': self.get_choice("modo da parede", wall_modes),
            'fluid_mode': self.get_choice("modo do fluido", fluid_modes),
            'manifold_check': self.get_boolean("verificar manifold", True),
            'merge_distance': self.get_number_input("distancia de fusao", "0.001", "m", False)
        }
        
        # secao cfd (opcional) - parametros de simulacao de fluidos
        self.print_section("parametros cfd (opcional)")
        if self.get_boolean("incluir parametros cfd?", False):
            cfd_regimes = ["laminar", "turbulent_rans"]  # regimes de escoamento disponiveis
            self.params['cfd'] = {
                'regime': self.get_choice("regime cfd", cfd_regimes),
                'inlet_velocity': self.get_number_input("velocidade de entrada", "0.1", "m/s", False),
                'fluid_density': self.get_number_input("densidade do fluido", "1.225", "kg/m3", False),
                'fluid_viscosity': self.get_number_input("viscosidade do fluido", "1.8e-5", "pa.s", False),
                'max_iterations': int(self.get_number_input("iteracoes maximas", "1000", "", False)),
                'convergence_criteria': self.get_number_input("criterio de convergencia", "1e-6", "", False),
                'write_fields': self.get_boolean("escrever campos", False)
            }
    
    def interactive_questionnaire(self) -> None:
        """apenas coleta parametros (usado pelo pipeline completo, sem salvar .bed aqui)."""
        self._fill_params_from_questionnaire()
    
    def interactive_mode(self):
        """modo questionario interativo - usuario responde perguntas passo a passo"""
        self.clear_screen()
        self.print_header("questionario interativo", "parametrizacao do leito passo a passo")
        self.ui.breadcrumbs("wizard", "questionario")
        self.ui.muted("vamos criar o leito empacotado. use enter para aceitar o valor padrao quando aparecer entre colchetes.")
        self.ui.println()
        self._fill_params_from_questionnaire()
        self.output_file = self.get_input("nome do arquivo de saida", "meu_leito.bed")
        self.confirm_and_save()
    
    def template_mode(self):
        """modo edicao de template - usuario edita um arquivo template padrao"""
        self.clear_screen()
        self.print_header("editor de template", "edicao de modelo .bed")
        self.ui.breadcrumbs("wizard", "template")

        # nomes dos ficheiros json em dsl wizard templates sem extensao
        json_names = list_template_names()
        # se existir pelo menos um template json oferecemos fluxo rapido sem editor externo
        if json_names:
            # usuario escolhe entre carregar json pronto ou cair no editor bed classico
            modo = self.get_choice(
                "origem do template",
                ["ficheiros json em dsl/wizard_templates", "editor .bed classico"],
                0,
            )
            # ramo json carrega dict ja estruturado converte para params do wizard e compila
            if modo.startswith("ficheiros"):
                # pick e o identificador do template por exemplo default spherical
                pick = self.get_choice("template", json_names, 0)
                # data e o dicionario python lido do ficheiro json do template
                data = load_template(pick)
                # normalizar chaves aninhadas e tipos antes de mapear para o wizard
                normalize_loaded_dict(data)
                # self params fica no mesmo formato que o questionario interativo preencheria
                self.params = json_to_wizard_params(data)
                # sugestao de nome troca prefixo default por leito para o bed de saida
                self.output_file = self.get_input(
                    "nome do arquivo de saida", f"{pick.replace('default_', 'leito_')}.bed"
                )
                # grava o texto bed no disco a partir de self params
                self.save_bed_file()
                # se o compilador antlr passar aplicamos patches no json gerado
                if self.verify_and_compile():
                    # jpath e o json compilado ao lado do bed mesmo nome com sufixo json
                    jpath = Path(str(Path(self.output_file).resolve()) + ".json")
                    # recoloca packing mode e campos que a gramatica bed nao serializa
                    patch_compiled_json_packing(jpath, self.params)
                    # recoloca formatos de export pedidos pelo usuario stl obj etc
                    patch_compiled_json_export(jpath, self.params)
                # termina template mode neste fluxo sem abrir editor temporario
                return
        
        # criar template padrao com valores exemplo
        template = self.create_default_template()
        
        # obter nome do arquivo de saida
        self.output_file = self.get_input("nome do arquivo de saida", "meu_leito.bed")
        
        # criar arquivo temporario para edicao
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bed', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(template)  # escrever template no arquivo temporario
            temp_file_path = temp_file.name  # obter caminho do arquivo temporario
        
        self.ui.println()
        self.ui.muted(f"template temporario: {temp_file_path}")
        self.ui.println("editores sugeridos:")
        self.ui.muted("notepad (windows) | nano / vim (linux ou mac) | ou continuar sem editar")
        
        # obter escolha do editor
        editor_choice = self.get_choice("escolha um editor", 
                                      ["notepad", "nano", "vim", "continuar sem editar"], 3)
        
        # abrir editor se escolhido
        if editor_choice != "continuar sem editar":
            try:
                # executar editor com arquivo temporario
                if editor_choice == "notepad":
                    subprocess.run([editor_choice, temp_file_path], check=True)
                else:
                    subprocess.run([editor_choice, temp_file_path], check=True)
            except subprocess.CalledProcessError:
                self.ui.warn(f"erro ao abrir editor {editor_choice}; continuando sem edicao")
            except FileNotFoundError:
                self.ui.warn(f"editor {editor_choice} nao encontrado; continuando sem edicao")
        
        # ler conteudo editado do arquivo temporario
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # limpar arquivo temporario
        os.unlink(temp_file_path)
        
        # salvar arquivo final com conteudo editado
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.ui.ok(f"arquivo salvo: {self.output_file}")
        
        # verificar sintaxe e compilar arquivo
        self.verify_and_compile()
    
    def create_default_template(self) -> str:
        """criar template padrao com valores exemplo para edicao"""
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
        """confirmar parametros configurados e salvar arquivo"""
        self.clear_screen()
        self.print_header("confirmacao", "revise antes de salvar o .bed")
        self.ui.breadcrumbs("wizard", "questionario", "confirmacao")
        self.ui.println("parametros configurados:")
        self.ui.println()
        self.ui.println(f"  leito: {self.params['bed']['diameter']} m x {self.params['bed']['height']} m")
        self.ui.println(f"  particulas: {self.params['particles']['count']} {self.params['particles']['kind']} ({self.params['particles']['diameter']} m)")
        self.ui.println(f"  empacotamento: {self.params['packing']['method']}")
        self.ui.println(f"  exportacao: {', '.join(self.params['export']['formats'])}")
        if 'cfd' in self.params:
            self.ui.println(f"  cfd: {self.params['cfd']['regime']}")
        self.ui.println()
        
        # confirmar se usuario quer salvar
        if self.get_boolean("salvar arquivo .bed?", True):
            self.save_bed_file()
            self.verify_and_compile()
        else:
            self.ui.muted("operacao cancelada.")
    
    def save_bed_file(self):
        """salvar arquivo .bed com conteudo gerado"""
        content = self.generate_bed_content()  # gerar conteudo do arquivo
        
        # escrever arquivo com codificacao utf-8
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.ui.ok(f"arquivo salvo: {self.output_file}")

    def generate_bed_file(self) -> bool:
        # usado pelo pipeline completo e menu de testes rapidos
        # nao mostra confirmacao rica apenas grava e devolve bool
        # parent mkdir garante pastas intermediarias se output bed tiver caminho profundo
        try:
            content = self.generate_bed_content()
            Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except OSError as e:
            self.ui.err(f"falha ao gravar .bed: {e}")
            return False

    def generate_bed_content(self) -> str:
        """gerar conteudo do arquivo .bed a partir dos parametros configurados"""
        lines = ["// arquivo .bed gerado pelo wizard"]
        lines.append("")
        
        # secao bed - parametros geometricos do leito
        lines.append("bed {")
        bed = self.params['bed']
        lines.append(f"    diameter = {bed['diameter']} m;")
        lines.append(f"    height = {bed['height']} m;")
        lines.append(f"    wall_thickness = {bed['wall_thickness']} m;")
        lines.append(f"    clearance = {bed['clearance']} m;")
        lines.append(f"    material = \"{bed['material']}\";")
        # adicionar rugosidade apenas se especificada
        if bed['roughness']:
            lines.append(f"    roughness = {bed['roughness']} m;")
        lines.append("}")
        lines.append("")
        
        # secao lids - parametros das tampas
        lines.append("lids {")
        lids = self.params['lids']
        lines.append(f"    top_type = \"{lids['top_type']}\";")
        lines.append(f"    bottom_type = \"{lids['bottom_type']}\";")
        lines.append(f"    top_thickness = {lids['top_thickness']} m;")
        lines.append(f"    bottom_thickness = {lids['bottom_thickness']} m;")
        # adicionar folga do selo apenas se especificada
        if lids['seal_clearance']:
            lines.append(f"    seal_clearance = {lids['seal_clearance']} m;")
        lines.append("}")
        lines.append("")
        
        # secao particles - parametros das particulas
        lines.append("particles {")
        particles = self.params['particles']
        lines.append(f"    kind = \"{particles['kind']}\";")
        lines.append(f"    diameter = {particles['diameter']} m;")
        lines.append(f"    count = {particles['count']};")
        # adicionar parametros opcionais apenas se especificados
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
        
        # secao packing - parametros do empacotamento fisico
        lines.append("packing {")
        packing = self.params['packing']
        lines.append(f"    method = \"{packing['method']}\";")
        lines.append(f"    gravity = {packing['gravity']} m/s2;")
        # adicionar parametros opcionais apenas se especificados
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
        
        # secao export - parametros de exportacao
        lines.append("export {")
        export = self.params['export']
        # formatar lista de formatos com aspas
        formats_str = ", ".join([f'"{fmt}"' for fmt in export['formats']])
        lines.append(f"    formats = [{formats_str}];")
        # adicionar parametros opcionais apenas se especificados
        if export['units']:
            lines.append(f"    units = \"{export['units']}\";")
        if export['scale']:
            lines.append(f"    scale = {export['scale']};")
        lines.append(f"    wall_mode = \"{export['wall_mode']}\";")
        lines.append(f"    fluid_mode = \"{export['fluid_mode']}\";")
        # converter boolean para string minuscula
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
        print(f"\nverificando arquivo: {self.output_file}")
        
        # verificar se arquivo existe
        if not os.path.exists(self.output_file):
            print(f"  erro: arquivo nao encontrado: {self.output_file}")
            return False
        
        # caminho absoluto: o subprocess do compilador usa cwd=dsl/; paths relativos
        # gravados na raiz do repo nao seriam encontrados sem isso
        bed_abs = str(Path(self.output_file).resolve())
        json_abs = f"{bed_abs}.json"
        
        # tentar compilar com ANTLR
        try:
            result = subprocess.run([
                sys.executable, 
                "compiler/bed_compiler_antlr_standalone.py", 
                bed_abs, 
                "-o", json_abs,
                "-v"
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                print("  sucesso: sintaxe valida!")
                print("  sucesso: compilacao bem-sucedida!")
                print(f"  arquivo json gerado: {json_abs}")
                print(f"  resultado: {result.stdout}")
                return True
            else:
                print("  erro: erro na compilacao:")
                if result.stderr:
                    print(f"  {result.stderr}")
                if result.stdout:
                    print(f"  {result.stdout}")
                return False
                
        except FileNotFoundError:
            print("  aviso: compilador antlr nao encontrado!")
            print("  verifique se o arquivo bed_compiler_antlr_standalone.py existe")
            return False
        except Exception as e:
            print(f"  erro: erro inesperado: {e}")
            return False
    
    def blender_mode(self):
        """modo blender - apenas geracao de modelo 3d sem parametros cfd"""
        self.clear_screen()
        self.print_header("modo blender", "somente modelo 3d (sem cfd)")
        self.ui.breadcrumbs("wizard", "blender")
        self.ui.muted("gera modelo no blender; parametros cfd nao sao pedidos.")
        self.ui.muted("enter aceita padrao; '?' mostra ajuda no campo numerico.")
        self.ui.println()
        
        # secao bed - parametros geometricos do leito
        self.print_section("geometria do leito")
        self.params['bed'] = {
            'diameter': self.get_number_input("diametro do leito", "0.05", "m", True, "bed.diameter"),
            'height': self.get_number_input("altura do leito", "0.1", "m", True, "bed.height"),
            'wall_thickness': self.get_number_input("espessura da parede", "0.002", "m", True, "bed.wall_thickness"),
            'clearance': self.get_number_input("folga superior", "0.01", "m", True, "bed.clearance"),
            'material': self.get_input("material da parede", "steel"),
            'roughness': self.get_number_input("rugosidade", "0.0", "m", False, "bed.roughness")
        }
        
        # secao lids - parametros das tampas do leito
        self.print_section("tampas")
        lid_types = ["flat", "hemispherical", "none"]
        self.params['lids'] = {
            'top_type': self.get_choice("tipo da tampa superior", lid_types),
            'bottom_type': self.get_choice("tipo da tampa inferior", lid_types),
            'top_thickness': self.get_number_input("espessura tampa superior", "0.003", "m", True, "lids.top_thickness"),
            'bottom_thickness': self.get_number_input("espessura tampa inferior", "0.003", "m", True, "lids.bottom_thickness"),
            'seal_clearance': self.get_number_input("folga do selo", "0.001", "m", False, "lids.seal_clearance")
        }
        
        # secao particles - parametros das particulas do leito
        self.print_section("particulas")
        particle_kinds = ["sphere", "cube", "cylinder"]
        self.params['particles'] = {
            'kind': self.get_choice("tipo de particula", particle_kinds),
            'diameter': self.get_number_input("diametro das particulas", "0.005", "m", True, "particles.diameter"),
            'count': int(self.get_number_input("numero de particulas", "100", "", True, "particles.count")),
            'target_porosity': self.get_number_input("porosidade alvo", "0.4", "", False, "particles.target_porosity"),
            'density': self.get_number_input("densidade do material", "2500.0", "kg/m3", True, "particles.density"),
            'mass': self.get_number_input("massa das particulas", "0.0", "g", False, "particles.mass"),
            'restitution': self.get_number_input("coeficiente de restituicao", "0.3", "", False, "particles.restitution"),
            'friction': self.get_number_input("coeficiente de atrito", "0.5", "", False, "particles.friction"),
            'rolling_friction': self.get_number_input("atrito de rolamento", "0.1", "", False, "particles.rolling_friction"),
            'linear_damping': self.get_number_input("amortecimento linear", "0.1", "", False, "particles.linear_damping"),
            'angular_damping': self.get_number_input("amortecimento angular", "0.1", "", False, "particles.angular_damping"),
            'seed': int(self.get_number_input("seed para reproducibilidade", "42", "", False, "particles.seed"))
        }
        
        self.params['packing'] = self._collect_packing_params(with_param_help=True)
        
        # secao export - parametros de exportacao simplificados
        self.print_section("exportacao")
        self.params['export'] = {
            'formats': ["stl_binary", "blend"],  # formatos para blender
            'units': "m",
            'scale': 1.0,
            'wall_mode': "surface",
            'fluid_mode': "none",
            'manifold_check': True,
            'merge_distance': 0.001
        }
        
        # nao incluir secao cfd
        self.ui.hint("secao cfd omitida neste modo")
        
        # obter nome do arquivo de saida
        self.output_file = self.get_input("nome do arquivo de saida", "leito_blender.bed")
        
        # confirmar e processar
        self.confirm_and_generate_blender()
    
    def blender_interactive_mode(self):
        """modo blender interativo - gera modelo e abre blender automaticamente"""
        self.clear_screen()
        self.print_header("blender interativo", "gera e abre o blender automaticamente")
        self.ui.breadcrumbs("wizard", "blender-interativo")
        self.ui.muted("apos gerar, o blender abre para visualizar ou editar.")
        self.ui.muted("enter aceita padrao; '?' ajuda nos campos numericos.")
        self.ui.println()
        
        # usar mesma coleta de parametros do modo blender normal
        # secao bed - parametros geometricos do leito
        self.print_section("geometria do leito")
        self.params['bed'] = {
            'diameter': self.get_number_input("diametro do leito", "0.05", "m", True, "bed.diameter"),
            'height': self.get_number_input("altura do leito", "0.1", "m", True, "bed.height"),
            'wall_thickness': self.get_number_input("espessura da parede", "0.002", "m", True, "bed.wall_thickness"),
            'clearance': self.get_number_input("folga superior", "0.01", "m", True, "bed.clearance"),
            'material': self.get_input("material da parede", "steel"),
            'roughness': self.get_number_input("rugosidade", "0.0", "m", False, "bed.roughness")
        }
        
        # secao lids - parametros das tampas do leito
        self.print_section("tampas")
        lid_types = ["flat", "hemispherical", "none"]
        self.params['lids'] = {
            'top_type': self.get_choice("tipo da tampa superior", lid_types),
            'bottom_type': self.get_choice("tipo da tampa inferior", lid_types),
            'top_thickness': self.get_number_input("espessura tampa superior", "0.003", "m", True, "lids.top_thickness"),
            'bottom_thickness': self.get_number_input("espessura tampa inferior", "0.003", "m", True, "lids.bottom_thickness"),
            'seal_clearance': self.get_number_input("folga do selo", "0.001", "m", False, "lids.seal_clearance")
        }
        
        # secao particles - parametros das particulas do leito
        self.print_section("particulas")
        particle_kinds = ["sphere", "cube", "cylinder"]
        self.params['particles'] = {
            'kind': self.get_choice("tipo de particula", particle_kinds),
            'diameter': self.get_number_input("diametro das particulas", "0.005", "m", True, "particles.diameter"),
            'count': int(self.get_number_input("numero de particulas", "100", "", True, "particles.count")),
            'target_porosity': self.get_number_input("porosidade alvo", "0.4", "", False, "particles.target_porosity"),
            'density': self.get_number_input("densidade do material", "2500.0", "kg/m3", True, "particles.density"),
            'mass': self.get_number_input("massa das particulas", "0.0", "g", False, "particles.mass"),
            'restitution': self.get_number_input("coeficiente de restituicao", "0.3", "", False, "particles.restitution"),
            'friction': self.get_number_input("coeficiente de atrito", "0.5", "", False, "particles.friction"),
            'rolling_friction': self.get_number_input("atrito de rolamento", "0.1", "", False, "particles.rolling_friction"),
            'linear_damping': self.get_number_input("amortecimento linear", "0.1", "", False, "particles.linear_damping"),
            'angular_damping': self.get_number_input("amortecimento angular", "0.1", "", False, "particles.angular_damping"),
            'seed': int(self.get_number_input("seed para reproducibilidade", "42", "", False, "particles.seed"))
        }
        
        self.params['packing'] = self._collect_packing_params(with_param_help=True)
        
        # secao export - parametros de exportacao simplificados
        self.print_section("exportacao")
        self.params['export'] = {
            'formats': ["stl_binary", "blend"],  # formatos para blender
            'units': "m",
            'scale': 1.0,
            'wall_mode': "surface",
            'fluid_mode': "none",
            'manifold_check': True,
            'merge_distance': 0.001
        }
        
        # nao incluir secao cfd
        self.ui.hint("secao cfd omitida neste modo")
        
        # obter nome do arquivo de saida
        self.output_file = self.get_input("nome do arquivo de saida", "leito_interativo.bed")
        
        # confirmar e processar com abertura automatica
        self.confirm_and_generate_blender_interactive()
    
    def confirm_and_generate_blender(self):
        """confirmar parametros e executar geracao no blender"""
        self.clear_screen()
        self.print_header("confirmacao", "geracao 3d no blender")
        self.ui.breadcrumbs("wizard", "blender", "confirmar")
        self.ui.println("resumo:")
        self.ui.muted(f"  leito: {self.params['bed']['diameter']} m x {self.params['bed']['height']} m")
        self.ui.muted(f"  particulas: {self.params['particles']['count']} {self.params['particles']['kind']}")
        self.ui.muted(f"  empacotamento: {self.params['packing']['method']} | export: blend, stl")
        self.ui.println()
        
        if not self.get_boolean("continuar com geracao no blender?", True):
            self.ui.muted("operacao cancelada.")
            return
        
        self.save_bed_file()
        
        self.ui.section("compilando .bed")
        if not self.verify_and_compile():
            self.ui.err("nao foi possivel compilar o arquivo")
            return
        jpath = Path(str(Path(self.output_file).resolve()) + ".json")
        patch_compiled_json_packing(jpath, self.params)
        patch_compiled_json_export(jpath, self.params)

        self.ui.section("executando blender")
        ok, blend_path = self.execute_blender(open_after=False)
        if ok and blend_path and self.get_boolean(
            "gostaria de abrir o blender com o modelo gerado?", False
        ):
            self.open_blender_gui_with_blend(blend_path)
    
    def confirm_and_generate_blender_interactive(self):
        """confirmar parametros, gerar modelo e abrir blender automaticamente"""
        self.clear_screen()
        self.print_header("confirmacao", "geracao 3d + abrir blender")
        self.ui.breadcrumbs("wizard", "blender-interativo", "confirmar")
        self.ui.println("resumo:")
        self.ui.muted(f"  leito: {self.params['bed']['diameter']} m x {self.params['bed']['height']} m")
        self.ui.muted(f"  particulas: {self.params['particles']['count']} {self.params['particles']['kind']}")
        self.ui.muted(f"  empacotamento: {self.params['packing']['method']} | export: blend, stl")
        self.ui.println()
        self.ui.hint("apos gerar, o blender abre automaticamente")
        self.ui.println()
        
        if not self.get_boolean("continuar com geracao e abertura no blender?", True):
            self.ui.muted("operacao cancelada.")
            return
        
        self.save_bed_file()
        
        self.ui.section("compilando .bed")
        if not self.verify_and_compile():
            self.ui.err("nao foi possivel compilar o arquivo")
            return
        jpath = Path(str(Path(self.output_file).resolve()) + ".json")
        patch_compiled_json_packing(jpath, self.params)
        patch_compiled_json_export(jpath, self.params)

        self.ui.section("executando blender")
        success, blend_file = self.execute_blender(open_after=True)
        
        if success:
            self.ui.section("concluido")
            self.ui.ok(f"modelo: {blend_file}")
            self.ui.muted("blender em segundo plano — zoom: scroll; orbita: botao do meio; topo: numpad 7; shading: z")
            self.ui.pause("enter para voltar ao menu...")
    
    def find_blender_executable(self) -> Optional[str]:
        # procura instalacoes tipicas no windows por caminho absoluto
        # se nenhuma existir tenta blender no path via shutil which
        # retorno none significa que run blender with json path vai falhar cedo
        candidates = [
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender\blender.exe",
            r"C:\Steam\steamapps\common\Blender\blender.exe",
        ]
        for path in candidates:
            if Path(path).exists():
                return path
        w = shutil.which("blender")
        return w

    def run_blender_with_json_path(
        self,
        json_file: Path,
        open_after: bool = False,
        formats: Optional[str] = None,
        output_blend: Optional[Path] = None,
    ) -> Tuple[bool, Optional[Path]]:
        # subprocesso blender background python leito extracao py
        # json file e o params json ja com patch de packing cientifico
        # formats string virgula blend stl glb se none le do proprio json export
        # output blend destino do ficheiro principal se none derivado do stem do json
        # open after true chama open blender with file no fim
        # timeout 600 segundos para leitos grandes ou muitas esferas rigid body
        try:
            project_root = Path(__file__).parent.parent
            blender_script = project_root / "scripts" / "blender_scripts" / "leito_extracao.py"
            output_dir = project_root / "generated" / "3d" / "output"
            output_dir.mkdir(parents=True, exist_ok=True)

            json_file = Path(json_file).resolve()
            if output_blend is None:
                stem = json_file.name.replace(".bed.json", "").replace(".json", "")
                output_blend = output_dir / f"{stem}.blend"
            else:
                output_blend = Path(output_blend)

            print(f"script blender: {blender_script}")
            print(f"arquivo json: {json_file}")
            print(f"saida .blend: {output_blend}")

            if not blender_script.exists():
                print(f"erro: script blender nao encontrado: {blender_script}")
                return False, None
            if not json_file.exists():
                print(f"erro: arquivo json nao encontrado: {json_file}")
                return False, None

            blender_exe = self.find_blender_executable()
            if not blender_exe:
                print("erro: blender nao encontrado")
                return False, None

            if formats is None:
                try:
                    import json as _json

                    with open(json_file, "r", encoding="utf-8") as f:
                        d = _json.load(f)
                    formats = export_formats_for_blender(d.get("export") or {})
                except Exception:
                    formats = "blend,stl"

            print(f"blender encontrado: {blender_exe}")
            print(f"formatos: {formats}")
            print("\niniciando geracao do modelo 3d...")

            cmd = [
                blender_exe,
                "--background",
                "--python",
                str(blender_script),
                "--",
                "--params",
                str(json_file),
                "--output",
                str(output_blend),
                "--formats",
                formats,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.stdout:
                print("\nsaida do blender:")
                print(result.stdout)

            if result.returncode == 0 and output_blend.exists():
                print("\nsucesso: modelo 3d gerado!")
                if open_after:
                    print("\nabrindo modelo no blender...")
                    self.open_blender_with_file(blender_exe, output_blend)
                return True, output_blend

            print("\nerro: falha na geracao do modelo")
            print(f"codigo: {result.returncode}")
            if result.stderr:
                print(result.stderr)
            return False, None

        except subprocess.TimeoutExpired:
            print("erro: timeout na execucao do blender (limite: 10 minutos)")
            return False, None
        except Exception as e:
            print(f"erro: {e}")
            return False, None

    def open_blender_gui_with_blend(self, blend_file: Path) -> None:
        # atalho que resolve o executavel outra vez e delega em open blender with file
        exe = self.find_blender_executable()
        if exe:
            self.open_blender_with_file(exe, blend_file)
        else:
            print("aviso: blender nao encontrado para abrir o ficheiro")

    def execute_blender(self, open_after=False):
        # compatibilidade com fluxos antigos que assumem self output file bed
        # o json e sempre output file absoluto mais sufixo json
        # le export do json para montar lista de formatos
        bed_resolved = Path(self.output_file).resolve()
        json_file = Path(str(bed_resolved) + ".json")
        fmt = None
        if json_file.exists():
            try:
                import json as _json

                with open(json_file, "r", encoding="utf-8") as f:
                    fmt = export_formats_for_blender(_json.load(f).get("export") or {})
            except Exception:
                fmt = None
        return self.run_blender_with_json_path(json_file, open_after=open_after, formats=fmt)
    
    def open_blender_with_file(self, blender_exe, blend_file):
        """abrir blender com arquivo especifico em modo gui"""
        try:
            print(f"executando: {blender_exe} {blend_file}")
            
            # abrir blender em modo gui (sem --background)
            # usar Popen para nao bloquear o terminal
            subprocess.Popen([blender_exe, str(blend_file)], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            print("\nsucesso: blender aberto!")
            print("o blender esta rodando em segundo plano")
            print("voce pode fechar esta janela sem afetar o blender")
            
        except Exception as e:
            print(f"\nerro ao abrir blender: {e}")
            print(f"\nabra manualmente executando:")
            print(f"{blender_exe} {blend_file}")
    
    def tests_quick_menu(self) -> None:
        # menu9 do wizard
        # glob test json na pasta python modeling
        # mostra indice nome ficheiro e modo packing lido do json
        # carrega json converte para self params gera bed compila patch
        # pergunta se corre blender e se abre gui no fim
        self.clear_screen()
        self.print_header("testes rapidos", "fixtures em scripts/python_modeling")
        self.ui.breadcrumbs("wizard", "testes")
        fix_dir = _REPO_ROOT / "scripts" / "python_modeling"
        files = sorted(fix_dir.glob("_test_*.json"))
        if not files:
            self.ui.err("nenhum _test_*.json encontrado")
            self.ui.pause()
            return
        self.ui.println("ficheiros disponiveis:")
        for i, p in enumerate(files, 1):
            try:
                d = load_wizard_json(p)
                pm = d.get("packing_mode") or (d.get("packing") or {}).get("method") or "?"
            except OSError:
                pm = "?"
            self.ui.muted(f"  {i}. {p.name}  | modo: {pm}")
        self.ui.println()
        raw = self.ui.ask_line(f"numero (1-{len(files)}) ou 0 voltar: ").strip()
        if raw == "0" or raw == "":
            return
        try:
            idx = int(raw) - 1
            if not (0 <= idx < len(files)):
                raise ValueError
        except ValueError:
            self.ui.warn("escolha invalida")
            self.ui.pause()
            return
        chosen = files[idx]
        data = load_wizard_json(chosen)
        self.params = json_to_wizard_params(data)
        self.output_file = str((Path.cwd() / f"{chosen.stem}.bed").resolve())
        do_blender = self.ui.confirm("executar blender apos compilar?", default=False)
        if not self.generate_bed_file():
            self.ui.err("falha ao gerar .bed")
            self.ui.pause()
            return
        self.ui.section("compilando")
        if not self.verify_and_compile():
            self.ui.err("falha na compilacao")
            self.ui.pause()
            return
        jpath = Path(str(Path(self.output_file).resolve()) + ".json")
        patch_compiled_json_packing(jpath, self.params)
        patch_compiled_json_export(jpath, self.params)
        if do_blender:
            fmt = export_formats_for_blender(self.params.get("export") or {})
            ok, blend = self.run_blender_with_json_path(jpath, open_after=False, formats=fmt)
            if ok and blend and self.ui.confirm(
                "gostaria de abrir o blender com o modelo gerado?", default=False
            ):
                self.open_blender_gui_with_blend(blend)
        else:
            self.ui.ok(f"json pronto: {jpath}")
        self.ui.pause("enter para voltar ao menu...")

    def show_help_menu(self):
        """mostrar menu de ajuda com informacoes sobre parametros"""
        self.clear_screen()
        self.print_header("ajuda", "parametros do arquivo .bed")
        self.ui.breadcrumbs("wizard", "ajuda")
        
        sections = {
            '1': ('bed', 'geometria do leito'),
            '2': ('lids', 'tampas'),
            '3': ('particles', 'particulas'),
            '4': ('packing', 'empacotamento'),
            '5': ('export', 'exportacao'),
            '6': ('cfd', 'simulacao cfd')
        }
        
        entries = [(k, v[1]) for k, v in sections.items()]
        self.ui.render_help_section_menu(entries, back_key="0")
        choice = self.ui.ask_line("opcao (0-6): ").strip()
        
        if choice == '0':
            return
        elif choice in sections:
            section_key, section_desc = sections[choice]
            self.clear_screen()
            self.print_header(f"ajuda: {section_desc}", "detalhes dos campos")
            self.ui.breadcrumbs("wizard", "ajuda", section_key)
            
            for param_key, param_info in sorted(self.param_help.items()):
                if param_key.startswith(f"{section_key}."):
                    param_name = param_key.split('.')[1]
                    lines = [
                        f"parametro: {param_name}",
                        f"descricao: {param_info['desc']}",
                    ]
                    if 'min' in param_info and 'max' in param_info:
                        unit = param_info.get('unit', '')
                        lines.append(f"range: {param_info['min']}{unit} .. {param_info['max']}{unit}")
                    if 'exemplo' in param_info:
                        lines.append(f"exemplo: {param_info['exemplo']}")
                    self.ui.param_help(lines)
            
            self.ui.pause()
            self.show_help_menu()
        else:
            self.ui.warn("opcao invalida")
            self.ui.pause()
            self.show_help_menu()
    
    def pipeline_completo_mode(self):
        """modo pipeline completo - gera modelo 3d, cria caso cfd e executa simulacao"""
        self.clear_screen()
        self.print_header("pipeline completo", "modelagem 3d + caso openfoam + simulacao")
        self.ui.breadcrumbs("wizard", "pipeline")
        self.ui.println("etapas:")
        self.ui.muted("1) .bed + json  2) blender  3) stl  4) caso openfoam  5) simulacao no wsl")
        self.ui.println()
        self.ui.warn("tempo estimado 10-30 min | blender | wsl2 + openfoam | ~2 gb disco")
        self.ui.println()
        
        if not self.ui.confirm("deseja continuar?", default=False):
            self.ui.muted("operacao cancelada")
            return
        
        # usar questionario interativo para coletar parametros
        self.ui.section("etapa 1/5 — parametrizacao do leito")
        self.interactive_questionnaire()
        
        if not self.params:
            self.ui.err("parametros nao definidos")
            return
        
        # gerar arquivo .bed
        self.ui.section("etapa 2/5 — geracao e compilacao do .bed")
        
        output_name = self.ui.ask_line("nome do arquivo .bed (sem extensao) [leito_pipeline]: ").strip()
        if not output_name:
            output_name = "leito_pipeline"
        
        self.output_file = f"{output_name}.bed"
        
        if not self.generate_bed_file():
            self.ui.err("falha ao gerar arquivo .bed")
            return
        
        self.ui.section("compilando .bed")
        if not self.verify_and_compile():
            self.ui.err("falha na compilacao do arquivo .bed")
            return
        json_path = Path(str(Path(self.output_file).resolve()) + ".json")
        patch_compiled_json_packing(json_path, self.params)
        patch_compiled_json_export(json_path, self.params)
        self.ui.ok(f"arquivo compilado: {json_path}")
        
        # gerar modelo 3d no blender
        self.ui.section("etapa 3/5 — modelo 3d no blender")
        fmt = export_formats_for_blender(self.params.get("export") or {})
        success, blend_file = self.run_blender_with_json_path(
            json_path, open_after=False, formats=fmt
        )
        
        if not success:
            self.ui.err("falha na geracao do modelo 3d")
            return
        
        self.ui.ok(f"modelo 3d: {blend_file}")
        
        # criar caso openfoam
        self.ui.section("etapa 4/5 — caso openfoam")
        
        success, case_dir = self.create_openfoam_case(json_path, blend_file)
        if not success:
            self.ui.err("falha na criacao do caso openfoam")
            return
        
        self.ui.ok(f"caso cfd: {case_dir}")
        
        # executar simulacao cfd
        self.ui.section("etapa 5/5 — simulacao cfd")
        
        success = self.run_openfoam_simulation(case_dir)
        if not success:
            self.ui.err("falha na execucao da simulacao cfd")
            return
        
        # resumo final
        self.ui.section("pipeline concluido")
        self.ui.ok("resumo dos artefatos:")
        self.ui.muted(f"  .bed: {self.output_file}")
        self.ui.muted(f"  json: {json_path}")
        self.ui.muted(f"  blend: {blend_file}")
        self.ui.muted(f"  caso: {case_dir}")
        self.ui.println()
        self.ui.muted("proximo passo: paraview — abrir caso.foam no diretorio do caso")
        self.ui.muted(f"  {case_dir / 'caso.foam'}")
        self.ui.pause("enter para voltar ao menu principal...")
    
    def create_openfoam_case(self, json_path, blend_file):
        """
        criar caso openfoam a partir do modelo blender
        
        returns:
            (success, case_dir) - tupla com sucesso e diretorio do caso
        """
        try:
            print("\ncriando caso openfoam...")
            print("  [1/3] validando arquivos de entrada")
            
            # validar arquivos
            json_path = Path(json_path)
            blend_file = Path(blend_file)
            
            if not json_path.exists():
                print(f"  erro: arquivo json nao encontrado: {json_path}")
                return False, None
            
            if not blend_file.exists():
                print(f"  erro: arquivo blend nao encontrado: {blend_file}")
                return False, None
            
            print("  ✓ arquivos validados")
            
            # determinar diretorio de saida
            output_root = Path(__file__).parent.parent / "generated" / "cfd"
            output_root.mkdir(parents=True, exist_ok=True)
            
            # encontrar script de setup
            script_path = Path(__file__).parent.parent / "scripts" / "openfoam_scripts" / "setup_openfoam_case.py"
            
            if not script_path.exists():
                print(f"  erro: script setup_openfoam_case.py nao encontrado")
                print(f"  procurado em: {script_path}")
                return False, None
            
            print(f"  [2/3] executando script de setup do openfoam")
            print(f"  script: {script_path}")
            print(f"  json: {json_path}")
            print(f"  blend: {blend_file}")
            print()
            
            # executar script de setup (sem --run ainda)
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    str(json_path),
                    str(blend_file),
                    "--output-dir", str(output_root)
                ],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            # mostrar saida do comando
            if result.stdout:
                print(result.stdout)
            
            if result.returncode == 0:
                print("  ✓ caso openfoam criado com sucesso")
                
                # determinar diretorio do caso
                case_name = json_path.stem.replace('.bed', '')
                case_dir = output_root / case_name
                
                print(f"  [3/3] caso criado em: {case_dir}")
                
                return True, case_dir
            else:
                print(f"  erro: falha na criacao do caso openfoam")
                print(f"  codigo de erro: {result.returncode}")
                if result.stderr:
                    print(f"  detalhes do erro:")
                    print(result.stderr)
                return False, None
                
        except subprocess.TimeoutExpired:
            print("  erro: timeout na criacao do caso (limite: 5 minutos)")
            return False, None
        except Exception as e:
            print(f"  erro: erro inesperado: {e}")
            return False, None
    
    def run_openfoam_simulation(self, case_dir):
        """
        executar simulacao openfoam no wsl
        
        args:
            case_dir: diretorio do caso openfoam
            
        returns:
            success - boolean indicando sucesso
        """
        try:
            case_dir = Path(case_dir)
            
            if not case_dir.exists():
                print(f"  erro: diretorio do caso nao encontrado: {case_dir}")
                return False
            
            print("\nexecutando simulacao cfd no wsl/ubuntu...")
            print("  ⚠️  este processo pode levar varios minutos")
            print()
            
            # converter caminho windows para wsl
            # C:\Users\... -> /mnt/c/Users/...
            wsl_path = str(case_dir).replace('\\', '/')
            if wsl_path[1] == ':':
                drive = wsl_path[0].lower()
                wsl_path = f"/mnt/{drive}{wsl_path[2:]}"
            
            print(f"  caminho wsl: {wsl_path}")
            print()
            
            # verificar se wsl esta instalado
            print("  [1/4] verificando wsl...")
            result = subprocess.run(
                ["wsl", "--list", "--quiet"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print("  erro: wsl nao esta instalado ou configurado")
                print("  instale o wsl2 com ubuntu e openfoam")
                return False
            
            print("  ✓ wsl detectado")
            
            # executar script Allrun no wsl
            print(f"  [2/4] executando ./Allrun no wsl...")
            print(f"  diretorio: {wsl_path}")
            print()
            
            # comando para executar no wsl
            wsl_command = f"cd '{wsl_path}' && chmod +x Allrun && ./Allrun"
            
            print(f"  comando: {wsl_command}")
            print()
            print("  aguarde... (isto pode levar 10-30 minutos)")
            print("  " + "="*50)
            print()
            
            # executar com output em tempo real
            process = subprocess.Popen(
                ["wsl", "bash", "-c", wsl_command],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # mostrar output em tempo real
            for line in process.stdout:
                print(f"  {line.rstrip()}")
            
            # aguardar conclusao
            return_code = process.wait()
            
            print()
            print("  " + "="*50)
            print()
            
            if return_code == 0:
                print("  [3/4] ✓ simulacao concluida com sucesso")
                
                # verificar se arquivo de resultados existe
                print("  [4/4] verificando resultados...")
                
                # criar arquivo .foam para paraview
                foam_file = case_dir / "caso.foam"
                foam_file.touch()
                
                print(f"  ✓ arquivo paraview criado: {foam_file}")
                print()
                print("  resultados disponiveis em:")
                print(f"  {case_dir}")
                
                return True
            else:
                print(f"  [3/4] erro: simulacao falhou com codigo {return_code}")
                print()
                print("  verifique os logs em:")
                print(f"  {case_dir}/log.*")
                
                return False
                
        except subprocess.TimeoutExpired:
            print("  erro: timeout na verificacao do wsl")
            return False
        except FileNotFoundError:
            print("  erro: comando 'wsl' nao encontrado")
            print("  instale o wsl2 no windows")
            return False
        except Exception as e:
            print(f"  erro: erro inesperado: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_documentation(self):
        """abrir documentacao html completa do projeto"""
        import webbrowser
        
        # obter caminho do arquivo de documentacao
        doc_path = Path(__file__).parent / "documentacao.html"
        
        # verificar se arquivo existe
        if not doc_path.exists():
            self.ui.err("arquivo de documentacao nao encontrado")
            self.ui.muted(f"caminho esperado: {doc_path}")
            self.ui.pause()
            return
        
        self.ui.println("abrindo documentacao no navegador padrao...")
        self.ui.muted(str(doc_path))
        
        try:
            webbrowser.open(f"file://{doc_path.absolute()}")
            self.ui.ok("se o navegador nao abrir, abra manualmente o arquivo acima")
        except Exception as e:
            self.ui.err(f"nao foi possivel abrir o navegador: {e}")
            self.ui.muted(f"abra manualmente: {doc_path}")
        
        self.ui.pause()
    
    def _draw_main_menu(self) -> None:
        """tela inicial estilo navegador (barra + tabela de modos)."""
        self.ui.clear()
        self.ui.header("wizard de parametrizacao", "leitos empacotados — arquivos .bed / antlr / blender / openfoam")
        if not rich_available():
            self.ui.hint("instale rich para cores e tabelas: pip install rich")
            self.ui.println()
        self.ui.render_main_menu(self.MENU_ROWS, "digite o numero da opcao e pressione enter.")
    
    def run(self):
        """executar wizard"""
        while True:
            self._draw_main_menu()
            choice = self.ui.ask_line("opcao (1-9): ").strip()
            
            if choice == "1":
                self.interactive_mode()
                break
            elif choice == "2":
                self.template_mode()
                break
            elif choice == "3":
                self.blender_mode()
                break
            elif choice == "4":
                self.blender_interactive_mode()
                break
            elif choice == "5":
                self.pipeline_completo_mode()
                break
            elif choice == "6":
                self.show_help_menu()
            elif choice == "7":
                self.show_documentation()
            elif choice == "8":
                self.ui.muted("ate logo!")
                sys.exit(0)
            elif choice == "9":
                self.tests_quick_menu()
            else:
                self.ui.warn("escolha um numero de 1 a 9")
                self.ui.pause("enter para voltar ao menu...")

def main():
    """entrada do programa import tardio evita ciclo se wizard cli importar este modulo"""
    # import dentro da funcao so corre quando main e chamada
    from wizard_cli import run_cli, should_hand_off_to_cli

    # argumentos sem o nome do script contem apenas flags e valores passados pelo usuario
    # should hand off verifica se ha flag tipo load json spec template ou help
    if should_hand_off_to_cli():
        # instancia minima do wizard para reutilizar save verify compile e blender
        wizard = BedWizard()
        # run cli devolve codigo de saida numerico para o sistema operativo
        sys.exit(run_cli(wizard, sys.argv[1:]))
    # sem flags cli abrimos o menu interativo classico
    wizard = BedWizard()
    # run contem o loop do menu e todos os modos questionario template blender
    wizard.run()

# quando executas python bed wizard py diretamente este bloco corre
# quando importas bed wizard como modulo este bloco nao corre
if __name__ == "__main__":
    main()
