#!/usr/bin/env python

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
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pycmlh5.metadata_def_parser import read_and_check_metadata

if __name__ == "__main__":
    fn = sys.argv[0]
    print fn
    cml_metadata_list, error_list = io.read_and_check_metadata(fn)



