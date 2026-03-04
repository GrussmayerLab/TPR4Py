import numpy as np
import math

def precompute_mask(self, stack, struct):
    # mirror the data and compute adequate Fourier space grid
    kx,kz,stackM = self.getMirroredStack(stack,struct)

    # compute usefull stuff
    th=math.asin(struct.optics_NA / struct.optics_n)
    th_ill=math.asin(struct.optics_NA_ill / struct.optics_n)
    k0max = np.dot(np.dot(struct.optics_n,2),np.pi) / (struct.optics_wv - struct.optics_dlambda / 2) 
    k0min = np.dot(np.dot(struct.optics_n,2),np.pi) / (struct.optics_wv + struct.optics_dlambda / 2) 
    
    # compute Fourier space grid and the phase mask
    Kx,Kz=np.meshgrid(kx,kz)
    if struct.optics_kzT is None:
        mask2D = Kz >= np.dot(k0max,(1 - np.cos(th_ill)))
    else:
        mask2D = Kz >= struct.optics_kzT


    if struct.proc_applyFourierMask:  #  => compute the CTF mask for extra denoising
        # CTF theory
        maskCTF = np.logical_and(np.logical_and(np.logical_and(
            ((Kx - np.dot(k0max,np.sin(th_ill))) ** 2 + (Kz - np.dot(k0max,np.cos(th_ill))) ** 2) <= k0max ** 2, \
                ((Kx + np.dot(k0min,np.sin(th_ill))) ** 2 + (Kz - k0min) ** 2) >= k0min ** 2), Kx >= 0), \
                Kz < np.dot(k0max,(1 - np.cos(th))))            
        maskCTF = np.logical_or(maskCTF,maskCTF[:,::-1])
        mask2D = np.asanyarray(np.logical_and(mask2D,maskCTF), dtype=int)
    # since we assume a circular symetric CTF, we expand the 2Dmask in 3D
    mask=self.map3D(mask2D)
    return mask