"""
out = cropXY(input,N)
---------------------------------------
    
This function crop the input 3D stack to have the size [N,N,~]
if N > than Nx or Ny/ not given, it make sure that the resulting image is square
    
    Inputs:
  input        2D/3D data
  N            Size of the cropped image
              if not set, crop the image to min(size(N,1),size(N,2))
Outputs:
  out        	Cropped data
    
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
from copy import copy 
    
def cropXY_old(input_=None,N=None):
    print("Cropping..")
    Nx,Ny,_=input_.shape
    if N is None:
        N=max(Nx,Ny) + 1
        
    if N > max(Nx,Ny): # invalid/ missing input N => square the stack
        if Nx != Ny:
            N=min(Nx,Ny)
            ox=int(np.floor((Nx - N) / 2))
            oy=int(np.floor((Ny - N) / 2))
            out=input_[ox:ox+N-1,oy:oy+N-1,:]      # beware matlab indexing
        else:
            out=copy(input_)
    else:
        ox=int(np.floor((Nx - N) / 2))
        oy=int(np.floor((Ny - N) / 2))
        out=input_[ox:ox+N, oy:oy+N,:]
    print("Cropping finished")
    return out
    

    
def cropXY(input_=None,N=None):
    print("Cropping..")
    
    size = input_.shape
    if len(size) == 3:
        D_FLAG = True
        Nx,Ny,Nz =input_.shape
    elif len(size) == 4:
        D_FLAG = False
        Nx,Ny,Nz,Nt =input_.shape
        
    if N is None:
        N=max(Nx,Ny)+1
        
    if N > max(Nx,Ny): # invalid/ missing input N => square the stack
        if Nx != Ny:
            N=min(Nx,Ny)
            ox=int(np.floor((Nx - N) / 2))
            oy=int(np.floor((Ny - N) / 2))
            if D_FLAG:
                out=input_[ox:ox+N,oy:oy+N,:]      # beware matlab indexing
            else: 
                out=input_[ox:ox+N,oy:oy+N,:, :] 
        else:
            out=copy(input_)
    else:
        ox=int(np.floor((Nx - N) / 2))
        oy=int(np.floor((Ny - N) / 2))
        if D_FLAG:
            out=input_[ox:ox+N, oy:oy+N,:]
        else: 
            out=input_[ox:ox+N, oy:oy+N,:, :]
    print("Cropping finished")
    return out
    
#if __name__ == '__main__':
#    pass
    

