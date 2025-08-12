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

# bf loader
from os import listdir, getcwd
from os.path import isfile, join, exists, normpath
from skimage import io
import tifffile as tiff
import sys
import tkinter as tk
from tkinter import filedialog as tkFileDialog
from collections import OrderedDict
#%matplotlib inline
import javabridge as jv
import bioformats as bf
import numpy as np
import xml
import xml.etree.ElementTree as ET
import os
import tifffile as tf
import progressbar


def loadDataOld(path=None):
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
    print("Finished reading... \nStack size: {}".format(image_batch.shape))
    return image_batch, filenames
    
    
def loadData(path=None, filetype = "tiff", Z = None, T = None):
    

    jv.start_vm(class_path=bf.JARS, max_heap_size="8G")
    
    if path is None:
        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askopenfilename()
    else: 
        filename = path
    if Z is None or T is None:
        root=tk.Tk()
        root.withdraw()
        Z = tk.simpledialog.askinteger(title="Insert z-planes", prompt="IntegerInput z-points \n min = 1 ")
        T = tk.simpledialog.askinteger(title="Insert timepoints", prompt="IntegerInput t-points \n min = 1")
        root.destroy()
    
    #files = [f for f in listdir(path) if isfile(join(path, f)) and
    #         f.endswith(filetype) and 
    #         not (f.endswith("json") or f.endswith("txt"))]   
    image_batch = []
    #with bf.ImageReader(filename) as reader:
    #    image_batch.append(reader.read())
    for z in range(Z):
        t_stack = []
        for t in range(T):
            t_stack.append(bf.load_image(filename, z = z, t = t))
        image_batch.append(np.array(t_stack))
  
    # determine order for permutating 
    #order = defaul 
    image_batch = np.array(image_batch).squeeze() 
    
    if len(image_batch.shape) == 4:
        image_batch = np.transpose(image_batch, (2,3,0,1))
     
    return  image_batch, filename



def writeData(QP, path, filename): 
    outputImageFileName = os.path.join(path, f"QP_{filename}")    
    if len(QP.shape) == 4:
        QP = np.transpose(QP, (2,1,0,3))
        print("4d")
        axes = 'ZYXT'
    else: 
        QP = np.transpose(QP, (2,1,0))
        print("3d")
        axes = "ZXY"
    print(QP.shape)
    tf.imwrite(
        outputImageFileName,
        QP,
        resolution=(0.1083, 0.1083),
        metadata={ 
            'spacing': 0.720,
            'unit': 'nm',
            'finterval': 1,
            'axes': axes
        })

    print(f"writing QP stack {outputImageFileName} finished.")
    


def selectparamterZ(): 
    root=tk.Tk()
    root.withdraw()
    intUserInput = tk.simpledialog.askinteger(title="Select  dimensions of Z dimension [0,1,2,3]", prompt="integerInputPlease")
    root.destroy()
    return intUserInput

def selectparamterT(): 
    root=tk.Tk()
    root.withdraw()
    intUserInput = tk.simpledialog.askinteger(title="Select  dimensions of T dimension [0,1,2,3], other than Z", prompt="integerInputPlease")
    root.destroy()
    return intUserInput





#if __name__ == '__main__':
#    loadData()
