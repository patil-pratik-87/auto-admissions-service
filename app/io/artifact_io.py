"""Strict, atomic JSON persistence for artifacts this runtime owns."""

import json
import os
import tempfile
from contextlib import suppress
from pathlib import Path

from pydantic import BaseModel, ValidationError

from app.models.artifacts import ApplicationFactsArtifact


class ArtifactIOError(Exception):
    """Expected local persistence error with a stable public code."""

    def __init__(self, code: str, safe_message: str) -> None:
        """Initialize a safe filesystem error."""
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message


def preflight_output_paths(paths: tuple[Path, ...], *, overwrite: bool) -> None:
    """Create parent directories and reject every command-owned collision.

    Args:
        paths: Every success or failure path the command may own.
        overwrite: Whether existing exact target files may be replaced.

    Raises:
        ArtifactIOError: If a parent cannot be prepared or a target is unsafe.
    """
    if len(paths) != len(set(paths)):
        raise ArtifactIOError("DUPLICATE_OUTPUT_PATH", "Command output paths must be distinct.")

    for path in paths:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ArtifactIOError("OUTPUT_PARENT_UNAVAILABLE", "An output directory could not be prepared.") from exc

        if path.exists():
            if path.is_dir():
                raise ArtifactIOError("OUTPUT_TARGET_IS_DIRECTORY", "An output target is a directory.")
            if not overwrite:
                raise ArtifactIOError("OUTPUT_EXISTS", "A command-owned output already exists.")


def atomic_write_model(path: Path, model: BaseModel, *, overwrite: bool) -> None:
    """Serialize one strict model as stable UTF-8 JSON and publish it atomically.

    Args:
        path: Exact command-owned output path.
        model: Validated Pydantic artifact or report.
        overwrite: Whether an existing exact target may be replaced.

    Raises:
        ArtifactIOError: If the target cannot be written without violating the
            requested overwrite behavior.
    """
    payload = json.dumps(
        model.model_dump(mode="json"),
        allow_nan=False,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())

        if overwrite:
            os.replace(temporary_path, path)
            temporary_path = None
        else:
            try:
                os.link(temporary_path, path)
            except FileExistsError as exc:
                raise ArtifactIOError("OUTPUT_EXISTS", "A command-owned output already exists.") from exc
    except ArtifactIOError:
        raise
    except OSError as exc:
        raise ArtifactIOError("ARTIFACT_WRITE_FAILED", "A JSON artifact could not be written.") from exc
    finally:
        if temporary_path is not None:
            with suppress(OSError):
                temporary_path.unlink(missing_ok=True)


def load_facts_artifact(path: Path) -> ApplicationFactsArtifact:
    """Load one exact, strict Revision 2 facts artifact from disk.

    Args:
        path: Existing local facts artifact path.

    Returns:
        The validated immutable facts artifact.

    Raises:
        ArtifactIOError: If the path is unavailable or its JSON does not satisfy
            the frozen artifact contract.
    """
    if not path.exists():
        raise ArtifactIOError("FACTS_PATH_NOT_FOUND", "The facts artifact does not exist.")
    if not path.is_file():
        raise ArtifactIOError("FACTS_PATH_NOT_REGULAR_FILE", "The facts artifact path is not a regular file.")
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise ArtifactIOError("FACTS_ARTIFACT_READ_FAILED", "The facts artifact could not be read.") from exc
    try:
        return ApplicationFactsArtifact.model_validate_json(payload, strict=True)
    except (ValidationError, ValueError) as exc:
        raise ArtifactIOError("FACTS_ARTIFACT_INVALID", "The facts artifact is invalid or incompatible.") from exc
