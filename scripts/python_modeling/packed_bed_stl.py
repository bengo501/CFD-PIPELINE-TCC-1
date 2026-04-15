#!/usr/bin/env python3
# script principal gera ficheiro stl binario com leito empacotado sem blender
#
# dois grandes caminhos conforme packing method no json
# caminho cientifico spherical packing ou hexagonal 3d usa packed bed science e pure bed mesh
# caminho legacy rigid body usa simulacao de queda em modelo cilindro
#
# modelagem em python puro no caminho cientifico
# o cilindro oco vem de create hollow cylinder geometry com quatro aneis de vertices
# as tampas sao cilindros curtos solidos create cap geometry
# as esferas sao malhas uv sphere fundidas com merge mesh
#
# validacao geometrica reutiliza validate configuration do pacote packed bed science
# o dominio e AnnulusBedDomain igual ao script blender leito extracao
#
# integracao com o backend
# o servico blender service chama este script quando modeling profile e python ou pure python
# aliases blender python e blender apontam para o motor blender
# ver funcao normalize modeling profile em blender service
#
# modo spherical packing
# coloca esferas por sorteio com rejeicao ate preencher pedido ou esgotar tentativas
# respeita gap minimo entre centros e limites do dominio anular
#
# modo hexagonal 3d
# usa grade hexagonal filtrada ao dominio anular e altura util
# opcao step x ajusta espacamento horizontal da grade
#
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

# diretorio deste ficheiro para importar stl mesh utils e pure bed mesh no mesmo nivel
_PMDIR = Path(__file__).resolve().parent
if str(_PMDIR) not in sys.path:
    sys.path.insert(0, str(_PMDIR))

# raiz do projeto dois niveis acima deste script
_ROOT = Path(__file__).resolve().parents[2]
# vis cilindro opcional para outras ferramentas
_VIS_CIL = _ROOT / "tools" / "vis_cilindro"
if str(_VIS_CIL) not in sys.path:
    sys.path.insert(0, str(_VIS_CIL))

# pasta scripts um nivel acima para importar packed bed science e blender scripts
_SCRIPTS = Path(__file__).resolve().parents[1]
_BLENDER_SCRIPTS_DIR = _SCRIPTS / "blender_scripts"
if str(_BLENDER_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_BLENDER_SCRIPTS_DIR))

from modelo_cilindro import (  # noqa: E402
    gera_malha_tubo_com_tampas,
    mesh,
    params_cilindro,
    params_particulas,
    simula_ate_tampa_fechar,
)

from packed_bed_science.geometry_math import AnnulusBedDomain, estimate_porosity  # noqa: E402
from packed_bed_science.packing_hexagonal import generate_hexagonal_packing  # noqa: E402
from packed_bed_science.packing_spherical import generate_spherical_packing  # noqa: E402
from packed_bed_science.validation import validate_configuration  # noqa: E402

from pure_bed_mesh import build_packed_bed_model, export_model_data  # noqa: E402
from stl_mesh_utils import merge_mesh, uv_sphere, write_stl_binary  # noqa: E402

# alias de tipo para tripla de floats xyz
vec3 = Tuple[float, float, float]
# alias de tipo para triangulo como tres indices
tri = Tuple[int, int, int]


def _to_float(v: Any, default: float = 0.0) -> float:
    # converte entrada solta do json para float seguro
    # aceita int float ou string com virgula trocada por ponto
    # v valor vindo do json pode ser none
    # default retorno se none
    if v is None:
        return float(default)
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", "."))


def _to_int(v: Any, default: int = 0) -> int:
    # converte entrada para inteiro
    # trunca float e parseia strings numericas
    if v is None:
        return int(default)
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    return int(float(str(v).replace(",", ".")))


def _packing_method_name(packing: Dict[str, Any]) -> str:
    # le o metodo de empacotamento e normaliza nomes
    # packing pode ser vazio no json
    # method aceita chave method ou packing method
    # hexagonal3d e hexagonal-3d viram hexagonal_3d
    if not packing:
        return "rigid_body"
    m = packing.get("method") or packing.get("packing_method") or "rigid_body"
    s = str(m).strip().strip('"').lower()
    if s in ("hexagonal3d", "hexagonal-3d"):
        return "hexagonal_3d"
    return s


