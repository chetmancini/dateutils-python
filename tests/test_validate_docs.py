import importlib.util
from pathlib import Path
from typing import Any


def _load_validate_docs_module() -> Any:
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "validate_docs.py"
    spec = importlib.util.spec_from_file_location("validate_docs_script", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_docs_script = _load_validate_docs_module()


def test_extract_python_blocks_excludes_other_fences() -> None:
    markdown = """```python
answer = 42
```
```sh
echo ignored
```
```
also_ignored = True
```
```Python
case_sensitive = True
```
"""

    assert validate_docs_script.extract_python_blocks(markdown) == ["answer = 42\n"]


def test_readme_blocks_use_fresh_namespaces() -> None:
    markdown = """```python
value = "first"
```
```python
assert "value" not in globals()
```
"""

    assert validate_docs_script.validate_readme_blocks(markdown) == []


def test_readme_block_failure_reports_index_and_captured_output() -> None:
    markdown = """```python
import sys
print("before failure")
print("error output", file=sys.stderr)
raise RuntimeError("broken example")
```
"""

    failures = validate_docs_script.validate_readme_blocks(markdown)

    assert len(failures) == 1
    assert "README Python block 1 failed" in failures[0]
    assert "Captured output:\nbefore failure\nerror output\n" in failures[0]
    assert "RuntimeError: broken example" in failures[0]


def test_real_readme_python_blocks_pass() -> None:
    readme = validate_docs_script.README_PATH.read_text(encoding="utf-8")

    assert validate_docs_script.validate_readme_blocks(readme) == []


def test_public_module_doctests_pass() -> None:
    assert validate_docs_script.validate_module_doctests() == []
