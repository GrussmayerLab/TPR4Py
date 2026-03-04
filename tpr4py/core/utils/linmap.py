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
from __future__ import annotations
import numpy as np
from typing import Union

def linmap(
    val: np.ndarray,
    val_min: float | None = None,
    val_max: float | None = None,
    map_min: float = 0.0,
    map_max: float = 1.0,
) -> np.ndarray:
    """Scale *val* linearly from [val_min, val_max] → [map_min, map_max].

    If ``val_min``/``val_max`` are omitted they are inferred from ``val``.
    Values outside the source range are clipped to the target range.
    """
    if val_min is None:
        val_min = np.nanmin(val)
    if val_max is None:
        val_max = np.nanmax(val)

    # Normalise → [0, 1]
    norm = (val - val_min) / (val_max - val_min)
    norm = np.clip(norm, 0, 1)

    # Rescale
    return norm * (map_max - map_min) + map_min
