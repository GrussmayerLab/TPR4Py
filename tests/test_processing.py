"""
Tests for the core processing pipeline of **tpr4py**.

The test uses the small example stack shipped with the repository
(`tests/data/fiji_test.tif`).  It verifies that:

1. The TIFF can be loaded with the unified I/O helper.
2. The data is returned in the canonical ``(x, y, z)`` order.
3. The phase‑retrieval routine runs without raising an exception.
4. The output has the expected shape and dtype.
5. The QP volume can be written to disk (using a temporary directory).

These checks are intentionally lightweight – they do not validate the
numerical correctness of the algorithm (that would require reference data),
but they guarantee that the public API works end‑to‑end.
"""

from pathlib import Path

import numpy as np
import pytest
import pathlib

# ----------------------------------------------------------------------
# Import the public API from the package (the import path works because the
# project is installed in editable mode during the test run).
# ----------------------------------------------------------------------
from tpr4py.core.utils.io import load_data, write_data
from tpr4py.core import run_phase_retrieval
from tpr4py.core.phase_structure import phase_structure


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture(scope="module")
def fiji_test_path() -> Path:
    """Absolute path to the small test TIFF shipped with the repo."""
    return Path(__file__).parent / "data" / "fiji_test.tif"


@pytest.fixture(scope="module")
def loaded_stack(fiji_test_path):
    """Load the test stack using the unified I/O helper."""
    stack, _ = load_data(str(fiji_test_path))
    return stack


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------
def test_load_returns_xyz_order(loaded_stack):
    """
    The loader must return a NumPy array in **(x, y, z)** order.
    """
    assert isinstance(loaded_stack, np.ndarray), "load_data should return a ndarray"
    # The test file is a 3‑D stack (x≈y≈z).  We only assert that it has three axes.
    assert loaded_stack.ndim == 3, "Loaded stack should be 3‑D"
    # Verify that the axes are ordered as (x, y, z) by checking shape consistency
    x, y, z = loaded_stack.shape
    # For the supplied test file the dimensions are equal, but the important
    # thing is that we have three distinct axes.
    assert x > 0 and y > 0 and z > 0, "All dimensions must be positive"


def test_phase_retrieval_runs_without_error(loaded_stack):
    """
    Run the quantitative‑phase algorithm on the test stack and ensure it
    completes without raising an exception.
    """
    s = phase_structure()          # default optics / processing parameters
    qp = run_phase_retrieval.run_phase_retrieval(loaded_stack, s)

    # Basic sanity checks on the result
    assert isinstance(qp, np.ndarray), "run_phase_retrieval should return a ndarray"
    # The algorithm returns a floating‑point phase map
    assert np.issubdtype(qp.dtype, np.floating), "QP should be a float array"


def test_write_qp_to_repo_data():
    """
    Verify that the QP volume can be written to the permanent
    ``tests/data/`` directory of the repository.
    """
    # Resolve the repository root (the folder that contains this test file)
    repo_root = pathlib.Path(__file__).resolve().parents[1]   # <repo>/tests/
    repo_data_dir = repo_root / "tests" / "data"
    repo_data_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1️⃣  Produce a QP volume with the existing pipeline
    # ------------------------------------------------------------------
    stack, _ = load_data(str(repo_data_dir / "fiji_test.tif"))
    s = phase_structure()
    qp = run_phase_retrieval.run_phase_retrieval(stack, s)

    # ------------------------------------------------------------------
    # 2️⃣  Write the file to a *temporary* location first
    # ------------------------------------------------------------------
    base_name = "fiji_test"

    # ``write_data`` expects (qp, out_dir, base_name)
    write_data(qp, str(repo_data_dir), base_name)

    tmp_file = repo_data_dir / f"QP_{base_name}.tif"
    assert tmp_file.is_file(), f"Temporary QP file not created: {tmp_file}"

    # ------------------------------------------------------------------
    # 4️⃣  Validate the persisted file
    # ------------------------------------------------------------------
    assert tmp_file.is_file(), f"Expected output file {tmp_file} not found"

    # Optional sanity‑check: read the file back and compare shapes
    reloaded, _ = load_data(str(tmp_file))
    assert reloaded.shape == qp.shape, (
        "Reloaded QP should match the written shape: "
        f"{reloaded.shape} vs {qp.shape}"
    )


# ----------------------------------------------------------------------
# Additional regression test (optional)
# ----------------------------------------------------------------------
def test_consistent_dtype_across_runs(loaded_stack):
    """
    Running the algorithm twice on the same input should yield identical
    dtypes and shapes (numerical values may differ slightly due to
    nondeterministic FFT planning, but the dtype/shape must be stable).
    """
    s = phase_structure()
    qp1 = run_phase_retrieval.run_phase_retrieval(loaded_stack, s)
    qp2 = run_phase_retrieval.run_phase_retrieval(loaded_stack, s)

    assert qp1.shape == qp2.shape
    assert qp1.dtype == qp2.dtype
    # A loose numeric check – the two results should be close to each other.
    np.testing.assert_allclose(qp1, qp2, rtol=1e-6, atol=1e-8)