"""
[im,pname,fname] = loadData(path);
---------------------------------------

Basic function to load tif data stack from a specified path
If no path are provided, the user can manually select the data

Inputs:
  path         Full path of the data

Outputs:
  im        	Data stack
  pname        Path name
  fname        File name

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
import tkinter as tk
from tkinter import filedialog
import numpy as np  
import skimage.io as skio

def loadData(path=None):
    if path is None:
        root = tk.Tk()
        root.withdraw()
        filenames = filedialog.askopenfilenames()
        im_ = skio.imread(filenames[0])
        print("Files retrieved from {}".format(filenames[0]))
    else: 
        #filenames = os.path.basename(path)
        # TODO: load both stacks and multiple single plane images in same structure
        filenames = path
        print("Files retrieved from {}\nFilenames[0]: {}".format(path, filenames[0]))
        im_ = np.array(skio.imread(filenames, plugin='tifffile'))
        
    dims = im_.shape
    z_dim = len(filenames)
    if len(dims) < 2:  # check if multiple single images or image stack loaded
        z_dim = dims[2]
    
    image_batch = np.empty((z_dim, dims[0], dims[1], dims[2]), dtype=np.uint16) #dtype=np.uint8
    for idx, file in enumerate(filenames):
        try:
            img = skio.imread(file, plugin="tifffile")
            # if img is of different width and height than defined above
            # do some resize and then insert in the array.
            image_batch[idx] = img
        except ValueError or OSError as error:
            print('File {:s} failed due to {:s}'.format(file, error))
    
    image_batch = image_batch.squeeze()      
    print("Finished reading... /nStack size: {}".format(image_batch.shape))
    return image_batch, filenames
            
        
if __name__ == '__main__':
    loadData()
