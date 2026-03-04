from magicgui import magicgui
from napari import Viewer

@magicgui(call_button="Run QP", dz={"widget_type": "FloatSlider", "min": 0.05, "max": 1.0})
def qp_widget(viewer: Viewer, path: str, dz: float = 0.1):
    stack = _load_stack(path)
    s = phase_structure()
    s.optics_dz = dz
    qp = run_phase_retrieval(stack, s)
    viewer.add_image(qp, name="QP", colormap="gray")