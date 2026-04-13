"""
configuração central (env) para perfis de modelagem e caminhos lógicos.
"""
import os

# blender: rigid body no blender | python: malha procedural + stl sem blender
MODELING_PROFILE = os.getenv("MODELING_PROFILE", "blender").strip().lower()
