# le variaveis de ambiente que alteram comportamento sem recompilar codigo
import os

# perfil de modelacao escolhe entre motor blender com gui headless ou script python puro
# strip remove espacos e lower normaliza para comparacoes seguras mais abaixo
MODELING_PROFILE = os.getenv("MODELING_PROFILE", "blender").strip().lower()
