# TomographicPhaseRetrieval - TomPhaseRetPy

TomPhaseRetPy is a tool to recover quantitative phase differences from a 3D stack of bright field images.
It leans on the Matlab script from "insert citation Descloux et al. 2019"
The main script contains a basic pipeline for QP retrieval from brightfield stacks
* 3D image stack loading
* 3D stack preprocessing
* processing parameters definition
* phase calculation
* display of the results (optional, conducted via napari) 

## Installation
Via command line:
'''git clone git@github.com:GrussmayerLab/TomographicPhaseRetrieval.git'''
clones into the repository to and gives access to the source code on your local machine

Ideally a separate environment is set up and dependencies installed. 
### Processing only 
''' pip install -r requirements.txt '''
This basically sets up the necessary scikit-image and numpy modules. 
Visualisation is not possible with these modules. 

### Visualisation inlcuded 
To display the 3D phase map, install the requirements via 
''' pip install -r requirements_detailed.txt '''
This initialises napari version 0.4.12 that enables a powerful n-dimensional image processing and visualisation toolbox.


## Requirements
 * sci-kit image == 0.19.2
 * numpy == 1.12.5
 (* napari == 0.4.12 -> only necessary when you want to view the 3D phase map)
 
## Usage
 
* qp_main.py is the main script that can be run in the IDE of choice. It accesses the utility scripts under /utilities. 

# input
A .tiff or .png stack containing at least two z-positions of the investigated object.

# returns 'QP'
A 3D stack with the same dimensions as the input image stack, wherein each pixel represent the pathlength differences. 

## Contributing
A detailled description of the theory supporting this program can be found in : "Descloux, A., et al. "Combined multi-plane phase retrieval and super-resolution optical fluctuation imaging for 4D cell microscopy." Nature Photonics 12.3 (2018): 165.
The script was originally designed by the authors in matlab. 
The adaption to python 3 was conducted by Moritz Engelhardt, Grussmayer Lab TU Delft (2022). 
## License
Copyright © 2018 Adrien Descloux - adrien.descloux@epfl.ch, École Polytechnique Fédérale de Lausanne, LBEN/LOB, BM 5.134, Station 17, 1015 Lausanne, Switzerland.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.