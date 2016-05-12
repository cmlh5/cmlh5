# ----------------------------------------------------------------------------
# Name:         metadata_def_parser
# Purpose:      Functions for reading cmlh5 metadata definitions
#
# Authors:      Christian Chwala
#
# Created:      19.04.2016
# Copyright:    (c) Christian Chwala 2016
# Licence:      The MIT License
# ----------------------------------------------------------------------------

import os
import numpy as np
import pandas as pd
import h5py


def _load_metadata_def():
    # Parse CSV files with definitions to DataFrames and store them in a dict for each level
    module_dir = os.path.dirname(__file__)
    def_dir = 'definitions'
    fn_for_level = {'root': 'metadata_def_root_level.csv',
                    'cml': 'metadata_def_cml_level.csv',
                    'channel': 'metadata_def_channel_level.csv'}
    metadata_def_df_dict = {}
    for level, fn in fn_for_level.iteritems():
        full_path = os.path.join(module_dir, def_dir, fn)
        metadata_def_df_dict[level] = pd.read_csv(full_path, delimiter=',', index_col=0)

    # Parse everything to a new dict with a different (more accessible...) structure
    metadata_dict = {}
    levels = fn_for_level.keys()
    for level in levels:
        metadata_dict[level] = {}
        for metadata_name in metadata_def_df_dict[level].index.values:
            metadata_dict[level][metadata_name] = {}
            for info in metadata_def_df_dict[level].columns:  # ['Units', 'Type', 'Mandatory', 'Description']:
                entry = metadata_def_df_dict[level].ix[metadata_name][info]
                if type(entry) == str:
                    entry = entry.strip()
                metadata_dict[level][metadata_name][info] = entry
    return metadata_dict


metadata_def = _load_metadata_def()


def read_and_check_metadata(fn, strict_type_check=True):
    h5_reader = h5py.File(fn, mode='r')

    cml_list = []
    error_list = []

    for cml_g_name in h5_reader['/']:
        cml_dict = {}
        cml_dict[cml_g_name] = {}

        cml_g = h5_reader['/' + cml_g_name]

        cml_dict[cml_g_name]['metadata'], errors = \
            _read_cml_metadata(cml_g, strict_type_check)
        error_list = error_list + errors

        for chan_g_name, chan_g in cml_g.items():
            cml_dict[cml_g_name][chan_g_name] = {}
            cml_dict[cml_g_name][chan_g_name]['metadata'], errors = \
                _read_channel_metadata(chan_g, strict_type_check)
            error_list = error_list + errors

        cml_list.append(cml_dict)

    return cml_list, error_list


def _read_metadata(h5_group, level, strict_type_check=True):
    metadata = {}
    error_list = []
    for metadata_name in metadata_def[level]:
        try:
            metadata_entry = h5_group.attrs[metadata_name]
            metadata_entry = _convert_missing_values(metadata_entry,
                                                     metadata_def[level][metadata_name]['Type'])
            type_error = _check_metadata_type(metadata_name,
                                              metadata_entry,
                                              metadata_def[level][metadata_name]['Type'],
                                              strict_type_check=strict_type_check)
            if type_error is not None:
                error_list.append('%s: %s' % (h5_group.name, type_error))

            metadata[metadata_name] = metadata_entry
        except KeyError:
            if metadata_def[level][metadata_name]['Mandatory'] == 'True':
                error_list.append('%s: Mandatory metadata `%s` is missing' %
                                  (h5_group.name, metadata_name))
            else:
                continue
    return metadata, error_list


def _read_root_metadata(root_g, strict_type_check=True):
    return _read_metadata(root_g, 'root', strict_type_check)


def _read_cml_metadata(cml_g, strict_type_check=True):
    return _read_metadata(cml_g, 'cml', strict_type_check)


def _read_channel_metadata(chan_g, strict_type_check=True):
    return _read_metadata(chan_g, 'channel', strict_type_check)


def _check_metadata_type(metadata_name, metadata, type_str, strict_type_check=True):
    error = None
    if (type_str == 'float16' or
            type_str == 'float32' or
            type_str == 'float64' or
            type_str == 'float'):
        try:
            metadata_isnan = np.isnan(metadata)
        except TypeError:
            error = ('Metadata `%s` is `%s` with type `%s`, but it should be some kind of float' %
                     (metadata_name, metadata, type(metadata)))
            return error

        if not np.isnan(metadata):
            if strict_type_check is True:
                if type_str == 'float16':
                    np_type = np.float16
                if type_str == 'float32':
                    np_type = np.float32
                if type_str == 'float64':
                    np_type = np.float64
                if type_str == 'float':
                    np_type = np.float
                type_is_correct = (type(metadata) == np_type)
            else:
                type_is_correct = (type(metadata) == np.float16 or
                                   (type(metadata) == np.float32) or
                                   (type(metadata) == np.float64) or
                                   (type(metadata) == np.float))
            if not type_is_correct:
                error = ('Metadata `%s` is `%s` with type `%s` which should be %s' %
                         (metadata_name, metadata, type(metadata), type_str))
    elif type_str == 'string':
        if metadata is not None:
            if not ((type(metadata) == np.string_) or
                        (type(metadata) == str)):
                error = ('Metadata `%s` is `%s` with type `%s` which should be a string' %
                         (metadata_name, metadata, type(metadata)))
    else:
        error = 'Metadata type_str `%s` for `%s` is not supported' % (type_str, metadata_name)
    return error


def _convert_missing_values(value, type_str):
    if type_str == 'float32':
        if (value == 'NA') or (value == 'NaN') or (value == 'nan'):
            value = np.nan
    if type_str == 'string':
        if value == 'NA':
            value = None
    return value

