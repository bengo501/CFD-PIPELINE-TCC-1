# este modulo prepara textos e listas numericas para o modo testes rapidos
# nao gera malha 3d so le json lateral e desenha ascii no terminal
# os modos spherical packing e hexagonal 3d sao gerados noutro sitio em pure generation
# la a colisao usa distancia entre centros maior ou igual a dois raios mais gap
# spherical sorteia pontos ate aceitar ou esgotar tentativas
# hexagonal corta uma grade regular pelo dominio cilindrico anular
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


def sidecar_path_for_stl(out_stl: Path) -> Path:
    # entrada out stl e o caminho do ficheiro stl que o python puro acabou de escrever
    # saida e o json com o mesmo stem mais sufixo fixo pure bed
    # o export model data em pure generation segue esta convencao de nome
    stl = Path(out_stl)
    return stl.parent / f"{stl.stem}_pure_bed.json"


def load_sidecar(path: Path) -> Optional[Dict[str, Any]]:
    # tenta ler um json utf8 e devolve dict ou none se falhar
    # p pode ser qualquer caminho o Path normaliza ao usar
    p = Path(path)
    if not p.is_file():
        return None
    try:
        with p.open("r", encoding="utf-8") as f:
            o = json.load(f)
        return o if isinstance(o, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def centers_for_histogram(obj: Dict[str, Any]) -> List[Tuple[float, float, float]]:
    # prefere a lista longa sphere centers histogram ate quinhentos pontos
    # serve para barras de altura sem guardar todas as esferas em ficheiros enormes
    # se nao existir cai em centers from sidecar que usa a amostra curta
    hist = obj.get("sphere_centers_histogram")
    if isinstance(hist, list) and hist:
        out: List[Tuple[float, float, float]] = []
        for item in hist:
            if isinstance(item, (list, tuple)) and len(item) >= 3:
                out.append((float(item[0]), float(item[1]), float(item[2])))
        if out:
            return out
    return centers_from_sidecar(obj)


def centers_from_sidecar(obj: Dict[str, Any]) -> List[Tuple[float, float, float]]:
    # extrai xyz de listas aninhadas no json lateral
    # ordem de preferencia e preview curto depois chaves legadas
    prev = obj.get("sphere_centers_preview")
    if isinstance(prev, list) and prev:
        out: List[Tuple[float, float, float]] = []
        for item in prev:
            if isinstance(item, (list, tuple)) and len(item) >= 3:
                out.append((float(item[0]), float(item[1]), float(item[2])))
        if out:
            return out
    for path in (
        ("sphere_centers",),
        ("centers",),
        ("generation", "centers"),
    ):
        cur: Any = obj
        ok = True
        for k in path:
            if not isinstance(cur, dict) or k not in cur:
                ok = False
                break
            cur = cur[k]
        if ok and isinstance(cur, list) and cur:
            out2: List[Tuple[float, float, float]] = []
            for item in cur:
                if isinstance(item, (list, tuple)) and len(item) >= 3:
                    out2.append((float(item[0]), float(item[1]), float(item[2])))
            return out2
    return []


def height_distribution_lines(
    centers: Sequence[Tuple[float, float, float]],
    z_lo: float,
    z_hi: float,
    nbins: int = 6,
    bar_width: int = 28,
) -> List[str]:
    # divide o eixo z em nbins faixas conta quantas esferas caem em cada faixa
    # z de cada esfera e o terceiro numero do centro xyz
    # a barra ascii usa hashtag proporcional ao maximo da coluna
    # isto nao substitui histograma cientifico so ajuda a ver empilhamento rapido
    if z_hi <= z_lo or nbins < 1:
        return ["intervalo z invalido"]
    if not centers:
        return ["sem centros para histograma"]
    step = (z_hi - z_lo) / nbins
    counts = [0] * nbins
    for c in centers:
        z = c[2]
        if z < z_lo or z > z_hi:
            continue
        i = int((z - z_lo) / step) if step > 0 else 0
        i = max(0, min(nbins - 1, i))
        counts[i] += 1
    mx = max(counts) if counts else 1
    lines: List[str] = []
    for i in range(nbins):
        z0 = z_lo + i * step
        z1 = z_lo + (i + 1) * step
        n = counts[i]
        fill = int(bar_width * n / mx) if mx else 0
        bar = "#" * fill
        lines.append(f"z {z0*1000:03.0f}-{z1*1000:03.0f} mm {bar:<{bar_width}s}  {n}")
    return lines


def ascii_cross_section_schematic(
    bed: Dict[str, Any],
    particles: Dict[str, Any],
    packing_method: str,
    backend_label: str,
    width: int = 44,
) -> str:
    # desenho muito simples de uma faixa horizontal com paredes verticais
    # nao calcula posicao real das esferas so mostra numeros do json
    # serve como cabecalho visual antes de correr o motor pesado
    d = float(bed.get("diameter") or 0.0)
    h = float(bed.get("height") or 0.0)
    pd = float(particles.get("diameter") or 0.0)
    n = int(particles.get("count") or 0)
    line = "-" * max(3, width - 2)
    inner = width - 2
    mid = inner // 2
    row = ["|"] + ["."] * inner + ["|"]
    row[mid + 1] = "o"
    if inner > 3:
        row[2] = ":"
        row[-3] = ":"
    srow = "".join(row)
    lines = [
        f"packing: {packing_method}  |  backend: {backend_label}",
        f"leito: diametro={d} m  altura={h} m",
        f"particulas: count={n}  diametro={pd} m",
        f"+{line}+",
        srow,
        f"+{line}+",
    ]
    return "\n".join(lines)


def ascii_cross_section_with_particles(
    bed: Dict[str, Any],
    centers_xy: Sequence[Tuple[float, float, float]],
    grid: int = 31,
) -> str:
    # vista de cima aproximada projeta x y das esferas num quadrado
    # o circulo de raio externo do leito mapeia para um disco na grade
    # asterisco marca celula com particula cardinalidade pode perder se duas caem na mesma celula
    # tralha marca anel de parede aproximado nao e malha cad exata
    d = float(bed.get("diameter") or 0.0)
    r_ext = d / 2.0
    if r_ext <= 0:
        return "(geometria invalida para preview)"
    g = max(7, min(grid, 51))
    mid = g // 2
    cells = [["." for _ in range(g)] for _ in range(g)]

    def in_circle(ii: int, jj: int) -> bool:
        # normaliza indices para disco unitario centrado na grade
        x = (ii - mid) / mid
        y = (jj - mid) / mid
        return (x * x + y * y) <= 1.0

    for ii in range(g):
        for jj in range(g):
            if not in_circle(ii, jj):
                cells[ii][jj] = " "
            elif abs(math.hypot(ii - mid, jj - mid) - mid) < 1.15:
                cells[ii][jj] = "#"

    rng = random.Random(42)
    sample = list(centers_xy)
    if len(sample) > 80:
        sample = rng.sample(sample, 80)
    for x, y, _z in sample:
        ix = int(mid + (x / r_ext) * (mid - 1.5))
        iy = int(mid + (y / r_ext) * (mid - 1.5))
        if 0 <= ix < g and 0 <= iy < g and in_circle(ix, iy):
            if cells[ix][iy] in (".", "#"):
                cells[ix][iy] = "*"

    lines = ["vista superior x y aproximada asterisco particulas tralha parede"]
    for row in cells:
        lines.append("".join(row))
    return "\n".join(lines)


def preview_before_from_dict(data: Dict[str, Any], backend_label: str) -> None:
    # funcao legada que imprime direto no stdout sem rich
    # o fluxo novo prefere ascii cross section schematic via quick test rich
    bed = dict(data.get("bed") or {})
    particles = dict(data.get("particles") or {})
    packing = dict(data.get("packing") or {})
    pm = str(data.get("packing_mode") or packing.get("method") or "?")
    print("\n--- preview (antes) ---")
    print(ascii_cross_section_schematic(bed, particles, pm, backend_label))
    print()


def preview_after_pure_sidecar(sidecar_path: Path, limit: int = 5) -> None:
    # impressao simples depois da geracao util para scripts sem wizard
    p = Path(sidecar_path)
    print("\n--- preview (depois, python puro) ---")
    obj = load_sidecar(p)
    if not obj:
        print(f"  sidecar nao encontrado: {p}")
        print()
        return
    n_placed = obj.get("n_spheres_placed")
    n_req = obj.get("n_spheres_requested")
    val = obj.get("validation")
    ok = None
    if isinstance(val, dict):
        ok = val.get("ok")
    print(f"  ficheiro: {p.name}")
    if n_placed is not None:
        print(
            f"  esferas colocadas: {n_placed}"
            + (f" / pedidas {n_req}" if n_req is not None else "")
        )
    if ok is not None:
        print(f"  validacao ok: {ok}")
    samp = centers_from_sidecar(obj)[:limit]
    if samp:
        print("  amostra centros (primeiros %d):" % len(samp))
        for c in samp:
            print(f"    ({c[0]:.6f}, {c[1]:.6f}, {c[2]:.6f})")
    else:
        print("  amostra de centros: nao presente no sidecar")
    print()


def preview_after_blender_note(stdout_tail: Optional[str] = None) -> None:
    # quando nao ha json lateral do blender mostramos so o rabo do stdout
    print("\n--- preview (depois, blender) ---")
    if stdout_tail:
        lines = stdout_tail.strip().splitlines()
        tail = lines[-12:] if len(lines) > 12 else lines
        print("  ultimas linhas da saida:")
        for ln in tail:
            print(f"    {ln}")
    else:
        print(
            "  ver saida do blender acima; relatorio packing gravado junto ao .blend se aplicavel"
        )
    print()
