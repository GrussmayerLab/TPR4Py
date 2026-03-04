"""
Utility functions for loading and saving image stacks.

The primary entry point is :func:`load_data`, which reads any Bio‑Formats‑
compatible file and returns a NumPy array in **(x, y, z)** order.

Both Bio‑Formats (via ``javabridge``) and a pure‑Python fallback
(`skimage.io.imread`) are supported.  The fallback is useful on systems
where Java cannot be started (e.g. restricted CI containers).

Author:  Moritz Engelhardt, supported by lumo
"""

from __future__ import annotations

import os
import pathlib
import warnings
from typing import Tuple, Union, Optional

import numpy as np
import tifffile as tiff

# ----------------------------------------------------------------------
# Optional Bio‑Formats import –‑ lazily loaded only when needed
# ----------------------------------------------------------------------
try:
    import javabridge as jv          # type: ignore
    import bioformats as bf          # type: ignore
    _BIOFORMATS_AVAILABLE = True
except Exception:  # pragma: no cover –‑ import failure is fine, we fall back
    _BIOFORMATS_AVAILABLE = False
    warnings.warn(
        "Bio‑Formats (javabridge + python‑bioformats) not available. "
        "Falling back to tifffile for TIFF/OME‑TIFF only.",
        RuntimeWarning,
    )

# ----------------------------------------------------------------------
# Helper –‑ start/stop the JVM only once per interpreter session
# ----------------------------------------------------------------------
_JVM_STARTED = False


def _ensure_jvm_started(max_heap: str = "8G") -> None:
    """Start the Java VM if it isn’t already running."""
    global _JVM_STARTED
    if not _BIOFORMATS_AVAILABLE:
        return
    if not jv.is_vm_running():
        jv.start_vm(class_path=bf.JARS, max_heap_size=max_heap)
        _JVM_STARTED = True


def _shutdown_jvm() -> None:
    """Stop the Java VM –‑ useful for scripts that exit cleanly."""
    if _BIOFORMATS_AVAILABLE and jv.is_vm_running():
        jv.kill_vm()


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def load_data(
    path: Union[str, os.PathLike],
    *,
    use_bioformats: bool = True,
    series: int = 0,
    z_slice: Optional[int] = None,
) -> Tuple[np.ndarray, str]:
    """
    Load an image stack from *path* and return it as a NumPy array ordered as
    **(x, y, z)**.

    Parameters
    ----------
    path :
        Full path to the image file (any format supported by Bio‑Formats).
    use_bioformats :
        Force the use of Bio‑Formats even if a pure‑Python reader could
        handle the file.  Set to ``False`` to skip the Java dependency
        entirely (only TIFF/OME‑TIFF will work).
    series :
        Index of the image series to read (most files contain a single
        series, but multi‑series OME‑XML files can store several).
    z_slice :
        If the file contains a 3‑D stack and you only want a single Z slice,
        provide its 0‑based index here.  ``None`` (default) loads the full
        Z dimension.

    Returns
    -------
    data :
        NumPy array with shape ``(x, y, z)`` (or ``(x, y)`` for a 2‑D image).
    filename :
        The absolute path that was read (handy for downstream logging).

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    RuntimeError
        If Bio‑Formats fails to read the file.
    """
    #path = pathlib.Path(path).expanduser().resolve()
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    # --------------------------------------------------------------
    # 1️⃣ Try Bio‑Formats (preferred, works for virtually any microscopy format)
    # --------------------------------------------------------------
    if use_bioformats and _BIOFORMATS_AVAILABLE:
        _ensure_jvm_started()
        try:
            # ``load_image`` returns an array in (z, y, x, c) order.
            raw = bf.load_image(str(path), series=series, rescale=False)
        except Exception as exc:  # pragma: no cover –‑ rare but possible
            raise RuntimeError(f"Bio‑Formats failed to read {path}: {exc}") from exc

        # ----------------------------------------------------------
        # Normalise axis order
        # ----------------------------------------------------------
        # Drop channel axis if present (original code assumed single‑channel)
        if raw.ndim == 4:          # (z, y, x, c)
            raw = raw[..., 0]
        elif raw.ndim == 3:        # (z, y, x)
            pass
        else:                      # pragma: no cover –‑ unexpected shape
            raise RuntimeError(
                f"Unexpected array shape {raw.shape} from Bio‑Formats for {path}"
            )

        # At this point raw.shape == (z, y, x)
        data = np.transpose(raw, (2, 1, 0))   # → (x, y, z)

        # Optional single‑slice extraction
        if z_slice is not None:
            data = data[:, :, z_slice]

        return data, str(path)

    # --------------------------------------------------------------
    # 2️⃣ Pure‑Python fallback –‑ tifffile (handles TIFF/OME‑TIFF)
    # --------------------------------------------------------------
    try:
        raw = tiff.imread(str(path))
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"tifffile failed to read {path}: {exc}") from exc

    # tifffile returns (z, y, x) for 3‑D stacks, (y, x) for 2‑D images.
    if raw.ndim == 3:          # (z, y, x)
        data = np.transpose(raw, (2, 1, 0))   # → (x, y, z)
    elif raw.ndim == 2:        # (y, x) –‑ treat as a single‑plane stack
        data = np.transpose(raw, (1, 0))[..., np.newaxis]  # (x, y, 1)
    else:                      # pragma: no cover –‑ unsupported dimensionality
        raise RuntimeError(
            f"Unsupported image dimensionality {raw.shape} for file {path}"
        )

    if z_slice is not None:
        data = data[:, :, z_slice : z_slice + 1]

    return data, str(path)


