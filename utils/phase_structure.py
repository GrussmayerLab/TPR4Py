"""
  s = setup_phase_default;
  ---------------------------------------

  this file return a structure required for Quanatitative Phase reconstruction

  Inputs:
  -

  Outputs:
  s        Structure containing experimental and processing parameters

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

class phase_structure: 
    
    def __init__(self):
        self.optics_dx = 0.1067
        self.optics_dz = 0.1          # axial sampling [um]
        self.optics_NA = 1.3          # Numerical Aperture detection (Olympus 60x silicone objective UPLSAPO60XS2) 
        self.optics_NA_ill = 0.55     # Numerical Aperture illumination (Olympus IX2-LWUCD condenser)
        #self.optics_NA_ill = 0.26     # EPFL setup empirically determined
        #self.optics_NA_ill = 0.5     # TUD setup optimisation, Olympus IX2-LWUCD condenser
        self.optics_n = 1.406          # refractive index (Olympus silicone) 
        self.optics_wv = 0.58          # Central wavelength in vacuum/ WAS optics.lambda (py internal command)
        self.optics_dlambda = 0.075   # Spectrum bandwidth
        self.optics_alpha = 4.21      # Experimental coefficient for QP "normalisation" optimised for TUD/MCL setup
        self.optics_kzT = 0.01        # Axial cutoff frequency.
                                        # if set to [], use the theoretical value
    ### Practical note : Inacurate values of illumination NA and source spectrum
    # in conjunction with coarse z-sampling may lead to an overestimation of
    # the axial cutoff if the theoretical value is used.
    # Best practice is to use a small value > 0
    
        # processing parameters
        self.proc_mirrorX = False            # mirror the input stack along X 
        self.proc_mirrorZ = True             # mirror the input stack along Z
        self.proc_applyFourierMask = True    # apply the denoising Fourier mask
                                    
                           
    def summarise(self):
        print("Phase structure: \n_________________")
        print(f"s.optics_dx = {self.optics_dx} \t \t s.optics_wv = {self.optics_wv}")
        print(f"s.optics_dz = {self.optics_dz} \t \t s.optics_dlambda = {self.optics_dlambda}")
        print(f"s.optics_NA = {self.optics_NA} \t \t s.optics_alpha = {self.optics_alpha}")
        print(f"s.optics_NA_ill = {self.optics_NA_ill} \t \t s.optics_kzT = {self.optics_kzT}")
        print(f"s.optics_n = {self.optics_n}")
        print("Processing paramters: \n_________________")
        print(f"s.proc_mirrorX = {self.proc_mirrorX} \t \t s.proc_mirrorZ = {self.proc_mirrorZ}")
        print(f"s.proc_applyFourierMask = {self.proc_applyFourierMask}")
        
        





