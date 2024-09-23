# TSM-to-ZDA
Originally, this application reads in TurboSM data files (.tsm, .tbn), bins to an image size that the original C++-only PhotoZ can handle, translates or fills in metadata, and writes a legacy ZDA file
While this is the core functionality, features have expanded to automate data collection, conversion, and export.

## User Manual
[OrchZ User Manual]([url](https://docs.google.com/document/d/13jKigNSDtpZ_gP7-GxjhCbAx95AXcjIO4ldb4gicgj0/edit?usp=sharing))

## Instructions

Clone and install conda environment.
```
git clone https://github.com/john-judge/TSM-to-ZDA.git
cd TSM-to-ZDA
conda env create -f environment.yml -n TSM_to_ZDA
conda activate TSM_to_ZDA
jupyter notebook
```

Jupyter will open in browser. Open the ipynb file.

Adjust filename and directory as needed. Default binning and cropping should work well for DaVinci recordings and original PhotoZ.
As of 5/27/22, output is simply hardcoded as `output.zda` in the current directory.

## Caveats
https://github.com/john-judge/PhotoZ_upgrades/tree/load-hacked-zda is a version of PhotoZ created for testing with this script and is known to be compatible. This version ignores some PhotoZ validation such as version and bit-depth, which do not need to be written correctly for the data to load properly. This version also includes an initially high but adjustable binning setting in PhotoZ to avoid performance issues.

PhotoZ only plays nicely with ZDA files containing square images (i.e. where width equals height).

Binning is high for large images to avoid performance and memory issues in PhotoZ.
