"""
gera arquivo results.json padronizado para um caso openfoam.

uso típico (apos rodar a simulacao no wsl ou windows):

    python postprocess_results.py --case-dir ../../generated/cfd/leito_blender \\
        --pressure-drop 123.4 --average-velocity 0.25 --reynolds-number 1500 \\
        --mesh-cells 850000 --mesh-quality good

o script tambem tenta detectar automaticamente:
- caminho do log (log.simpleFoam)
- tempo de execucao a partir do log (ExecutionTime)
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


def parse_execution_time(log_path: Path) -> float | None:
    if not log_path.exists():
        return None

    try:
        # ler de tras para frente procurando linha com ExecutionTime
        lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line in reversed(lines):
            if "ExecutionTime" in line and "=" in line:
                parts = line.split("=")
                if len(parts) >= 2:
                    value_part = parts[1].strip().split()[0]
                    return float(value_part)
    except Exception:
        return None
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="gera arquivo results.json para um caso openfoam"
    )
    parser.add_argument(
        "--case-dir",
        required=True,
        help="diretorio do caso openfoam (ex: generated/cfd/leito_blender)",
    )
    parser.add_argument("--pressure-drop", type=float, default=None, help="queda de pressao (Pa)")
    parser.add_argument(
        "--average-velocity", type=float, default=None, help="velocidade media na saida (m/s)"
    )
    parser.add_argument(
        "--reynolds-number", type=float, default=None, help="numero de reynolds do escoamento"
    )
    parser.add_argument(
        "--mesh-cells", type=int, default=None, help="numero total de celulas da malha"
    )
    parser.add_argument(
        "--mesh-quality",
        type=str,
        default=None,
        help="qualidade da malha (por ex.: good, acceptable, poor)",
    )
    parser.add_argument(
        "--execution-time",
        type=float,
        default=None,
        help="tempo total de execucao da simulacao (s)",
    )

    args = parser.parse_args()

    case_dir = Path(args.case_dir).resolve()
    if not case_dir.exists():
        raise SystemExit(f"diretorio do caso nao encontrado: {case_dir}")

    # raiz do projeto (assumindo scripts/openfoam_scripts/postprocess_results.py)
    project_root = Path(__file__).resolve().parents[2]

    case_name = case_dir.name
    now_iso = datetime.now().isoformat()

    log_path = case_dir / "log.simpleFoam"

    execution_time = args.execution_time
    if execution_time is None:
        execution_time = parse_execution_time(log_path)

    # montar estrutura padrao do results.json
    data: dict[str, object] = {
        "case_name": case_name,
        "created_at": now_iso,
        "completed_at": now_iso,
        "solver": "simpleFoam",
    }

    if execution_time is not None:
        data["execution_time"] = execution_time

    if args.mesh_cells is not None:
        data["mesh_cells_count"] = args.mesh_cells
    if args.mesh_quality is not None:
        data["mesh_quality"] = args.mesh_quality

    if args.pressure_drop is not None:
        data["pressure_drop"] = args.pressure_drop
    if args.average_velocity is not None:
        data["average_velocity"] = args.average_velocity
    if args.reynolds_number is not None:
        data["reynolds_number"] = args.reynolds_number

    if log_path.exists():
        rel_log = log_path.relative_to(project_root)
        data["log_file"] = str(rel_log).replace("\\", "/")

    # tambem salvar em estruturas mais ricas (metrics)
    metrics: dict[str, dict[str, object]] = {}
    if args.pressure_drop is not None:
        metrics["pressure_drop"] = {"value": args.pressure_drop, "unit": "Pa"}
    if args.average_velocity is not None:
        metrics["average_velocity"] = {"value": args.average_velocity, "unit": "m/s"}
    if args.reynolds_number is not None:
        metrics["reynolds_number"] = {"value": args.reynolds_number, "unit": ""}

    if metrics:
        data["metrics"] = metrics

    results_path = case_dir / "results.json"
    with results_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"results.json gerado em: {results_path}")


if __name__ == "__main__":
    main()

