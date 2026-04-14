# algoritmo spherical_packing coloca esferas uma a uma usando sorteio e rejeicao
# ideia geral sorteia um ponto na caixa que envolve o leito
# se o ponto cai dentro do anel valido e longe de todas as esferas ja aceitas entao aceita
# se nao sorteia de novo ate atingir a quantidade desejada ou o limite de tentativas

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
    # domain descreve o leito e folgas
    # n_target quantas esferas queremos
    # r_sphere raio de cada esfera
    # gap folga entre superficies
    # random_seed se nao for none fixa o gerador para repetir o mesmo sorteio
    # max_placement_attempts limite de sorteios para nao travar para sempre

    t0 = time.perf_counter()
    # fixa a semente do modulo random do python para reprodutibilidade
    if random_seed is not None:
        random.seed(random_seed)

    centers: List[Tuple[float, float, float]] = []
    attempts = 0
    # limites da caixa onde sorteamos x y z
    xmin, xmax, ymin, ymax, zmin, zmax = domain.bbox_for_sampling()
    rho_min, rho_max = domain.radial_bounds()

    # se nao existe faixa radial ou vertical valida devolve vazio imediato
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
    # laco principal tenta ate ter n_target esferas ou estourar o contador
    while len(centers) < n_target and attempts < max_placement_attempts:
        attempts += 1
        # sorteia coordenadas uniformes dentro da caixa
        x = random.uniform(xmin, xmax)
        y = random.uniform(ymin, ymax)
        z = random.uniform(zmin, zmax)
        p = (x, y, z)
        # descarta se fora do cilindro com folga
        if not point_in_domain(p, domain):
            continue
        ok = True
        # distancia minima entre centros de duas esferas iguais com mesma folga
        need_prev = sphere_center_clearance(r_sphere, r_sphere, gap)
        need_sq = need_prev * need_prev
        # compara com cada esfera ja colocada usando distancia ao quadrado para evitar sqrt
        for c in centers:
            dx = p[0] - c[0]
            dy = p[1] - c[1]
            dz = p[2] - c[2]
            if dx * dx + dy * dy + dz * dz < need_sq:
                ok = False
                break
        if ok:
            centers.append(p)

    # se parou antes de n_target explica o motivo aproximado no relatorio
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
