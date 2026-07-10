#!/usr/bin/env python3
"""Smoke-test an installed dateutils wheel outside the source checkout."""

from importlib import import_module
from importlib.metadata import version
from importlib.resources import files

import dateutils


def main() -> None:
    distribution_version = version("dateutils-python")
    if dateutils.__version__ != distribution_version:
        raise RuntimeError(
            f"Imported version {dateutils.__version__!r} does not match distribution metadata {distribution_version!r}"
        )

    for module_name in ("dateutils.dateutils", "dateutils.parsing", "dateutils.timezones"):
        import_module(module_name)

    missing_exports = [name for name in dateutils.__all__ if not hasattr(dateutils, name)]
    if missing_exports:
        raise RuntimeError(f"Installed package is missing public exports: {', '.join(missing_exports)}")

    if not files("dateutils").joinpath("py.typed").is_file():
        raise RuntimeError("Installed package is missing dateutils/py.typed")

    print(f"Installed wheel smoke test passed for dateutils-python {distribution_version}")


if __name__ == "__main__":
    main()
