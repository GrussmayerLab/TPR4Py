""" 
out = map3D(in);
---------------------------------------

map a kz,klat 2D CTF into its kx,ky,kz 3D circular symetric counterpart

Inputs:
  in          2D image [kz klat] (klat=sqrt(kx^2+ky^2);)

Outputs:
  out         3D circular symetric [kx,ky,kz]

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

def map3D(in_=None):
    Nz, Nx =in_.shape
    out=np.zeros((Nx,Nx,Nz))
    x, y = np.meshgrid(np.linspace(0,Nx,Nx), np.linspace(0,Nx,Nx))
    c_lat = Nx/2
    # create grid of float radial pixel distances to center coordinate of Nx,Nx grid
    polargrid = np.sqrt((x-c_lat)**2+(y-c_lat)**2) # np.round for int distances 

    for kk in range(Nz):
        CTF1D= in_[kk,:]  # < 0      # extract the 1D psf = 1xNx boolean        
        CTF2D = np.zeros((Nx,Nx))    # initialise mask plane 

        # create circles from radii & superimpose to 2d mask from 1d psf
        if any(CTF1D):
            radii = np.unique(np.abs(np.subtract(np.nonzero(CTF1D)[0],c_lat)))
            for r in radii[1:]: # leave out first radius (improves superposition with .mat mapping, not sure why though)
                mask_coords = np.logical_and(polargrid <= r+1 , polargrid >= r-1)   # mask  
                dist_pxl = np.subtract(np.ones((Nx,Nx)),np.abs((polargrid*mask_coords) - np.round(r)))
                mask = dist_pxl*mask_coords
                CTF2D = np.add(CTF2D, mask) 

        out[:,:,kk]=CTF2D

    return out
    
if __name__ == '__main__':
    pass
    

