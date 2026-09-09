"""Basic input-file validation."""
from pathlib import Path
from data_engine.exceptions import DataEngineError
from data_engine.ingestion.file_type_detector import detect_file_type


def validate_file(path: str | Path) -> dict:
    p = Path(path).expanduser()
    if not p.exists():
        raise DataEngineError(f"File does not exist: {p}")
    if not p.is_file():
        raise DataEngineError(f"Input is not a file: {p}")
    if p.stat().st_size == 0:
        raise DataEngineError(f"Input file is empty: {p}")
    kind = detect_file_type(p)
    return {"valid": True, "path": str(p.resolve()), "input_kind": kind.value, "size_bytes": p.stat().st_size}
