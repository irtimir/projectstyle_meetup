from __future__ import annotations

import importlib
from pathlib import Path


def autodiscover_models() -> None:
    app_path = Path(__file__).parent.parent / "core"
    for models_file in app_path.glob("*/models.py"):
        module_name = f"app.core.{models_file.parent.name}.models"
        importlib.import_module(module_name)
