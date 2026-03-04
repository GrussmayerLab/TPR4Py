# tpr4py/napari_plugin/viewer.py
"""
Napari plug‑in that loads a bright‑field stack, runs quantitative‑phase
retrieval, and (optionally) displays the result in a Napari viewer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import napari
from napari.types import ImageData, LayerDataTuple

# ----------------------------------------------------------------------
# Absolute imports –‑ always start at the top‑level package name.
# ----------------------------------------------------------------------
from ..core.utils.io import load_data
from ..core import run_phase_retrieval
from ..core.phase_structure import phase_structure


def _load_stack(path: str | Path) -> np.ndarray:
    """
    Thin wrapper around :func:`tpr4py.core.utils.io.load_data`.

    Parameters
    ----------
    path :
        Path to a microscopy file that Bio‑Formats (or tifffile) can read.

    Returns
    -------
    np.ndarray
        Image stack in canonical (x, y, z) order.
    """
    stack, _ = load_data(path)
    return stack


def tpr_viewer(
    path: str | Path,
    *,
    show_napari: bool = True,
) -> np.ndarray:
    """
    Napari plug‑in entry point.

    Parameters
    ----------
    path :
        File path to the input stack.
    show_napari :
        If ``True`` (default) a Napari window is opened and the QP volume
        is added as an image layer.  Set to ``False`` when you only need the
        numeric result (e.g. from a script).

    Returns
    -------
    np.ndarray
        The quantitative‑phase (QP) volume with shape ``(x, y, z)``.
    """
    # ------------------------------------------------------------------
    # 1️⃣ Load the raw intensity stack
    # ------------------------------------------------------------------
    stack = _load_stack(path)

    # ------------------------------------------------------------------
    # 2️⃣ Build the optics / processing structure (uses the defaults from
    #    phase_structure.py)
    # ------------------------------------------------------------------
    s = phase_structure()

    # ------------------------------------------------------------------
    # 3️⃣ Run the core algorithm
    # ------------------------------------------------------------------
    qp = run_phase_retrieval.run_phase_retrieval(stack, s)

    # ------------------------------------------------------------------
    # 4️⃣ Optional visualisation
    # ------------------------------------------------------------------
    if show_napari:
        viewer = napari.Viewer()
        viewer.add_image(qp, name="Quantitative Phase (QP)", colormap="gray")
        napari.run()

    return qp