def _coerce_bool(v: Any, default: bool = True) -> bool:
    # interpreta texto como booleano para flags do json
    # aceita varias palavras em portugues e ingles
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "sim"):
        return True
    if s in ("false", "0", "no", "nao"):
        return False
    return default


def load_bed_json(path: Path) -> Dict[str, Any]:
    # le o ficheiro json completo e devolve um dicionario plano com chaves fixas
    # path caminho absoluto ou relativo ao cwd
    # secao bed tem diametro altura espessura de parede
    # secao particles tem contagem diametro e seed opcional
    # secao lids tem espessuras de tampas
    # secao packing tem metodo gravidade gap seeds e malha
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    bed = data.get("bed") or {}
    particles = data.get("particles") or {}
    lids = data.get("lids") or {}
    packing = data.get("packing") or {}

    # diametro externo util do leito em metros
    diameter = _to_float(bed.get("diameter"), 0.05)
    # altura util entre tampas em metros
    height = _to_float(bed.get("height"), 0.1)
    # espessura da parede cilindrica em metros
    wall = _to_float(bed.get("wall_thickness"), 0.002)

    # count numero pedido de particulas pode vir como string
    count = particles.get("count", 100)
    count_i = _to_int(count, 100)

    # diametro da particula esferica
    pd = particles.get("diameter", 0.005)
    particle_d = _to_float(pd, 0.005)

    # gravidade usada so no modo legacy rigid body
    grav = packing.get("gravity", -9.81)
    grav_f = _to_float(grav, -9.81)

    # espessuras fisicas das tampas inferior e superior
    bottom_t = _to_float(lids.get("bottom_thickness"), 0.003)
    top_t = _to_float(lids.get("top_thickness"), 0.003)

    # gap minimo extra entre superficies das esferas
    # preferimos chave gap se existir senao collision margin
    gap = packing.get("gap")
    if gap is not None:
        gap_f = _to_float(gap, 0.0)
    else:
        gap_f = _to_float(packing.get("collision_margin"), 0.0)

    # dicionario unificado usado por toda a geracao
    return {
        "diameter": diameter,
        "height": height,
        "wall_thickness": wall,
        "particle_count": max(1, count_i),
        "particle_diameter": particle_d,
        "gravity": grav_f,
        "bottom_thickness": bottom_t,
        "top_thickness": top_t,
        "packing": packing,
        "packing_method": _packing_method_name(packing),
        "gap": gap_f,
        "random_seed": packing.get("random_seed"),
        "max_placement_attempts": _to_int(packing.get("max_placement_attempts"), 500_000),
        "strict_validation": _coerce_bool(packing.get("strict_validation"), True),
        "step_x": packing.get("step_x"),
        "particles_seed": particles.get("seed"),
        "mesh_segmentos": _to_int(packing.get("mesh_segmentos"), 48),
        "sphere_lat": _to_int(packing.get("sphere_lat"), 4),
        "sphere_lon": _to_int(packing.get("sphere_lon"), 6),
    }


def _mesh_to_lists(m: mesh) -> Tuple[List[vec3], List[tri]]:
    # converte objeto mesh do modelo cilindro legacy para listas deste script
    # m tem atributos vertices e indices
    return list(m.vertices), list(m.indices)


