# le variaveis de ambiente para escolher como gerar geometria 3d
import os

# blender usa rigid body dentro do blender
# python gera malha procedural sem gui blender
MODELING_PROFILE = os.getenv("MODELING_PROFILE", "blender").strip().lower()
