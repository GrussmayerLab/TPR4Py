"""
rsc = linmap(val,valMin,valMax,mapMin,mapMax)
---------------------------------------

Map the variable val from the range [valMin valMax] to 
the range [mapMin mapMax]

Inputs:
  val          Input value
  valMin       Minimum range of input value "val"
  valMax       Maximum range of input value "val"
  mapMin       Minimum of mapping range
  mapMax       Maximum of mapping range

Outputs:
  rsc        	Rescaled value

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
from numpy import ravel, multiply

def linmap(val=None,valMin=None,valMax=None,mapMin=None,mapMax=None,*args):
    nargin = linmap.nargin

    if nargin == 3:
        mapMax=valMax
        mapMin=valMin
        valMin=min(ravel(val))
        valMax=max(ravel(val))
    
    # convert the input value between 0 and 1
    tempVal=(val - valMin) / (valMax - valMin)
    # clamp the value between 0 and 1
    map0=tempVal < 0
    map1=tempVal > 1
    tempVal[map0]=0
    tempVal[map1]=1

    # rescale and return
    rsc=multiply(tempVal,(mapMax - mapMin)) + mapMin
    return rsc
    
if __name__ == '__main__':
    pass
