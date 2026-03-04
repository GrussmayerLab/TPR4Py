import numpy as np
# ----------------------------------------------------------------------
# Import the public API from the package (the import path works because the
# project is installed in editable mode during the test run).
# ----------------------------------------------------------------------
from tpr4py.core.utils.io import load_data, write_data
from tpr4py.core import run_phase_retrieval
from tpr4py.core.phase_structure import phase_structure


s=phase_structure()
print(s)
stack, _ = load_data(r"E:\GitHub\TPR4Py\tests\data\fiji_test.tif")
print(stack.shape)
qp = run_phase_retrieval.run_phase_retrieval(stack, s)
print(qp.shape)