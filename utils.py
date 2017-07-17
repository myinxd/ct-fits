# Copyright (C) 2017 Zhixian MA <zxma_sjtu@qq.com>

"""
Utilities for dicom images processing

Requirements
============
astropy
pydicom
pandas
xlrd

References
==========
[1] pydicom documentation
https://pydicom.readthedoces.io/en/stable/working_with_pixel_data.html
[2] Read and write excel with pandas
http://blog.csdn.net/qq_24683561/article/details/54576520

Methods
=======
load_info(infopath="patient_list.xlsx")
    Load the patient names and identities
sort_filename(foldname)
    readjust filenames and sort
gen_fits(dcmpath,header=None)
    transform the dcm image to fits
gen_fits_cube(foldname, header=None)
    transform the group of dcm files into a cube
"""

import os
import dicom
import pandas as pd
import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt

def load_info(infopath):
    """
    Load the patient names and identities

    input
    =====
    infopath: str
        The path to save the info file.

    output
    ======
    namelist: dict
        The list hoding name and id of the patients
    """
    # load the excel
    try:
        p_list = pd.read_excel(infopath)
    except:
        print("Something wrong when loading the info file.")
        return None

    # sort
    idx = np.argsort(p_list['name'])
    p_name = p_list['name'][idx]
    p_name.index = np.arange(0, p_name.shape[0])
    p_id = p_list['id'][idx]
    p_id.index = np.arange(0, p_id.shape[0])

    # dict
    namelist = {'name': p_name, 'id': p_id}

    return namelist

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

def gen_fits(dcmname, header=None):
    """
    Transform dcm image to fits image

    inputs
    ======
    dcmname: str
        File path of the dcm image
    header: dict
        <TODO> The header of the fits file

    output
    ======
    hdu: astropy.io.fits.PrimarHDU
        The single image
    """
    # read the dcm image
    try:
        img_dcm = dicom.read_file(dcmname)
    except:
        print("Something wrong when read the dcm image.")
        return None

    # Initialize hdu
    hdu = fits.ImageHDU()
    if header is not None:
        hdu.header.update(header)
    hdu.data = np.flipud(img_dcm.pixel_array)

    return hdu

def save_fits(hdu, savepath):
    """Save the fits image"""
    hdu.writeto(savepath, clobber=True)

def gen_fits_cube(samplepath, header=None):
    """Generate the fits cube from dcm group

    inputs
    ======
    samplepath: str
        Path of the sample folder
    header: dict
        The header of the fits file

    output
    ======
    cube_hdu: astropy.io.fits.PrimaryHDU
        The fits cube
    """
    # Init a hdu cube
    cube_hdu = fits.ImageHDU()

    # load single extension
    fitslist = sort_filename(samplepath)
    fitslist = fitslist[1:]

    # Initialize the data cube
    data_cube = []

    for f in fitslist:
        # print("Processing on dcm %s " % f[0:-4])
        dcmpath = os.path.join(samplepath,f)
        try:
            img_dcm = dicom.read_file(dcmpath)
        except:
            print("Cannot load dcm %s." % f)
            continue

        data_cube.append(np.flipud(img_dcm.pixel_array))

    cube_hdu.data = np.array(data_cube)
    if header is not None:
        cube_hdu.header.update(header)

    return cube_hdu

def gen_infodict(namelist,keys_idx,p_idx):
    """Genearte the info dict"""
    infodict = []
    for kid in keys_idx:
        key = namelist.keys()[kid]
        value = str(namelist[key][p_idx])
        temp_dict = key + ": " + value
        infodict.append(temp_dict)

    return infodict

def gen_mark_image(infodict,savepath,imgshape=(128,128)):
    """Generate blank image with info marked."""
    # Init
    img = np.zeros(imgshape,dtype='uint8')

    fig = plt.figure(figsize=(imgshape[0]/10,imgshape[1]/10))
    ax = plt.subplot(111)
    ax.imshow(img,cmap='Greys')
    # mark text
    x0 = 0
    y0 = 0
    step = 15
    for info_text in infodict:
        y0 = y0 + step
        ax.text(x0, y0, info_text,fontsize=60)

    plt.box('off')
    ax.set_xticks([])
    ax.set_yticks([])
    # save
    fig.savefig(savepath, dpi=10)
