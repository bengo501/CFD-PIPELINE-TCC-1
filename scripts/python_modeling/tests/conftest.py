# prepara sys path antes de importar packed_bed_stl e modulos vizinhos
import sys
from pathlib import Path

_PMDIR = Path(__file__).resolve().parent.parent
_SCRIPTS = _PMDIR.parent
_BLENDER_SCRIPTS = _SCRIPTS / "blender_scripts"
_ROOT = _SCRIPTS.parent
_VIS_CIL = _ROOT / "tools" / "vis_cilindro"

for p in (_PMDIR, _VIS_CIL, _BLENDER_SCRIPTS):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
