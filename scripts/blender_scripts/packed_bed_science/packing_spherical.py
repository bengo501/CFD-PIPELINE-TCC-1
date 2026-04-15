# modo spherical packing coloca centros de esferas um a um com algoritmo de monte carlo
# cada tentativa sorteia x y z dentro de uma caixa que envolve o dominio anular
# point_in_domain rejeita pontos fora do cilindro oco com folga para parede e tampas
# para cada candidato comparamos distancia ao quadrado a todos os centros ja aceites
# se distancia ao quadrado for menor que need ao quadrado ha sobreposicao ou violacao de gap
# need vem de sphere center clearance que e raio mais raio mais gap para duas esferas iguais
# o dominio geometrico completo esta em geometry math AnnulusBedDomain e point in domain
# apos gerar centros o ficheiro validation py percorre pares para confirmar que nada escapou
from __future__ import annotations

import random
import time
from typing import List, Tuple, Dict, Any, Optional

from .geometry_math import AnnulusBedDomain, point_in_domain, sphere_center_clearance


def generate_spherical_packing(
    domain: AnnulusBedDomain,
    n_target: int,
    r_sphere: float,
    gap: float,
    *,
    random_seed: Optional[int] = None,
    max_placement_attempts: int = 500_000,
) -> Dict[str, Any]:
    # domain resume o leito cilindrico oco com raios espessuras de tampa e folga entre esferas
    # n_target e quantas esferas o utilizador pediu pode nao ser atingivel se o volume for pequeno
    # r_sphere e o raio fisico da esfera todas iguais neste fluxo
    # gap e folga minima extra entre superficies duas esferas encostadas teriam distancia de centro 2r mais gap
    # random seed fixa o gerador pseudo aleatorio para repetir a mesma sequencia em depuracao
    # max placement attempts evita laco infinito quando o dominio esta cheio ou muito dificil

    t0 = time.perf_counter()
    if random_seed is not None:
        random.seed(random_seed)

    centers: List[Tuple[float, float, float]] = []
    attempts = 0
    xmin, xmax, ymin, ymax, zmin, zmax = domain.bbox_for_sampling()
    rho_min, rho_max = domain.radial_bounds()

    if rho_min > rho_max or zmin > zmax:
        return {
            "centers": [],
            "n_placed": 0,
            "n_target": n_target,
            "attempts": 0,
            "elapsed_sec": time.perf_counter() - t0,
            "stopped_reason": "dominio_vazio",
        }

    stopped_reason = "ok"
    while len(centers) < n_target and attempts < max_placement_attempts:
        attempts += 1
        x = random.uniform(xmin, xmax)
        y = random.uniform(ymin, ymax)
        z = random.uniform(zmin, zmax)
        p = (x, y, z)
        if not point_in_domain(p, domain):
            continue
        ok = True
        need_prev = sphere_center_clearance(r_sphere, r_sphere, gap)
        need_sq = need_prev * need_prev
        for c in centers:
            dx = p[0] - c[0]
            dy = p[1] - c[1]
            dz = p[2] - c[2]
            if dx * dx + dy * dy + dz * dz < need_sq:
                ok = False
                break
        if ok:
            centers.append(p)

    if len(centers) < n_target:
        stopped_reason = (
            "max_tentativas" if attempts >= max_placement_attempts else "volume_insuficiente"
        )

    elapsed = time.perf_counter() - t0
    return {
        "centers": centers,
        "n_placed": len(centers),
        "n_target": n_target,
        "attempts": attempts,
        "elapsed_sec": elapsed,
        "acceptance_rate": (len(centers) / attempts) if attempts else 0.0,
        "stopped_reason": stopped_reason,
    }
