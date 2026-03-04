#!/usr/bin/env python
"""
Command‑line front‑end for TPR4Py.

Typical usage:

    $ tpr4py /path/to/my_stack.nd2 -o results/ --no‑napari

The script will:
    - 1. Load the image stack (any Bio‑Formats‑supported format).
    - 2. Run the phase‑retrieval pipeline.
    - 3. Save the quantitative‑phase (QP) volume as a TIFF.
    - 4. (Optionally) launch Napari to visualise the result.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np

# ----------------------------------------------------------------------
# Local imports –‑ these come from the refactored package layout
# ----------------------------------------------------------------------
from tpr4py.core.utils.io import load_data, write_data
from tpr4py.core.phase_structure import phase_structure
from tpr4py.core import run_phase_retrieval
from tpr4py.core.utils.processing_loader import build_phase_structure

# Optional Napari import –‑ only pulled in if the user wants visualisation
try:
    import napari  # noqa: F401
    _NAPARI_AVAILABLE = True
except Exception:  # pragma: no cover
    _NAPARI_AVAILABLE = False


def _show_in_napari(volume: np.ndarray, title: str) -> None:
    """Open a Napari viewer and display *volume*."""
    if not _NAPARI_AVAILABLE:  # defensive –‑ should never happen
        raise RuntimeError("Napari is not installed; cannot display the result.")
    viewer = napari.Viewer()
    viewer.add_image(volume, name=title, colormap="gray", blending="additive")
    napari.run()


def parse_cli() -> argparse.Namespace:
    """Parse command‑line arguments."""
    parser = argparse.ArgumentParser(
        prog="tpr4py",
        description="Quantitative phase retrieval from bright‑field image stacks.",
    )
    parser.add_argument(
        "input_path",
        type=pathlib.Path,
        help="Path to the input image stack (any Bio‑Formats‑supported file).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help="Directory where the QP TIFF will be written (default: current working directory).",
    )
    parser.add_argument(
        "--no-napari",
        action="store_true",
        help="Skip launching Napari after processing.",
    )
    parser.add_argument(
        "--series",
        type=int,
        default=0,
        help="Series index to read from multi‑series OME files (default: 0).",
    )
    parser.add_argument(
        "--z-index",
        type=int,
        default=None,
        help="If you only want a single Z slice, give its 0‑based index here.",
    )
    # ────────────────────────────────────────────────────────────────
    # NEW: phase‑structure selection
    # ────────────────────────────────────────────────────────────────
    parser.add_argument(
        "--phase-config",
        type=pathlib.Path,
        default=phase_structure.__module__,  # default to the built‑in class
        help=(
            "Path to a YAML/JSON file **or** a Python module that defines a "
            "`phase_structure` class. If omitted the built‑in defaults are used."
        ),
    )
    parser.add_argument(
        "--class-name",
        type=str,
        default="phase_structure",
        help=(
            "When `--phase-config` points to a Python module, the name of the "
            "class to instantiate (defaults to `phase_structure`)."
        ),
    )

    return parser.parse_args()


def main() -> int:
    """Entry point for the console script."""
    args = parse_cli()

    # ------------------------------------------------------------------
    # 1️⃣ Load the data
    # ------------------------------------------------------------------
    try:
        stack, filename = load_data(
            args.input_path,
            use_bioformats=True,
            series=args.series,
            z_slice=args.z_index,
        )
    except Exception as exc:  # pragma: no cover –‑ user‑visible error
        sys.stderr.write(f"Failed to read {args.input_path}: {exc}\n")
        return 1

    # ------------------------------------------------------------------
    # 2️⃣ Build the optics / processing structure
    # ------------------------------------------------------------------
    try:
        s = build_phase_structure(args.phase_config, args.class_name)
    except Exception as exc:  # pragma: no cover
        sys.stderr.write(f"Failed to build specific phase_structure: {exc}\n")
        return 1

    # ------------------------------------------------------------------
    # 3️⃣ Run the phase‑retrieval algorithm
    # ------------------------------------------------------------------
    qp_volume = run_phase_retrieval.run_phase_retrieval(stack, s)

    # ------------------------------------------------------------------
    # 4️⃣ Write the result
    # ------------------------------------------------------------------
    out_dir = args.output_dir.resolve()
    base_name = pathlib.Path(filename).stem
    write_data(qp_volume, out_dir, base_name)

    # ------------------------------------------------------------------
    # 5️⃣ (Optional) visualise in Napari
    # ------------------------------------------------------------------
    if not args.no_napari:
        if _NAPARI_AVAILABLE:
            _show_in_napari(qp_volume, title=f"QP_{base_name}")
        else:
            sys.stderr.write(
                "Napari not installed –‑ skipping visualisation.\n"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())