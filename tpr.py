import numpy as np
from copy import copy
from tqdm import tqdm 
import math



class TopographicPhaseRetrieval: 

    def linmap(self, val=None,valMin=None,valMax=None,mapMin=None,mapMax=None,*args):

        if len(*args) == 3:
            mapMax=valMax
            mapMin=valMin
            valMin=min(np.ravel(val))
            valMax=max(np.ravel(val))
        
        # convert the input value between 0 and 1
        tempVal=(val - valMin) / (valMax - valMin)
        # clamp the value between 0 and 1
        map0=tempVal < 0
        map1=tempVal > 1
        tempVal[map0]=0
        tempVal[map1]=1

        # rescale and return
        rsc=np.multiply(tempVal,(mapMax - mapMin)) + mapMin
        return rsc
    

    def map3D(self, in_=None):
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


    def qpmain(self, stack, s):
        Ny,Nx,Nz,Nt = stack.shape

        # set experimental parameters
        if Nz == 4:              # i.e. MultiPlane data
            s.optics_dz = 0.62     
            if Ny is not Nx:          # [um]
                stack=self.cropXY(stack)
        else:
            s.optics_dz = 0.2 
            if Ny is not Nx:   
                stack=self.cropXY(stack)

        #phase_structure.summarise(s)
        phase = iterate_getQP(stack, Nt, s)
        return phase
 
    #@jit(nopython=True)   
    def iterate_getQP(self, stack, Nt, s):
        phase = np.empty(stack.shape, np.float64)
        inner = tqdm(total=Nt, desc='phase - timepoint', position=0)
        mask = self.precompute_mask(stack, s)
        for timepoint in range(Nt):
            phase[:,:,:,timepoint], _ = self.getQP(stack[:,:,:,timepoint], s, mask)
            inner.update(1)
        return phase 


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

        
    def clamp(self, val=None,minval=None,maxval=None):
        if not minval: # no lower bound
            mapmax=val > maxval
            val[mapmax]=maxval
        
        if not maxval: # no upper bound
            mapmin=val < minval
            val[mapmin]=minval    
        if np.logical_not(minval is None) and np.logical_not(maxval is None):
            mapmax=val > maxval
            val[mapmax]=maxval
            mapmin=val < minval
            val[mapmin]=minval

    def cropCoregMask(self, stack=None):

        temp = stack != 0
        mask = sum(temp,1)
        mask = (mask == 8)
        
        [Nx,Ny,_] = stack[0].shape
        masky=(sum(mask,3) / Ny > 0.5)

        ay=masky.index(max(masky))
        by=masky[-1:None:-1].index(max(masky))
        by=len(masky) - by + 1
        
        maskx=(sum(mask,2) / Nx > 0.5)
        ax=maskx.index(max(maskx))
        bx=maskx[-1:None:-1].index(max(maskx))
        bx=len(maskx) - bx + 1
        
        temp_nPix=min(bx - ax + 1,by - ay + 1)
        stack = stack[ay:(temp_nPix - 1 + ay),ax:(temp_nPix + ax - 1),:]
        return stack

    def cropXY(self, input_=None,N=None):
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

  
    def getMirroredStack(self, stack=None,s=None,*args,**kwargs):

            Nx,Ny,Nz=stack.shape
            
            if Nx != Ny:                     # verify that the stack is square
                stack=self.cropXY(stack)          # if not, crop it
            
            # compute real space
            x=np.linspace(np.dot(- Nx,s.optics_dx) / 2,np.dot(Nx,s.optics_dx) / 2,Nx)
            z=np.linspace(np.dot(- Nz,s.optics_dz) / 2,np.dot(Nz,s.optics_dz) / 2,Nz)
            # mirror z-stack
            temp=copy(stack)
            if s.proc_mirrorZ:
                t=copy(temp)
                t = np.append(t,temp[:, :, ::-1], 2)
                temp=copy(t)
                kz=np.multiply(np.dot(2,np.pi) / (max(z) - min(z)),np.linspace(- Nz / 2,(Nz - 1) / 2,np.dot(2,Nz)))
            else:
                if np.mod(Nz,2):
                    kz=np.multiply(np.dot(2,np.pi) / (max(z) - min(z)),np.linspace(- Nz / 2,Nz / 2,Nz))
                else:
                    kz=np.multiply(np.dot(2,np.pi) / (max(z) - min(z)),np.linspace(- Nz / 2,Nz / 2 - 1,Nz))
                    
            # mirror x dim
            if s.proc_mirrorX:
                t=copy(temp)
                t = np.concatenate((t,temp[::-1,:, :]),0)
                temp = np.concatenate((t, t[:,::-1,:]),1)
                #t[Nx:,:,:] = t[:Nx:-1,:,:]
                #t = np.concatenate((t,flip))
                #temp=copy(t)
                kx=np.multiply(np.dot(2,np.pi) / (max(x) - min(x)),np.linspace(- Nx / 2,(Nx - 1) / 2,np.dot(2,Nx)))
            else:
                if np.mod(Nz,2):
                    kx=np.multiply(np.dot(2,np.pi) / (max(x) - min(x)),np.linspace(- Nx / 2,Nx / 2,Nx))
                else:
                    kx=np.multiply(np.dot(2,np.pi) / (max(x) - min(x)),np.linspace(- Nx / 2,Nx / 2 - 1,Nx))
            stackM = temp
            
            return kx,kz,stackM

    #@jit(nopython=True)   
    def getQP(self, stack=None,struct=None,mask=None):

        # mirror the data and compute adequate Fourier space grid
        kx,kz,stackM = self.getMirroredStack(stack,struct)
        
        if mask is None: # if no mask is provided
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
            #np.save("data\mask3D.npy", mask)

        # Cross-Spectral Density calculation
        #print("Shifting FFT..")
        Ik=np.fft.fftshift(np.fft.fftn(np.fft.fftshift(stackM)))
        Gamma=np.multiply(Ik,mask)          # cross-spectral density
        #print("Inverse FFT..")
        csd=np.fft.ifftshift(np.fft.ifftn(np.fft.ifftshift(Gamma)))
        csd = csd[:stack.shape[0], :stack.shape[1], :stack.shape[2]]   # remove the mirrored input    
        QP = np.angle(csd + np.mean(np.ravel(stack)) / struct.optics_alpha)

        return QP,mask