# modo hexagonal 3d coloca centros numa grade regular inspirada em empacotamento hexagonal compacto
# no plano xy linhas alternadas deslocam metade do passo horizontal formando triangulos equilateros
# em z camadas alternam outro deslocamento para aproximar empilhamento abc de esferas iguais
# passo vertical dz deriva de geometria de tetraedro regular entre centros vizinhos
# iteramos indices i j k numa caixa maior que o dominio depois filtramos com point in domain
# candidatos dentro do anulo cilindrico entram numa lista
# ordenamos por raio ao eixo depois z depois x depois y para o corte nos primeiros n ser determinista
# se houver menos candidatos que n target devolvemos todos e marcamos motivo insuficiente
# colisao entre pares ainda e verificada depois em validation py como no modo spherical
from __future__ import annotations

import math
import time
from typing import List, Tuple, Dict, Any, Optional

from .geometry_math import AnnulusBedDomain, point_in_domain


def _cylinder_radius_xy(p: Tuple[float, float, float]) -> float:
    # rho distancia euclidiana de x y ao eixo z ignorando z
    return math.hypot(p[0], p[1])


def generate_hexagonal_packing(
    domain: AnnulusBedDomain,
    n_target: int,
    r_sphere: float,
    gap: float,
    *,
    step_x: Optional[float] = None,
) -> Dict[str, Any]:
    # domain igual ao spherical packing
    # n target numero desejado de centros
    # r sphere raio
    # gap folga entre superficies
    # step x opcional espacamento horizontal se none usa dois r mais gap que e o diametro com folga

    t0 = time.perf_counter()
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

    dy = a * math.sqrt(3.0) / 2.0
    dz = a * math.sqrt(2.0 / 3.0)
    layer_shift_x = a / 2.0
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

    margin = 2.0 * a
    i_min = int(math.floor((xmin - margin) / a))
    i_max = int(math.ceil((xmax + margin) / a))
    j_min = int(math.floor((ymin - margin) / dy))
    j_max = int(math.ceil((ymax + margin) / dy))
    k_min = int(math.floor((zmin - margin) / dz))
    k_max = int(math.ceil((zmax + margin) / dz))

    candidates: List[Tuple[float, float, float]] = []
    for k in range(k_min, k_max + 1):
        lz = k * dz
        off_x_k = layer_shift_x if (k % 2) else 0.0
        off_y_k = layer_shift_y if (k % 2) else 0.0
        for j in range(j_min, j_max + 1):
            row_off = (a / 2.0) if (j % 2) else 0.0
            y = j * dy + off_y_k
            for i in range(i_min, i_max + 1):
                x = i * a + row_off + off_x_k
                z = lz
                p = (x, y, z)
                if point_in_domain(p, domain):
                    candidates.append(p)

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
