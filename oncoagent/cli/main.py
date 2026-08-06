from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from oncoagent.coordination.engine import OncoAgentEngine
from oncoagent.models.types import Modality, PatientBundle


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="oncoagent")
    subcommands = result.add_subparsers(dest="command", required=True)
    validate = subcommands.add_parser("validate")
    validate.add_argument("input", type=Path)
    run = subcommands.add_parser("run")
    run.add_argument("input", type=Path)
    run.add_argument("--output", type=Path, required=True)
    return result


def load_bundle(path: Path) -> PatientBundle:
    with path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict):
        raise ValueError("input must be a JSON object")
    case_id = str(raw.get("case_id", ""))
    if not case_id:
        raise ValueError("case_id is required")
    raw_modalities = raw.get("modalities")
    if not isinstance(raw_modalities, dict):
        raise ValueError("modalities must be an object")
    modalities: dict[Modality, dict[str, Any]] = {}
    for name, values in raw_modalities.items():
        modality = Modality(str(name))
        if not isinstance(values, dict):
            raise ValueError(f"modality {name} must be an object")
        modalities[modality] = values
    metadata = raw.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")
    return PatientBundle(case_id, modalities, metadata)


def serialize_result(result: object) -> Any:
    if hasattr(result, "__dataclass_fields__"):
        return {
            name: serialize_result(getattr(result, name)) for name in result.__dataclass_fields__
        }
    if isinstance(result, dict):
        return {str(key): serialize_result(value) for key, value in result.items()}
    if isinstance(result, (tuple, list)):
        return [serialize_result(value) for value in result]
    if hasattr(result, "value"):
        return result.value
    return result


def atomic_json(value: Any, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    bundle = load_bundle(arguments.input)
    if arguments.command == "validate":
        return 0
    result = OncoAgentEngine().run(bundle)
    atomic_json(serialize_result(result), arguments.output)
    return 0 if result.completed else 2


if __name__ == "__main__":
    raise SystemExit(main())
