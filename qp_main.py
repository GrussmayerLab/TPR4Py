#-*- coding: utf-8 -*-
# Main file to run quantitative phase recovery script
# Original script was written in Matlab by Adrien Descloux (see below)
# Author: mengelhardt
# main.py (was QP_main.m)
# This file contains a basic pipeline for QP retrieval from brightfield stacks
#     - 3D image stack loading
#     - 3D stack preprocessing
#     - processing parameters definition
#     - phase calculation
#     - display of the results
# ---------------------------------------    
# A detailled description of the theory supporting this program can be found in : 
# "Descloux, A., et al. "Combined multi-plane phase retrieval and
# super-resolution optical fluctuation imaging for 4D cell microscopy." 
# Nature Photonics 12.3 (2018): 165."
# Copyright © 2018 Adrien Descloux - adrien.descloux@epfl.ch, 
# École Polytechnique Fédérale de Lausanne, LBEN/LOB,
# BM 5.134, Station 17, 1015 Lausanne, Switzerland.
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from utils.loadData import loadData
from utils.cropXY import cropXY
from utils.cropCoregMask import cropCoregMask
from utils.phase_structure import phase_structure
from utils.getQP import getQP
from utils.plotStack import plotStack

import numpy as np

#%% 3D image stack loading
stack,fname = loadData() 
plot_flag = True
#stack,pname,fname = loadData
Nx,Ny,Nz = stack.shape

#%%3D stack preprocessing
if Nz == 8:                                 # i.e. multiplane data : remove the coregistration mask
    stack=cropCoregMask(stack)
    TEMP_NPIX = 100                         # variable was undefined in mat file, set accordingly         
    stack=cropXY(stack,TEMP_NPIX - 4)       #  extra safety crop 
else:
    stack=cropXY(stack)

np.save("data\stack_crop.npy", stack)

Nz,Nx,Ny = stack.shape
#%% Phase retrieval
# define optics and processing parameters
#s=copy(setup_phase_default)
s=phase_structure()
s.optics_kzT = 0.01             # Axial cutoff frequency

# if set to [], use the theoretical value
s.proc_mirrorX = False              # mirror the input stack along X 
s.proc_mirrorZ = True               # mirror the input stack along Z
s.proc_applyFourierMask = True

# set experimental parameters
if stack.shape[0] == 8:              # i.e. MultiPlane data
    s.optics_dz = 0.35               # [um]
else:
    s.optics_dz = 0.2               # typical sampling for fixed cells


#%% compute the phase
QP,_ = getQP(stack,s)

#%% napari 3D stack plotting
if plot_flag:
    plotStack(QP)
    np.save("data/QP.npy", QP)

#%% mat2py comparisons (mat files saved externally)



from matnpy_compare import compare
#py, mat, delta = compare("QP", "QP", True, False)
#py, mat, delta = compare("Ik", "Ik", False, False)

#compare("csd", "csd", False, False)
#compare("kx", "kx", False, False)   # check: equal
#compare("kz", "kz", False, False)   # check: equal
#compare("maskCTF", "maskCTF", True, False)   # check: equal
#compare("stack_crop", "stack", False, False)   # check: equal
#compare("mirroredStack", "stackM", vis = True ,save = False)  # check: equal


py, mat, delta = compare("mask3D", "mask", True, False)

#compare("mapr", "mapr", True, False)
#py, mat, delta = compare("in", "in", True, False)
#py, mat, delta = compare("r_py", "r", True, False)

#py, mat, delta = compare("mapf", "mapf", True, False)
#py, mat, delta = compare("mapc", "mapc", True, False)
#py, mat, delta = compare("mask2D", "mask2D", True, False)

#py, mat, delta = compare("p", "p", True, False)
#py, mat, delta = compare("Gamma", "Gamma", False, False)




