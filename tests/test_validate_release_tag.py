import importlib.util
from pathlib import Path
from typing import Any

import pytest


def _load_validate_release_tag_module() -> Any:
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "validate_release_tag.py"
    spec = importlib.util.spec_from_file_location("validate_release_tag_script", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_release_tag_script = _load_validate_release_tag_module()


def _write_pyproject(tmp_path: Path, version: str = "1.2.3") -> Path:
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(f'[project]\nname = "example"\nversion = "{version}"\n', encoding="utf-8")
    return pyproject_path


def test_validate_release_tag_accepts_matching_version(tmp_path: Path) -> None:
    pyproject_path = _write_pyproject(tmp_path)
    assert validate_release_tag_script.validate_release_tag("v1.2.3", pyproject_path) == "1.2.3"


def test_validate_release_tag_rejects_mismatch(tmp_path: Path) -> None:
    pyproject_path = _write_pyproject(tmp_path)
    with pytest.raises(ValueError, match="expected 'v1.2.3'"):
        validate_release_tag_script.validate_release_tag("v1.2.4", pyproject_path)


def test_read_project_version_rejects_missing_version(tmp_path: Path) -> None:
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text('[project]\nname = "example"\n', encoding="utf-8")

    with pytest.raises(ValueError, match="does not define a non-empty project.version"):
        validate_release_tag_script.read_project_version(pyproject_path)
