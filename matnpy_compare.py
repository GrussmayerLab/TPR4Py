# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 19:47:46 2022

@author: mengelhardt

this script superficially compares two equally named .mat & .py 
image files/variables from intermeditate steps of the phase recovery code and 
displays them in napari with different colormaps

"""

import numpy as np
import scipy.io as scio
import napari

def compare(file = "", variable = None, vis = False, save = False): 
    #file = "QP_001_HEK293T_stack100_WF_data1"
    mat_struct = scio.loadmat("data\{}.mat".format(file))
    mat = mat_struct[variable]
    py = np.load("data\{}.npy".format(file))
    

    print("{}:\nMat, shape: {}, type: {}, max: {}, min: {}\nNpy, shape: {}, type: {}, max: {}, min: {}".format(file, mat.shape, mat.dtype, np.max(mat), np.min(mat), py.shape, py.dtype, np.max(py), np.min(py)))
    
    
    delta = np.subtract(mat, py)
    span=np.max(delta)-np.min(delta)
    print("Span: {}".format(span))

    #%% napari processing
    if vis: 
        viewer = napari.Viewer()
        viewer.add_image(delta, opacity=0.5, colormap=('viridis'), name=str("delta_" + file )) 
        viewer.add_image(mat, opacity=0.5, name=str("mat_" + file ))
        viewer.add_image(py, opacity= 0.5, colormap=('inferno'), name=str("py_" + file ))
        
    return py, mat, delta