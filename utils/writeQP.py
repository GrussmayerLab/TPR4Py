import numpy as np  
import skimage.io as skio
import os

def writeQP(QP, pathfile):
    fpath = os.path.dirname(pathfile[0])
    fname = os.path.basename(pathfile[0])
    # todo tifffile imwriting
    skio.imsave(os.path.join(fpath, f"QP_{fname}"), QP)

