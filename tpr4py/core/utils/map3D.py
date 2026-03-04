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

def map3D(mask2d: np.ndarray) -> np.ndarray:
    """Expand a 2‑D radial CTF mask to a 3‑D isotropic mask."""
    nz, nx = mask2d.shape
    r = np.linspace(-1, 1, nx)
    x, y = np.meshgrid(r, r, indexing="ij")
    radius = np.sqrt(x**2 + y**2)
    radius = np.clip(radius, -1, 1)

    # Convert radius → nearest integer index in the 2‑D mask
    idx = np.round(((radius - r.min()) / (r.max() - r.min())) * (nx - 2)).astype(int)
    idx = np.clip(idx, 0, nx - 1)

    # Broadcast across the z‑dimension
    out = mask2d[np.arange(nz)[:, None, None], idx]
    return out.astype(float)
    

def map3D_old(in_: np.ndarray) -> np.ndarray:
    Nz, Nx =in_.shape
    temp_x = np.linspace(-1,1,Nx)
    temp_z = np.linspace(-1,1,Nz)
    
    x, y = np.meshgrid(temp_x, temp_x)
    r=np.sqrt(x**2+y**2)
    r[r>np.max(temp_x)] = np.max(temp_x)
    
    
    #c_lat = Nx/2
    # create grid of float radial pixel distances to center coordinate of Nx,Nx grid
    #polargrid = np.sqrt((x-c_lat)**2+(y-c_lat)**2) # np.round for int distances 
    
    mapr = (r-np.min(temp_x))/(np.max(temp_x)-np.min(temp_x))*(len(temp_x)-2) #-2
    mapf = np.floor(mapr)+1
    mapc = np.ceil(mapr)+1
    p = mapc-mapr-1
    
    out=np.zeros((Nx,Nx,Nz))

    for kk in range(Nz):
        CTF1D= in_[kk,:]  # < 0      # extract the 1D psf = 1xNx boolean        
        tempf = np.isin(mapf, np.add(1,np.where(CTF1D == 1)[0]))
        tempc = np.isin(mapc, np.add(1,np.where(CTF1D == 1)[0]))
        
        # local linear interpolation 
        temp = p*tempf + (1-p)*tempc

        out[:,:,kk]=temp

    return out