# TomographicPhaseRetrieval - TomPhaseRetPy

TomPhaseRetPy is a tool to recover quantitative phase differences from a 3D stack of bright field images.
It leans on the Matlab script from "insert citation Descloux et al. 2019"
The main script contains a basic pipeline for QP retrieval from brightfield stacks
* 3D image stack loading
* 3D stack preprocessing
* processing parameters definition
* phase calculation
* display of the results 

## Installation

use git clone git@github.com:GrussmayerLab/TomographicPhaseRetrieval.git to clone the repoistory and access the source code

## Requirements 

## Usage

```python IDE 
qpmain is the primary script that can be run via the command line via python qpmain.py or in the IDE of choice. 
It access the utility scripts under /utilities. 

# input
A .tiff or .png stack containing at least two z-positions of the investigated object.

# returns 'QP'
QP is a 3D stack with the same dimensions of the input image stack, whereby each pixel represent the pathlength differences. 

## Contributing


## License