def _legacy_generate_stl(p: Dict[str, Any], out_stl: Path, max_passos: int) -> None:
    # caminho legacy rigid body
    # simula particulas em queda ate estabilizar depois funde tubo e esferas
    # p dicionario vindo de load bed json
    # out stl destino
    # max passos limite de iteracao da simulacao fisica simples
    # r ext raio externo metade do diametro
    r_ext = p["diameter"] / 2.0
    # r int raio interno nunca menor que um pouco mais que raio da particula para nao ficar impossivel
    r_int = max(r_ext - p["wall_thickness"], p["particle_diameter"] * 0.51)
    # altura cilindro
    altura = p["height"]

    # parametros do tubo para malha com tampas incluidas no legacy
    p_cil = params_cilindro(
        raio_externo=r_ext,
        raio_interno=r_int,
        altura=altura,
        segmentos=min(64, max(12, p.get("mesh_segmentos", 48))),
    )
    # parametros das particulas numero raio passos e dt
    p_par = params_particulas(
        num_particulas=p["particle_count"],
        raio_particula=p["particle_diameter"] / 2.0,
        gravidade=p["gravity"],
        dt=0.004,
        max_passos=max_passos,
    )

    # gera malha do tubo com tampas como no fluxo antigo
    malha_tubo = gera_malha_tubo_com_tampas(p_cil)
    verts, faces = _mesh_to_lists(malha_tubo)

    # simula ate as particulas pararem ou fechar tampa conforme funcao legacy
    particulas_finais, _ = simula_ate_tampa_fechar(p_cil, p_par)
    # raio esferico igual ao usado na simulacao
    r_s = p_par.raio_particula
    # para cada particula final adiciona esfera uv
    for part in particulas_finais:
        x, y, z = part.pos
        sv, sf = uv_sphere(x, y, z, r_s, lat=p["sphere_lat"], lon=p["sphere_lon"])
        verts, faces = merge_mesh(verts, faces, sv, sf)

    write_stl_binary(out_stl, verts, faces)


def _science_generate_stl(p: Dict[str, Any], out_stl: Path) -> None:
    # caminho cientifico spherical packing ou hexagonal 3d
    # usa o mesmo nucleo matematico que o blender para posicoes
    # depois monta geometria com pure bed mesh e exporta stl mais json lateral
    # p dicionario normalizado
    # out stl ficheiro stl de saida
    # r ext raio externo do tubo
    r_ext = p["diameter"] / 2.0
    # r int raio interno parede menos espessura
    r_int = r_ext - p["wall_thickness"]
    # checagem basica de sanidade antes de continuar
    if r_int <= 0 or r_int >= r_ext:
        raise ValueError("raio interno invalido verifique diameter e wall thickness")
    # altura util
    altura = p["height"]
    # raio da esfera metade do diametro da particula
    r_s = p["particle_diameter"] / 2.0
    # gap copiado do dicionario
    gap = p["gap"]
    # espessuras de tampa inferior e superior
    tb = p["bottom_thickness"]
    tt = p["top_thickness"]

    # dominio geometrico compartilhado com validacao e geradores
    # define regiao anular em xy e faixa vertical entre tampas
    domain = AnnulusBedDomain(
        r_int=r_int,
        r_ext=r_ext,
        height=altura,
        bottom_cap_thickness=tb,
        top_cap_thickness=tt,
        r_sphere=r_s,
        gap=gap,
    )

    # method nome canonico ja normalizado
    method = p["packing_method"]
    # medir tempo de geracao para metadados
    t0 = time.perf_counter()
    if method == "spherical_packing":
        # modo sorteio com rejeicao
        # tenta colocar cada nova esfera sem sobrepor anteriores nem violar paredes
        # random seed pode vir de packing ou de particles seed
        seed = p.get("random_seed")
        if seed is None:
            seed = p.get("particles_seed")
        # se ainda none o gerador interno pode usar default proprio
        seed_i = _to_int(seed, 42) if seed is not None else None
        gen = generate_spherical_packing(
            domain,
            p["particle_count"],
            r_s,
            gap,
            random_seed=seed_i,
            max_placement_attempts=p["max_placement_attempts"],
        )
    else:
        # modo hexagonal 3d
        # preenche espaco com padrao tipo empilhamento compacto depois corta ao dominio
        # step x opcional afina distancia horizontal entre centros de camadas
        step_x_opt = p.get("step_x")
        step_x_f = _to_float(step_x_opt, 0.0) if step_x_opt is not None else None
        # zero ou negativo significa deixar o gerador escolher automatico
        if step_x_f is not None and step_x_f <= 0:
            step_x_f = None
        gen = generate_hexagonal_packing(
            domain,
            p["particle_count"],
            r_s,
            gap,
            step_x=step_x_f,
        )
    # tempo decorrido em segundos
    elapsed = time.perf_counter() - t0

    # centros devolvidos pelo gerador
    centers = gen["centers"]
    # lista de raios iguais para o validador
    radii = [r_s] * len(centers)
    # validate configuration verifica sobreposicao e limites segundo convencao de gap
    # gap convention aqui e distancia entre centros maior ou igual soma raios mais gap
    report_val = validate_configuration(centers, radii, domain, gap)
    # porosidade estimada por volume excluido das esferas
    poros = estimate_porosity(domain, centers, r_s)

    # strict validation se true falha com erro quando relatorio nao ok
    strict = p["strict_validation"]
    if not report_val.get("ok", False):
        if strict:
            raise RuntimeError(
                "validacao geometrica falhou: " + str(report_val.get("messages", []))[:500]
            )
    # no modo spherical tambem exige contagem se strict
    if method == "spherical_packing" and len(centers) < p["particle_count"] and strict:
        raise RuntimeError(
            f"spherical packing so colocou {len(centers)} de {p['particle_count']}"
        )

    # segmentos do cilindro limitados para nao explodir memoria
    seg = min(64, max(12, p.get("mesh_segmentos", 48)))
    # monta malha unificada tubo tampas esferas
    packed = build_packed_bed_model(
        r_ext=r_ext,
        r_int=r_int,
        height=altura,
        bottom_cap_thickness=tb,
        top_cap_thickness=tt,
        sphere_centers=centers,
        sphere_radius=r_s,
        segmentos_cil=seg,
        lat_sphere=p["sphere_lat"],
        lon_sphere=p["sphere_lon"],
    )

    # extra metadados escritos ao lado do stl
    extra: Dict[str, Any] = {
        "packing_method": method,
        "validation": report_val,
        "porosity_estimate": poros,
        "generation": {k: v for k, v in gen.items() if k != "centers"},
        "generation_wall_time_sec": elapsed,
        "gap_convention": "center_distance >= r1+r2+gap",
        "n_spheres_requested": p["particle_count"],
        "n_spheres_placed": len(centers),
    }
    # json opcional com mesmo nome base que stl mais sufixo pure bed
    out_json = out_stl.parent / f"{out_stl.stem}_pure_bed.json"
    export_model_data(packed, out_stl, out_json=out_json, extra=extra)


