import importlib.util
import re
from pathlib import Path
from typing import Any

import dateutils


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


def test_markdown_blocks_use_fresh_namespaces() -> None:
    markdown = """```python
value = "first"
```
```python
assert "value" not in globals()
```
"""

    assert validate_docs_script.validate_markdown_blocks(markdown, "README.md") == []


def test_markdown_block_failure_reports_document_index_and_captured_output() -> None:
    markdown = """```python
import sys
print("before failure")
print("error output", file=sys.stderr)
raise RuntimeError("broken example")
```
"""

    failures = validate_docs_script.validate_markdown_blocks(markdown, "API.md")

    assert len(failures) == 1
    assert "API.md Python block 1 failed" in failures[0]
    assert "Captured output:\nbefore failure\nerror output\n" in failures[0]
    assert "RuntimeError: broken example" in failures[0]


def test_real_readme_python_blocks_pass() -> None:
    readme = validate_docs_script.README_PATH.read_text(encoding="utf-8")

    assert validate_docs_script.validate_markdown_blocks(readme, "README.md") == []


def test_real_api_python_blocks_pass() -> None:
    api = validate_docs_script.API_PATH.read_text(encoding="utf-8")

    assert validate_docs_script.validate_markdown_blocks(api, "API.md") == []


def test_api_reference_documents_every_public_export() -> None:
    api = validate_docs_script.API_PATH.read_text(encoding="utf-8")

    headings = re.findall(r"^### `([A-Za-z_][A-Za-z0-9_]*)`$", api, flags=re.MULTILINE)

    assert len(headings) == len(set(headings)), "duplicate API headings"
    assert set(headings) == set(dateutils.__all__)
    for name in headings:
        assert getattr(dateutils, name) is not None


def test_public_module_doctests_pass() -> None:
    assert validate_docs_script.validate_module_doctests() == []
