"""
Napari plug‑in entry point.

Napari expects a dictionary called ``napari_hook_implementation`` that maps
the name of the hook (here ``tpr_viewer``) to a callable.
"""
#from .viewer import tpr_viewer
from viewer import tpr_viewer

napari_hook_implementation = {
    "tpr_viewer": tpr_viewer,
}