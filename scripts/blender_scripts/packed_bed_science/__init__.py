# pacote packed_bed_science agrupa matematica validacao e geradores de posicao
# o blender_build fica separado porque precisa de bpy
# o leito_extracao importa estes modulos ao rodar como script no blender

from .geometry_math import (
    euclidean_distance,
    AnnulusBedDomain,
    sphere_center_clearance,
)
from .validation import (
    validate_position,
    check_collision_pair,
    validate_configuration,
)
from .packing_spherical import generate_spherical_packing
from .packing_hexagonal import generate_hexagonal_packing

__all__ = [
    "euclidean_distance",
    "AnnulusBedDomain",
    "sphere_center_clearance",
    "validate_position",
    "check_collision_pair",
    "validate_configuration",
    "generate_spherical_packing",
    "generate_hexagonal_packing",
]

# leia abaixo um roteiro conceitual em linguagem simples
# objetivo gerar posicoes de esferas dentro de tubo oco com tampas
# comparar sorteio com rejeicao contra grade hexagonal filtrada
# equacao principal distancia entre centros maior ou igual soma dos raios mais gap
# limites radiais usam rho igual hipotenusa de x e y
# limites em z usam faces internas das tampas mais raio mais gap
# spherical fixa seed para repetir experimento
# hexagonal ordena por raio para cortar sempre igual
# validacao visita todos os pares custo n ao quadrado
# integracao o json traz packing.method e packing.gap o backend pode mesclar chaves extras no json compilado
