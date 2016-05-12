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

import argparse

from pycmlh5.metadata_def_parser import read_and_check_metadata


def parse_args():
    parser = argparse.ArgumentParser(description='Validate cmlh5 file')
    parser.add_argument('file_name',
                        help='Name of the file to validate')
    parser.add_argument('--less_strict_type_check', action='store_true',
                        help='Do not check for float precision')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    print '\n###################################################################'
    print ' Checking file %s' % args.file_name
    print '###################################################################\n'
    cml_metadata_list, error_list = read_and_check_metadata(fn=args.file_name,
                                                            strict_type_check=args.less_strict_type_check)
    for error in error_list:
        print error

    print '\n Found %d errors \n' % len(error_list)






