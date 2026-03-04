"""
[QP,mask] = getQP(stack,s,mask)
---------------------------------------

Recover the Cross-spectral density from the intensity stack

Inputs:
    stack        Input intensity 3D stack
    s            Structure containing all optics and processing parameters
                   see "setup_phase_default.m"
    mask         Precomputed mask for fast reconstruction

Outputs:
    QP        	Quantitative phase
    mask         Mask used to filter the intensity stack

---------------------------------------
A detailled description of the theory supporting this program can be found in : 
"Descloux, A., et al. "Combined multi-plane phase retrieval and 
 super-resolution optical fluctuation imaging for 4D cell microscopy." 
 Nature Photonics 12.3 (2018): 165."

  Copyright © 2018 Adrien Descloux - adrien.descloux@epfl.ch, 
  École Polytechnique Fédérale de Lausanne, LBEN/LOB,
  BM 5.134, Station 17, 1015 Lausanne, Switzerland.

 	This program is free software: you can redistribute it and/or modify
 	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
 	(at your option) any later version.

 	This program is distributed in the hope that it will be useful,
 	but WITHOUT ANY WARRANTY; without even the implied warranty of
 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
 	along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import numpy as np
from numpy import dot, pi, sin, cos, angle, logical_and, logical_or
import numpy.fft as fft
import math
from tpr4py.core.utils.getMirroredStack import getMirroredStack
from tpr4py.core.utils.map3D import map3D


def getQP(stack=None,struct=None,mask=None):

    # mirror the data and compute adequate Fourier space grid
    kx,kz,stackM = getMirroredStack(stack,struct)
    
    if mask is None: # if no mask is provided
        # compute usefull stuff
        th=math.asin(struct.optics_NA / struct.optics_n)
        th_ill=math.asin(struct.optics_NA_ill / struct.optics_n)
        k0max = dot(dot(struct.optics_n,2),pi) / (struct.optics_wv - struct.optics_dlambda / 2) 
        k0min = dot(dot(struct.optics_n,2),pi) / (struct.optics_wv + struct.optics_dlambda / 2) 
        
        # compute Fourier space grid and the phase mask
        Kx,Kz=np.meshgrid(kx,kz)
        if struct.optics_kzT is None:
            mask2D = Kz >= np.dot(k0max,(1 - cos(th_ill)))
        else:
            mask2D = Kz >= struct.optics_kzT


        if struct.proc_applyFourierMask:  #  => compute the CTF mask for extra denoising
            # CTF theory
            maskCTF = logical_and(logical_and(logical_and(
                ((Kx - dot(k0max,sin(th_ill))) ** 2 + (Kz - dot(k0max,cos(th_ill))) ** 2) <= k0max ** 2, \
                    ((Kx + dot(k0min,sin(th_ill))) ** 2 + (Kz - k0min) ** 2) >= k0min ** 2), Kx >= 0), \
                    Kz < dot(k0max,(1 - cos(th))))            
            maskCTF = logical_or(maskCTF,maskCTF[:,::-1])
            mask2D = np.asanyarray(logical_and(mask2D,maskCTF), dtype=int)
        # since we assume a circular symetric CTF, we expand the 2Dmask in 3D
        mask=map3D(mask2D)
        mask = np.transpose(mask, (2, 1, 0)) # transpose to match the stack dimensions


    # Cross-Spectral Density calculation
    Ik=fft.fftshift(fft.fftn(fft.fftshift(stackM)))
    Gamma=np.multiply(Ik,mask)          # cross-spectral density
    csd=fft.ifftshift(fft.ifftn(fft.ifftshift(Gamma)))
    csd = csd[:stackM.shape[0], :stackM.shape[1], :stackM.shape[2]]   # remove the mirrored input    
    QP = angle(csd + np.mean(np.ravel(stack)) / struct.optics_alpha)

    return QP,mask

    