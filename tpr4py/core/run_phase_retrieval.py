import numpy as np
from .phase_structure import phase_structure
from .algorithms.getQP import getQP


def run_phase_retrieval(
    stack: np.ndarray,
    struct: phase_structure | None = None,
    *,
    mask: np.ndarray | None = None,
    progress: bool = True,
) -> np.ndarray:
    """Convenient wrapper that performs the whole pipeline.

    Returns the quantitative‑phase (QP) volume.
    """
    if struct is None:
        struct = phase_structure()
    if progress:
        from tqdm import tqdm
        tqdm_desc = tqdm(total=1, desc="Phase retrieval")
    qp, _ = getQP(stack, struct, mask)
    if progress:
        tqdm_desc.update()
    return qp