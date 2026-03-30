import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


vec3 = Tuple[float, float, float]
triangulo = Tuple[int, int, int]


@dataclass
class mesh:
    vertices: List[vec3] = field(default_factory=list)
    indices: List[triangulo] = field(default_factory=list)


@dataclass
class params_cilindro:
    raio_externo: float
    raio_interno: float
    altura: float
    segmentos: int = 64


@dataclass
class params_particulas:
    num_particulas: int
    raio_particula: float
    gravidade: float = -9.81
    dt: float = 0.005
    max_passos: int = 20000


@dataclass
class particula:
    pos: vec3
    vel: vec3


def gera_malha_tubo_com_tampas(p: params_cilindro) -> mesh:
    m = mesh()

    for i in range(p.segmentos):
        ang = 2.0 * math.pi * i / p.segmentos
        x = p.raio_externo * math.cos(ang)
        y = p.raio_externo * math.sin(ang)
        m.vertices.append((x, y, 0.0))
        m.vertices.append((x, y, p.altura))

    base_interna = len(m.vertices)

    for i in range(p.segmentos):
        ang = 2.0 * math.pi * i / p.segmentos
        x = p.raio_interno * math.cos(ang)
        y = p.raio_interno * math.sin(ang)
        m.vertices.append((x, y, 0.0))
        m.vertices.append((x, y, p.altura))

    for i in range(p.segmentos):
        ni = (i + 1) % p.segmentos

        b_i = 2 * i
        t_i = 2 * i + 1
        b_n = 2 * ni
        t_n = 2 * ni + 1

        m.indices.append((b_i, t_i, b_n))
        m.indices.append((t_i, t_n, b_n))

    for i in range(p.segmentos):
        ni = (i + 1) % p.segmentos

        b_i = base_interna + 2 * i
        t_i = base_interna + 2 * i + 1
        b_n = base_interna + 2 * ni
        t_n = base_interna + 2 * ni + 1

        m.indices.append((b_i, b_n, t_i))
        m.indices.append((t_i, b_n, t_n))

    # vertices centrais das tampas (discos cheios, sem furo)
    indice_centro_inferior = len(m.vertices)
    m.vertices.append((0.0, 0.0, 0.0))

    indice_centro_superior = len(m.vertices)
    m.vertices.append((0.0, 0.0, p.altura))

    # tampa inferior (disco cheio em z = 0, usando apenas a borda externa)
    for i in range(p.segmentos):
        ni = (i + 1) % p.segmentos

        bo_i = 2 * i       # vertice da borda externa (base)
        bo_n = 2 * ni

        # triangulo em leque a partir do centro
        m.indices.append((indice_centro_inferior, bo_n, bo_i))

    # tampa superior (disco cheio em z = altura, usando apenas a borda externa)
    for i in range(p.segmentos):
        ni = (i + 1) % p.segmentos

        to_i = 2 * i + 1   # vertice da borda externa (topo)
        to_n = 2 * ni + 1

        m.indices.append((indice_centro_superior, to_i, to_n))

    return m


def cria_particulas_iniciais(p_cil: params_cilindro,
                             p_par: params_particulas) -> List[particula]:
    particulas = []

    for _ in range(p_par.num_particulas):
        r = random.uniform(0.0, p_cil.raio_interno * 0.8)
        ang = random.uniform(0.0, 2.0 * math.pi)
        x = r * math.cos(ang)
        y = r * math.sin(ang)
        z = p_cil.altura + random.uniform(0.1, 0.5)

        particulas.append(particula(
            pos=(x, y, z),
            vel=(0.0, 0.0, 0.0),
        ))

    return particulas


def passo_simulacao(particulas: List[particula],
                    p_cil: params_cilindro,
                    p_par: params_particulas,
                    tampa_superior_fechada: bool) -> None:
    g = p_par.gravidade
    dt = p_par.dt

    for p in particulas:
        x, y, z = p.pos
        vx, vy, vz = p.vel

        vz = vz + g * dt

        x = x + vx * dt
        y = y + vy * dt
        z = z + vz * dt

        if z - p_par.raio_particula < 0.0:
            z = p_par.raio_particula
            if vz < 0.0:
                vz = -0.3 * vz

        if tampa_superior_fechada and z + p_par.raio_particula > p_cil.altura:
            z = p_cil.altura - p_par.raio_particula
            if vz > 0.0:
                vz = -0.3 * vz

        r = math.sqrt(x * x + y * y)
        limite = p_cil.raio_interno - p_par.raio_particula
        if r > limite and r > 0.0:
            escala = limite / r
            x *= escala
            y *= escala

            vr = (vx * x + vy * y) / (r * r + 1e-8)
            vx = vx - 2.0 * vr * x
            vy = vy - 2.0 * vr * y
            vx *= 0.3
            vy *= 0.3

        p.pos = (x, y, z)
        p.vel = (vx, vy, vz)


def simula_ate_tampa_fechar(p_cil: params_cilindro,
                            p_par: params_particulas):
    particulas = cria_particulas_iniciais(p_cil, p_par)
    tampa_superior_fechada = False

    for passo in range(p_par.max_passos):
        if not tampa_superior_fechada:
            todas_dentro = all(p.pos[2] <= p_cil.altura for p in particulas)
            if todas_dentro:
                tampa_superior_fechada = True
                print(f"tampa superior fechada no passo {passo}")

        passo_simulacao(particulas, p_cil, p_par, tampa_superior_fechada)

    return particulas, tampa_superior_fechada


def salvar_obj(m: mesh, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8") as f:
        for vx, vy, vz in m.vertices:
            f.write(f"v {vx} {vy} {vz}\n")

        for a, b, c in m.indices:
            f.write(f"f {a + 1} {b + 1} {c + 1}\n")


def salvar_particulas_xyz(particulas: List[particula], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8") as f:
        for p in particulas:
            x, y, z = p.pos
            f.write(f"{x} {y} {z}\n")


if __name__ == "__main__":
    # raiz do repositorio: CFD-PIPELINE-TCC-1/
    base_dir = Path(__file__).resolve().parents[2]
    out_dir = base_dir / "generated" / "3d" / "cilindro_teste"

    obj_path = out_dir / "tubo_com_tampas.obj"
    particulas_path = out_dir / "particulas.xyz"

    p_cil = params_cilindro(
        raio_externo=1.0,
        raio_interno=0.8,
        altura=5.0,
        segmentos=64,
    )

    p_par = params_particulas(
        num_particulas=200,
        raio_particula=0.05,
        gravidade=-9.81,
        dt=0.005,
        max_passos=20000,
    )

    malha = gera_malha_tubo_com_tampas(p_cil)
    salvar_obj(malha, obj_path)
    print(f"arquivo {obj_path} salvo")

    particulas_finais, tampa_fechada = simula_ate_tampa_fechar(p_cil, p_par)
    salvar_particulas_xyz(particulas_finais, particulas_path)
    print(f"arquivo {particulas_path} salvo")
    print("tampa fechada:", tampa_fechada)

