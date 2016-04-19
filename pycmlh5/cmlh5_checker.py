#!/Users/chwala-c/anaconda/bin/python

#----------------------------------------------------------------------------
# Name:         cmlh5_checker
# Purpose:      Script to check a cmlh5 file for correct layout
#
# Authors:      Christian Chwala
#
# Created:      19.04.2016
# Copyright:    (c) Christian Chwala 2016
# Licence:      The MIT License
#----------------------------------------------------------------------------

import sys
import h5py

from . import io

metadata_dict = io._load_metadata()


def check_cmlh5_file(fn):
    


if __name__ == "__main__":
    fn = sys.argv[0]
    print fn
    h5_reader = h5py.File(fn, mode='r')



