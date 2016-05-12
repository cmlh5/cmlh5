# ----------------------------------------------------------------------------
# Name:         io
# Purpose:      Functions for reading and writing cml5h files
#
# Authors:      Christian Chwala
#
# Created:      19.04.2016
# Copyright:    (c) Christian Chwala 2016
# Licence:      The MIT License
# ----------------------------------------------------------------------------


def read_cmlh5(fn):
    h5_reader = h5py.File(fn, mode='r')
    cml_list = []
    cml = {}
    for cml_g_name in h5_reader['/']:
        cml_g = h5_reader['/' + cml_g_name]
        cml['metadata'] = _read_cml_metadata(cml_g)
        cml['channel'] = _read_channels_data()
        cml_list.append(cml)
    print '%d CMLs read in' % len(cml_list)
    return cml_list