def generate_packed_bed_stl(
    bed_json: Path, out_stl: Path, max_passos: int = 12000
) -> None:
    # funcao publica usada pelo backend e por linha de comando
    # carrega json escolhe ramo cientifico ou legacy
    # bed json entrada
    # out stl saida
    # max passos so legacy
    p = load_bed_json(bed_json)
    if p["packing_method"] in ("spherical_packing", "hexagonal_3d"):
        _science_generate_stl(p, out_stl)
    else:
        _legacy_generate_stl(p, out_stl, max_passos)


def main() -> None:
    # interface cli simples
    ap = argparse.ArgumentParser(description="gera stl empacotado python sem blender")
    ap.add_argument("bed_json", type=Path, help="ficheiro bed json")
    ap.add_argument("out_stl", type=Path, help="ficheiro stl saida")
    ap.add_argument(
        "--max-passos",
        type=int,
        default=12000,
        help="passos simulacao apenas no modo rigid body legacy",
    )
    args = ap.parse_args()
    if not args.bed_json.exists():
        raise SystemExit(f"ficheiro nao encontrado: {args.bed_json}")
    generate_packed_bed_stl(args.bed_json, args.out_stl, max_passos=args.max_passos)
    print(f"[ok] stl escrito: {args.out_stl}")


if __name__ == "__main__":
    main()

# bloco final didatico leia antes de alterar
# modelagem o tubo oco e malha de quatro aneis de vertices mais faces triangulares
# tampas sao cilindros curtos solidos com disco em cada base
# esferas sao esferas uv discretizadas
# spherical packing sorteia posicoes e rejeita colisoes ate cumprir meta ou parar
# hexagonal 3d usa grade hexagonal filtrada ao volume util
# validacao e validate configuration sobre AnnulusBedDomain com lista de mensagens
# colisao entre esferas usa distancia entre centros comparada com soma raios mais gap
# limites usam r int r ext z min z max derivados das tampas no dominio
# usuario escolhe motor na api modeling profile python ou pure python para este script
# usuario escolhe blender ou blender python para leito extracao no blender
