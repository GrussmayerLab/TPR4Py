# -*- coding: utf-8 -*-
# out = map3D(in);
# ---------------------------------------

# map a kz,klat 2D CTF into its kx,ky,kz 3D circular symetric counterpart

# Inputs:
#   in          2D image [kz klat] (klat=sqrt(kx^2+ky^2);)

# Outputs:
#   out         3D circular symetric [kx,ky,kz]

# ---------------------------------------
# A detailled description of the theory supporting this program can be found in : 
# "Descloux, A., et al. "Combined multi-plane phase retrieval and 
#  super-resolution optical fluctuation imaging for 4D cell microscopy." 
#  Nature Photonics 12.3 (2018): 165."

#   Copyright © 2018 Adrien Descloux - adrien.descloux@epfl.ch, 
#   École Polytechnique Fédérale de Lausanne, LBEN/LOB,
#   BM 5.134, Station 17, 1015 Lausanne, Switzerland.

#  	This program is free software: you can redistribute it and/or modify
#  	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
#  	(at your option) any later version.

#  	This program is distributed in the hope that it will be useful,
#  	but WITHOUT ANY WARRANTY; without even the implied warranty of
#  	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  	GNU General Public License for more details.

# 	You should have received a copy of the GNU General Public License
#  	along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    
#

import numpy as np
from scipy.ndimage import rotate

def map3D(in_=None,*args,**kwargs):
    np.save("data\in.npy", in_)
    Nz, Nx =in_.shape
    
    temp_x = np.linspace(- 1,1,Nx)
    temp_z = np.linspace(- 1,1,Nz)

    tX,tY = np.meshgrid(temp_x,temp_x)

    r = np.sqrt(tX ** 2 + tY ** 2)

    r[r > np.max(temp_x)]=np.max(temp_x)
    
    mapr=np.multiply(np.divide(r - np.min(temp_x),(np.max(temp_x) - np.min(temp_x))),(len(temp_x) - 2)) 
    mapf=np.floor(mapr) + 1
    mapc=np.ceil(mapr) + 1
    np.save("data\mapr.npy", mapr)
    np.save("data\mapf.npy", mapf)
    np.save("data\mapc.npy", mapc)
    #np.save("data\rpy.npy", np.asarray(r))

    p=mapc - mapr - 1
    np.save("data\p.npy", p)
    
    out=np.zeros((temp_x.shape[0],temp_x.shape[0], temp_z.shape[0]))
    CTF_temp = np.zeros((len(temp_z),mapf.shape[0], mapf.shape[1])) # remove when done
    
    ###
    X = np.linspace(0,Nx,Nx)
    Y = np.linspace(0,Nx,Nx)
    x, y = np.meshgrid(X, Y)
    c_lat = Nx/2
    #polargrid = np.round(np.sqrt((x-c_lat)**2+(y-c_lat)**2))
    polargrid = np.sqrt((x-c_lat)**2+(y-c_lat)**2)
    ###
    for kk in range(len(temp_z)):
        print(kk)
        CTF1D= in_[kk,:]  # < 0      # extract the 1D psf = 1xNx boolean        
        CTF2D = np.zeros((Nx,Nx))    #  < 0 cast to boolean
        #############################
        # create circles form radii & superimpose to 2d mask from 1d psf
        #if any(CTF1D):
        #    radii = np.unique(np.abs(np.subtract(np.nonzero(CTF1D)[0],c_lat)))
        #    for r in radii:
        #        mask = (polargrid == float(r))
        #        CTF2D = np.logical_or(CTF2D, mask) 
        ############################
        """
        if any(CTF1D):
            radii = np.unique(np.abs(np.subtract(np.nonzero(CTF1D)[0],c_lat)))
            for r in radii:
                mask = np.logical_and(polargrid <= r+.5 , polargrid >= r-.5)

                CTF2D = np.logical_or(CTF2D, mask) 
        """
        ############################
        if any(CTF1D):
            radii = np.unique(np.abs(np.subtract(np.nonzero(CTF1D)[0],c_lat)))
            for r in radii[1:]:
                mask_coords = np.logical_and(polargrid <= r+1 , polargrid >= r-1)
                dist_pxl = np.subtract(np.ones((Nx,Nx)),np.abs((polargrid*mask_coords) - np.round(r)))
                mask = dist_pxl*mask_coords
                CTF2D = np.add(CTF2D, mask) 
        ###########################
        
        CTF_temp[kk,:,:] = CTF2D  # remove when done
        #tempf = np.logical_and(CTF2D,mapf) 
        #print("max min tempf: {} {}".format(np.max(tempf), np.min(tempf)))
        #tempc = np.logical_and(CTF2D,mapc)
        # local linear interpolation
        #temp = np.multiply(p,tempf) + np.multiply((1 - p),tempc)

        #out[:,:,kk]=temp
        out[:,:,kk]=CTF2D

    np.save("data\CTF2D.npy", CTF_temp)
    return out
    
if __name__ == '__main__':
    pass
    

