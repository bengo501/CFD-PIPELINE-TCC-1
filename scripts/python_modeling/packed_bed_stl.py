#!/usr/bin/env python3
"""
gera um único ficheiro stl (binário) com tubo + tampas + esferas empacotadas,
usando a simulação simples de partículas de tools/vis_cilindro/modelo_cilindro.py.

uso:
  python packed_bed_stl.py caminho/leito.bed.json saida/leito.stl
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path
from typing import List, Tuple

# reutilizar malha do cilindro e simulação existentes
_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "tools" / "vis_cilindro"))
from modelo_cilindro import (  # noqa: E402
    gera_malha_tubo_com_tampas,
    mesh,
    params_cilindro,
    params_particulas,
    simula_ate_tampa_fechar,
)

vec3 = Tuple[float, float, float]
tri = Tuple[int, int, int]


def _to_float(v) -> float:
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", "."))


def _load_bed_params(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    bed = data.get("bed") or {}
    particles = data.get("particles") or {}
    packing = data.get("packing") or {}

    diameter = _to_float(bed.get("diameter", 0.05))
    height = _to_float(bed.get("height", 0.1))
    wall = _to_float(bed.get("wall_thickness", 0.002))

    count = particles.get("count", 100)
    if isinstance(count, str):
        count = int(float(count))
    else:
        count = int(count)

    pd = particles.get("diameter", 0.005)
    particle_d = _to_float(pd)

    grav = packing.get("gravity", -9.81)
    if isinstance(grav, str):
        grav = _to_float(grav)
    else:
        grav = float(grav)

    return {
        "diameter": diameter,
        "height": height,
        "wall_thickness": wall,
        "particle_count": max(1, count),
        "particle_diameter": particle_d,
        "gravity": grav,
    }


def _mesh_to_lists(m: mesh) -> Tuple[List[vec3], List[tri]]:
    return list(m.vertices), list(m.indices)


def _uv_sphere(cx: float, cy: float, cz: float, r: float, lat: int = 5, lon: int = 8) -> Tuple[List[vec3], List[tri]]:
    verts: List[vec3] = []
    faces: List[tri] = []
    for j in range(lat + 1):
        th = math.pi * j / lat
        sin_t = math.sin(th)
        cos_t = math.cos(th)
        for i in range(lon):
            ph = 2 * math.pi * i / lon
            x = cx + r * sin_t * math.cos(ph)
            y = cy + r * sin_t * math.sin(ph)
            z = cz + r * cos_t
            verts.append((x, y, z))
    for j in range(lat):
        for i in range(lon):
            a = j * lon + i
            b = j * lon + (i + 1) % lon
            c = (j + 1) * lon + (i + 1) % lon
            d = (j + 1) * lon + i
            faces.append((a, b, d))
            faces.append((b, c, d))
    return verts, faces


def _merge(
    va: List[vec3], fa: List[tri], vb: List[vec3], fb: List[tri]
) -> Tuple[List[vec3], List[tri]]:
    off = len(va)
    return va + vb, fa + [(a + off, b + off, c + off) for a, b, c in fb]


def write_stl_binary(path: Path, vertices: List[vec3], faces: List[tri]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", len(faces)))
        for i, j, k in faces:
            x0, y0, z0 = vertices[i]
            x1, y1, z1 = vertices[j]
            x2, y2, z2 = vertices[k]
            ux, uy, uz = x1 - x0, y1 - y0, z1 - z0
            vx, vy, vz = x2 - x0, y2 - y0, z2 - z0
            nx = uy * vz - uz * vy
            ny = uz * vx - ux * vz
            nz = ux * vy - uy * vx
            ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            nx, ny, nz = nx / ln, ny / ln, nz / ln
            f.write(
                struct.pack(
                    "<12fHxx",
                    nx,
                    ny,
                    nz,
                    x0,
                    y0,
                    z0,
                    x1,
                    y1,
                    z1,
                    x2,
                    y2,
                    z2,
                    0,
                )
            )


def generate_packed_bed_stl(bed_json: Path, out_stl: Path, max_passos: int = 12000) -> None:
    p = _load_bed_params(bed_json)
    r_ext = p["diameter"] / 2.0
    r_int = max(r_ext - p["wall_thickness"], p["particle_diameter"] * 0.51)
    altura = p["height"]

    p_cil = params_cilindro(
        raio_externo=r_ext,
        raio_interno=r_int,
        altura=altura,
        segmentos=48,
    )
    p_par = params_particulas(
        num_particulas=p["particle_count"],
        raio_particula=p["particle_diameter"] / 2.0,
        gravidade=p["gravity"],
        dt=0.004,
        max_passos=max_passos,
    )

    malha_tubo = gera_malha_tubo_com_tampas(p_cil)
    verts, faces = _mesh_to_lists(malha_tubo)

    particulas_finais, _ = simula_ate_tampa_fechar(p_cil, p_par)
    r_s = p_par.raio_particula
    for part in particulas_finais:
        x, y, z = part.pos
        sv, sf = _uv_sphere(x, y, z, r_s, lat=4, lon=6)
        verts, faces = _merge(verts, faces, sv, sf)

    write_stl_binary(out_stl, verts, faces)


def main() -> None:
    ap = argparse.ArgumentParser(description="gera stl empacotado (python, sem blender)")
    ap.add_argument("bed_json", type=Path, help="ficheiro .bed.json")
    ap.add_argument("out_stl", type=Path, help="ficheiro .stl de saída")
    ap.add_argument("--max-passos", type=int, default=12000, help="passos da simulação de queda")
    args = ap.parse_args()
    if not args.bed_json.exists():
        raise SystemExit(f"ficheiro não encontrado: {args.bed_json}")
    generate_packed_bed_stl(args.bed_json, args.out_stl, max_passos=args.max_passos)
    print(f"[ok] stl escrito: {args.out_stl}")


if __name__ == "__main__":
    main()
