# motor simples de templates json para o bed wizard
# ficheiros ficam em dsl wizard_templates com extensao json
# merge_template permite sobrepor campos sem copiar o ficheiro inteiro a mao
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

# pasta onde estao os ficheiros default rigid spherical hex
_TEMPLATES_DIR = Path(__file__).resolve().parent / "wizard_templates"

# chaves de primeiro nivel que o merge trata como blocos independentes
# cada chave e uma secao do modelo bed particles lids packing export cfd
# a secao generation e usada para configurar generation_backend
_MERGE_KEYS = ("bed", "particles", "lids", "packing", "export", "cfd", "generation")


def list_template_names() -> list[str]:
    # varre wizard_templates e devolve lista ordenada de stems sem extensao
    # stem e o nome do ficheiro sem ponto json
    # se a pasta nao existir devolve lista vazia para o menu nao rebentar
    if not _TEMPLATES_DIR.is_dir():
        return []
    names = []
    for p in sorted(_TEMPLATES_DIR.glob("*.json")):
        names.append(p.stem)
    return names


def load_template(name: str) -> Dict[str, Any]:
    # name pode ser default spherical ou default spherical json
    # le o ficheiro e valida que a raiz e um objeto dict
    stem = name.strip()
    if stem.endswith(".json"):
        stem = stem[:-5]
    path = _TEMPLATES_DIR / f"{stem}.json"
    if not path.is_file():
        raise FileNotFoundError(f"template nao encontrado: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("template deve ser um objeto json")
    return data


def merge_template(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    # base e o template carregado primeiro
    # overrides e tipicamente outro json de teste ou ajustes finos
    # para cada chave em merge keys se overrides tiver essa chave
    # o resultado funde dicts campo a campo no mesmo nivel
    # se overrides tiver valor nao dict substitui o bloco inteiro
    # packing_mode na raiz copia se existir em overrides
    out = deepcopy(base)
    for key in _MERGE_KEYS:
        if key not in overrides:
            continue
        ov = overrides[key]
        if ov is None:
            continue
        if not isinstance(ov, dict):
            out[key] = deepcopy(ov)
            continue
        if key not in out or not isinstance(out[key], dict):
            out[key] = deepcopy(ov)
        else:
            merged = deepcopy(out[key])
            merged.update(ov)
            out[key] = merged
    if "packing_mode" in overrides:
        out["packing_mode"] = overrides["packing_mode"]
    if "generation_backend" in overrides:
        out["generation_backend"] = overrides["generation_backend"]
    return out
