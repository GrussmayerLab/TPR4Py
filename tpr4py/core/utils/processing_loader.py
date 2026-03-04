# utils/phase_loader.py
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml  

# Import the *default* class so we can fall back to it
from ..phase_structure import phase_structure as DefaultPhaseStructure


def _load_python_module(module_path: Path) -> Any:
    """Import a .py file as a module and return the module object."""
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import module from {module_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_path.stem] = mod
    spec.loader.exec_module(mod)  # type: ignore[arg-type]
    return mod


def _load_mapping(file_path: Path) -> Mapping[str, Any]:
    """Read a YAML or JSON file and return a dict of parameters."""
    if file_path.suffix.lower() in {".yaml", ".yml"}:
        with file_path.open("rt", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    if file_path.suffix.lower() == ".json":
        with file_path.open("rt", encoding="utf-8") as fh:
            return json.load(fh)
    raise ValueError(
        f"Unsupported config file type: {file_path.suffix}. "
        "Supported: .yaml, .yml, .json, .py"
    )


def build_phase_structure(config_path: Path | None, class_name: str = "phase_structure"):
    """
    Return an instantiated ``phase_structure`` object.

    Parameters
    ----------
    config_path :
        Path to a YAML/JSON file **or** a Python module.  If ``None`` the
        built‑in defaults are used.
    class_name :
        Name of the class to instantiate when ``config_path`` points to a
        Python module.  Ignored for YAML/JSON.

    Returns
    -------
    An object that behaves like ``utils.phase_structure.phase_structure``.
    """
    # ------------------------------------------------------------------
    # No custom config → just use the defaults
    # ------------------------------------------------------------------
    if config_path is None:
        return DefaultPhaseStructure()

    # ------------------------------------------------------------------
    # YAML / JSON → load a mapping and *populate* a fresh instance
    # ------------------------------------------------------------------
    if config_path.suffix.lower() in {".yaml", ".yml", ".json"}:
        params = _load_mapping(config_path)
        obj = DefaultPhaseStructure()
        for key, value in params.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
            else:
                raise AttributeError(
                    f"The default phase_structure has no attribute '{key}'. "
                    "Check the spelling in your config file."
                )
        return obj

    # ------------------------------------------------------------------
    # Python module → import and instantiate the requested class
    # ------------------------------------------------------------------
    if config_path.suffix.lower() == ".py":
        mod = _load_python_module(config_path)
        if not hasattr(mod, class_name):
            raise AttributeError(
                f"Module {config_path} does not define a class named "
                f"'{class_name}'."
            )
        cls = getattr(mod, class_name)
        return cls()  # assume a no‑arg constructor like the default

    raise ValueError(
        f"Unsupported config file type: {config_path.suffix}. "
        "Supported: .yaml, .yml, .json, .py"
    )