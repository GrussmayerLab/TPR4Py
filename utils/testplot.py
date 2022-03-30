# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 19:17:56 2022

@author: mengelhardt
"""

#from loadData import loadData
import napari
from dask_image.imread import imread
import numpy as np

#stack = loadData()
QP =  np.load("QP.npy")
napari.view_image(QP)
#result = grayscale(QP)
#print(result)
#result.visualize()