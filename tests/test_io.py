import numpy as np
import os
from tpr4py.core.utils.io import write_data, load_data

def test_save_load(tmp_path=os.path.join(os.getcwd(), "tests", "data")):
    data = np.random.rand(5, 10, 10).astype(np.float32)
    tmp_name = "test_random"
    path = os.path.join(tmp_path, f"{tmp_name}.tif")
    write_data(data, tmp_path, tmp_name)
    reload_path = os.path.join(tmp_path, f"QP_{tmp_name}.tif")
    loaded, reload_path = load_data(path=reload_path)
    assert np.allclose(data, loaded)