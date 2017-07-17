# Copyright (C) 2017 Zhixian MA <zxma_sjtu@qq.com>

"""
Transform the fits image to jpeg form after some preprocessings,
so as to generate images for the paper required.

Three images are prepared
1. cropped region under cmap b {id}_b.jpeg
2. cropped region under cmap gray invert {id}_i.jpeg
3. cropped region under cmap b with mannualy contrast adjusted. {id}_a.jpeg

Reference
=========
ds9 command line options: http://ds9.si.edu/doc/ref/command.html
"""

import os
import pandas as pd
import numpy as np
import argparse
from scipy import misc

import utils

class ParamDS9():
    """
    A class to generate ds9 command line options

    example
    =======
    >>> optdict = {
                "cmap": "Heat",
                "smooth": "radius 4",
                "zoom": "to 3",
                }
    >>> opt = ParamDS9(optdict=optdict)
    >>> cmd_line = opt.gen_cmd(filepath="ds9.fits")
    """

    def __init__(self, optdict=None):
        self.optdict = optdict
        self.gen_opt()

    def gen_opt(self):
        """Generate the ds9 command line options"""

        # Init
        self.optlist = []
        if isinstance(self.optdict, dict):
            for key in self.optdict:
                if key[0] != '-':
                    param_tmp = '-' + key + ' ' + self.optdict[key]
                else:
                    param_tmp = key + ' ' + self.optdict[key]
                # append
                self.optlist.append(param_tmp)
        else:
            print("Option dictionary shoud be provided.")
            return

        self.optcmd = " ".join(self.optlist)

    def gen_cmd(self, filepath=None):
        """Generate the final command line sentence"""
        cmdline = " ".join(["ds9", filepath, self.optcmd])

        return cmdline

def main():
    """The main function"""

    # Init
    parser = argparse.ArgumentParser(
        description="Transform fits to other form.")
    # Parameters
    parser.add_argument("foldname", help="Path of the fits samples.")
    parser.add_argument(
        "savefolder", help="The folder to save transformed files.")
    parser.add_argument("infopath", help="Path of the patiens info.")
    parser.add_argument("batchlow")
    parser.add_argument("batchhigh")
    args = parser.parse_args()

    foldname = args.foldname
    savefolder = args.savefolder
    if not os.path.exists(savefolder):
        os.mkdir(savefolder)

    # load info
    infopath = args.infopath
    p_list = pd.read_excel(infopath)

    # Load sample list
    try:
        samplelist = os.listdir(foldname)
    except:
        print("The folder %s does not exist." % foldname)
        return

    batchlow = int(args.batchlow)
    batchhigh = int(args.batchhigh)
    if batchhigh > len(samplelist):
        batchhigh = len(samplelist)
    samplelist = samplelist[batchlow:batchhigh]

    for s in samplelist:
        print("Processing on patient with ID %s" % s)
        p_idx = np.where(p_list['ID'] == int(s))[0]
        if len(p_idx) == 0:
            continue
        p_idx = p_idx[0]
        # CT id
        p_ct = str(p_list['CT_MAX1'][p_idx])
        print(p_ct)
        p_reg = p_list['BOX'][p_idx]
        p_reg = str(p_reg[4:-1]).split(',')
        p_reg = p_reg[0:4]
        p_reg = " ".join(p_reg)
        # option dicts
        optdict_1 = {
            "cmap": "b",
            "scale": "mode 99.5",
            "crop" : p_reg,
            "width": "128",
            "height": "128",
            }
        optdict_2 = {
            "cmap": "invert yes",
            "scale": "mode 99.5",
            "crop": p_reg,
            "width": "128",
            "height": "128",
            }
        # ParamDS9
        opt_1 = ParamDS9(optdict=optdict_1)
        opt_2 = ParamDS9(optdict=optdict_2)
        opt_3 = ParamDS9(optdict=optdict_1)

        # make direction
        # if not os.path.exists(os.path.join(savefolder,s)):
        #    os.mkdir(os.path.join(savefolder, s))

        # open ds9 and save images
        fitsname = p_ct + ".fits"
        fitspath = os.path.join(foldname,s,fitsname)
        # savename
        savename1 = s + "_b.jpeg"
        savename2 = s + "_i.jpeg"
        savename3 = s + "_c.jpeg"
        savename4 = s + "_m.jpeg"
        savepath1 = os.path.join(savefolder, savename1)
        savepath2 = os.path.join(savefolder, savename2)
        savepath3 = os.path.join(savefolder, savename3)
        savepath4 = os.path.join(savefolder, savename4)
        # open
        cntcmd = "-frame center"
        savecmd1 = "-saveimage jpeg " + savepath1 + " 100"
        finalcmd1 = " ".join([opt_1.gen_cmd(filepath=fitspath), cntcmd, savecmd1,'&'])
        savecmd2 = "-saveimage jpeg " + savepath2 + " 100"
        finalcmd2 = " ".join([opt_2.gen_cmd(filepath=fitspath), cntcmd, savecmd2,'&'])
        savecmd3 = "-saveimage jpeg " + savepath3 + " 100"
        finalcmd3 = " ".join([opt_3.gen_cmd(filepath=fitspath), cntcmd, savecmd3,])

        infodict = utils.gen_infodict(namelist=p_list,
                                      keys_idx=[1,2,3,4,5,6,7,8,9],
                                      p_idx = p_idx)
        utils.gen_mark_image(infodict=infodict,
                             savepath=savepath4,
                            )
        #img = misc.imread(savepath4)
        #img_re = misc.imresize(img,(128,128))
        #misc.imsave(savepath4, img_re)
        print(finalcmd1)
        os.system(finalcmd1)
        print(finalcmd2)
        os.system(finalcmd2)
        print(finalcmd3)
        os.system(finalcmd3)

if __name__ == "__main__":
    main()