# ----------------------------------------------------------------------
# Helper for writing quantitative‑phase (QP) data –‑ unchanged semantics,
# but now uses tifffile directly.
# ----------------------------------------------------------------------
def write_data(
    qp: np.ndarray,
    out_dir: Union[str, os.PathLike],
    base_name: str,
) -> None:
    """
    Write a quantitative‑phase (QP) stack to disk as a TIFF file.

    Parameters
    ----------
    qp :
        The phase volume. Expected shape is ``(x, y, z)`` or ``(x, y, z, t)``.
    out_dir :
        Destination folder (will be created if it does not exist).
    base_name :
        Base filename *without* extension. The function prefixes ``QP_`` and
        writes ``.tif``.
    """
    #out_dir = pathlib.Path(out_dir).expanduser().resolve()
    out_dir = pathlib.Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Re‑order to the conventional (z, y, x) layout expected by most viewers.
    if qp.ndim == 4:  # (x, y, z, t) → (t, z, y, x)
        qp_to_save = np.transpose(qp, (3, 2, 1, 0))
        axes = "TZYX"
    else:            # (x, y, z) → (z, y, x)
        qp_to_save = np.transpose(qp, (2, 1, 0))
        axes = "ZYX"

    out_path = os.path.join(out_dir, f"QP_{base_name}.tif")
    tiff.imwrite(
        str(out_path),
        qp_to_save,
        metadata={
            "axes": axes,
            # Example metadata –‑ adapt to your instrument if needed
            "unit": "nm",
        },
    )
    print(f"QP stack written to {out_path}")


# ----------------------------------------------------------------------
# Small UI helpers –‑ kept for backward compatibility (Tkinter dialogs)
# ----------------------------------------------------------------------
def select_parameter_z() -> int:
    """Prompt the user for a Z‑dimension index (Tkinter dialog)."""
    import tkinter as tk
    from tkinter import simpledialog

    root = tk.Tk()
    root.withdraw()
    val = simpledialog.askinteger(
        title="Select Z dimension",
        prompt="Enter Z index (0‑based)",
    )
    root.destroy()
    return int(val)


def select_parameter_t() -> int:
    """Prompt the user for a T‑dimension index (Tkinter dialog)."""
    import tkinter as tk
    from tkinter import simpledialog

    root = tk.Tk()
    root.withdraw()
    val = simpledialog.askinteger(
        title="Select T dimension",
        prompt="Enter T index (0‑based)",
    )
    root.destroy()
    return int(val)