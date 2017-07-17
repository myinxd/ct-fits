# Copyright (C) 2017 Zhixian MA <zxma_sjtu@qq.com>

"""
Create multi-extension FITS (MET) files

References
==========
[1] FITS Cube
https://ds9.si.edu/doc/ref/file.html#FITSMultipleExtensionDataCube
[2] Create a multi-extension FITS (MEF) file from scratch
https://docs.astropy.org/en/stable/generated/examples/io/create-mef.html#
sphx-glr-generated-examples-io-create-mef-py
"""

import os
import numpy as np
import argparse
from astropy.io import fits

def sort_filename(foldname):
    """
    readjust filenames and sort
    """
    try:
        filelist = os.listdir(foldname)
    except:
        print("Folder %s does not exist." % foldname)
        return None

    # first sort
    filelist.sort()
    numfiles = len(filelist)
    filesort = ['' for n in range(numfiles)]

    for f in filelist:
        f_split = f.split('.')
        idx = int(f_split[-2]) - 1
        filesort[idx] = f

    return filesort

def main():

    # Init
    parser = argparse.ArgumentParser(
        description="Create multi-extension FITS cube.")
    # Parameters
    parser.add_argument("foldname", help="Path of the fits extensions.")
    parser.add_argument("foldsave", help="Path to save the MEF image.")
    args = parser.parse_args()

    foldname = args.foldname
    foldsave = args.foldsave

    # Init a new hdu
    cube_hdu = fits.ImageHDU()
    cube_hdu.name = foldname.split('/')[-2]

    # load single extension
    fitslist = sort_filename(foldname)

    # Initialize the data cube
    data_cube = []

    for f in fitslist:
        print("Processing on image %s " % f[0:-4])
        fitspath = os.path.join(foldname,f)
        temp_hdu = fits.open(fitspath)
        temp_data = temp_hdu[0].data
        data_cube.append(temp_data)

    # save
    cube_hdu.data = np.array(data_cube)
    savename = foldname.split('/')[-2] + '_cube.fits'
    print(savename)
    savepath = os.path.join(foldsave, savename)
    cube_hdu.writeto(savepath, overwrite=True)

if __name__ == "__main__":
    main()
