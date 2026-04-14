# algoritmo hexagonal_3d gera uma grade de pontos espacados como em empacotamento compacto
# primeiro criamos uma rede infinita em teoria depois limitamos aos indices que cobrem a caixa
# depois filtramos pontos que caem dentro do anulo cilindrico
# por fim ordenamos e pegamos os n primeiros para ter resultado determinístico

from __future__ import annotations

import math
import time
from typing import List, Tuple, Dict, Any, Optional

from .geometry_math import AnnulusBedDomain, point_in_domain


def _cylinder_radius_xy(p: Tuple[float, float, float]) -> float:
    # auxiliar que devolve a distancia do ponto ao eixo z no plano xy
    return math.hypot(p[0], p[1])


def generate_hexagonal_packing(
    domain: AnnulusBedDomain,
    n_target: int,
    r_sphere: float,
    gap: float,
    *,
    step_x: Optional[float] = None,
) -> Dict[str, Any]:
    # domain leito e folgas
    # n_target quantos pontos queremos no final
    # r_sphere raio
    # gap folga
    # step_x passo opcional na direcao x se none usamos dois r mais gap

    t0 = time.perf_counter()
    # a e o espacamento tipico entre centros vizinhos ao longo de x
    a = float(step_x) if step_x is not None else (2.0 * r_sphere + gap)
    if a <= 0:
        return {
            "centers": [],
            "n_placed": 0,
            "n_target": n_target,
            "elapsed_sec": time.perf_counter() - t0,
            "stopped_reason": "passo_invalido",
            "step_x": a,
        }

    # dy espacamento entre linhas no plano xy para padrao triangular
    dy = a * math.sqrt(3.0) / 2.0
    # dz espacamento vertical entre camadas em empacotamento compacto tipo ab c
    dz = a * math.sqrt(2.0 / 3.0)
    # deslocamento horizontal inteiro quando mudamos de camada impar
    layer_shift_x = a / 2.0
    # deslocamento vertical no plano quando mudamos de camada impar
    layer_shift_y = a / (2.0 * math.sqrt(3.0))

    xmin, xmax, ymin, ymax, zmin, zmax = domain.bbox_for_sampling()
    rho_min, rho_max = domain.radial_bounds()

    if rho_min > rho_max or zmin > zmax:
        return {
            "centers": [],
            "n_placed": 0,
            "n_target": n_target,
            "elapsed_sec": time.perf_counter() - t0,
            "stopped_reason": "dominio_vazio",
            "step_x": a,
        }

    # margem extra para indices de grade para nao perder pontos no bordo
    margin = 2.0 * a
    i_min = int(math.floor((xmin - margin) / a))
    i_max = int(math.ceil((xmax + margin) / a))
    j_min = int(math.floor((ymin - margin) / dy))
    j_max = int(math.ceil((ymax + margin) / dy))
    k_min = int(math.floor((zmin - margin) / dz))
    k_max = int(math.ceil((zmax + margin) / dz))

    candidates: List[Tuple[float, float, float]] = []
    # k indexa camadas em z
    for k in range(k_min, k_max + 1):
        lz = k * dz
        # camadas impares deslocam a malha no plano xy
        off_x_k = layer_shift_x if (k % 2) else 0.0
        off_y_k = layer_shift_y if (k % 2) else 0.0
        for j in range(j_min, j_max + 1):
            # linhas impares deslocam metade do passo em x para formar triangulos
            row_off = (a / 2.0) if (j % 2) else 0.0
            y = j * dy + off_y_k
            for i in range(i_min, i_max + 1):
                x = i * a + row_off + off_x_k
                z = lz
                p = (x, y, z)
                if point_in_domain(p, domain):
                    candidates.append(p)

    # ordenar garante que ao cortar em n_target o resultado e sempre o mesmo
    # criterio primeiro raio cilindrico depois z depois x depois y
    candidates.sort(key=lambda p: (_cylinder_radius_xy(p), p[2], p[0], p[1]))

    if len(candidates) >= n_target:
        chosen = candidates[:n_target]
        reason = "ok_truncado"
    else:
        chosen = candidates
        reason = "pontos_insuficientes_na_grade"

    elapsed = time.perf_counter() - t0
    return {
        "centers": chosen,
        "n_placed": len(chosen),
        "n_target": n_target,
        "elapsed_sec": elapsed,
        "stopped_reason": reason,
        "step_x": a,
        "step_y": dy,
        "step_z": dz,
        "candidates_before_trim": len(candidates),
    }
