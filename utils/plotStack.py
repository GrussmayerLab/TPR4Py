"""
plotStack(data,figID)
-------------------------
Opens a basic gui that allows simplified navigation through 3D data stacks
if figID is specified, first close(figID), then create figure(figID)
if figID is not specified, open a new figure

Inputs:
   data        Data stack [X Y Z]
   figID       Figure ID,  if set, close(figID),then create figure(figID)
                           if not set, open new figure

Outputs:
   s           Structure containing experimental and processing parameters

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

import napari

def plotStack(data=None, figID=None, *args,**kwargs):
    napari.view_image(data, axis_labels=["x","y","z"], name=str("QP_" + figID)) 

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
