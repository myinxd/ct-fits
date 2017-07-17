# Copyright (C) 2017 Zhixian MA <zxma_sjtu@qq.com>

"""
Batchly generating fits cubes of the patient samples
"""

import os
import argparse

import utils

def main():

    # Init
    parser = argparse.ArgumentParser(
        description="Batchly generating fits cubes of the patient samples.")
    # Parameters
    parser.add_argument("foldname", help="Path of the patients")
    parser.add_argument("foldsave", help="Path to save the MEF image")
    parser.add_argument("infopath", help="Path of the info file.")
    args = parser.parse_args()

    foldname = args.foldname
    foldsave = args.foldsave
    infopath = args.infopath

    # load patients info and sort
    print("Loading patients info.")
    namelist = utils.load_info(infopath=infopath)

    # load samples' folder names from foldpath
    samplelist = os.listdir(foldname)
    samplelist.sort()

    # Generate cubes
    # samplelist = samplelist[0:2]
    for i in range(len(samplelist)):
        s = samplelist[i]
        print("Processing on patient %s " % s)
        samplepath = os.path.join(foldname, s)
        # load dcmpath
        # dcmlist = utils.sort_filename(samplepath)
        # generate fits cube
        cube_hdu = utils.gen_fits_cube(samplepath=samplepath)
        # save
        savename = str(namelist['id'][i]) + '_cube.fits'
        savepath = os.path.join(foldsave, savename)
        utils.save_fits(hdu=cube_hdu, savepath=savepath)


if __name__ == "__main__":
    main()
