#----------------------------------------------------------------------------
# Name:         io
# Purpose:      Functions for reading and writing cml5h files
#
# Authors:      Christian Chwala
#
# Created:      19.04.2016
# Copyright:    (c) Christian Chwala 2016
# Licence:      The MIT License
#----------------------------------------------------------------------------

import pandas as pd
import h5py

#metadata_root = pd.read_csv('metadata_def_root_level.csv', delimiter=';')


def _load_metadata():
    metadata_def = {}
    metadata_def['root'] = pd.read_csv('metadata_def_root_level.csv', delimiter=';', index_col=0)
    metadata_def['cml'] = pd.read_csv('metadata_def_cml_level.csv', delimiter=';', index_col=0)
    metadata_def['channel'] = pd.read_csv('metadata_def_channel_level.csv', delimiter=';', index_col=0)

    metadata_dict = {}
    for level in ['root', 'cml', 'channel']:
        metadata_dict[level] = {}
        for metadata_name in metadata_def[level].index.values:
            metadata_dict[level][metadata_name] = {}
            for info in ['Units', 'Type', 'Mandatory', 'Description']:
                entry = metadata_def[level].ix[metadata_name][' ' + info]
                if type(entry) == str:
                    entry = entry.strip()
                metadata_dict[level][metadata_name][info] = entry
    return metadata_dict


def _read_root_metadata():
    pass


def _read_cml_metadata(cml_g):
    metadata = {}
    metadata['link_id'] = cml_g.attrs['id']
    metadata['length_km'] = cml_g.attrs['length']
    metadata['site_A'] = {'lat':cml_g.attrs['site_a_latitude'],
                          'lon': cml_g.attrs['site_a_longitude']}
    metadata['site_B'] = {'lat':cml_g.attrs['site_b_latitude'],
                          'lon': cml_g.attrs['site_b_longitude']}
    return metadata


def _read_channels_metadata(cml_g):
    tx_rx_pairs = {}
    for chan_g_name, chan_g in cml_g.items():
        tx_rx_pairs[chan_g_name] = {'name': chan_g_name,
                                    'tx': 'tx_' + chan_g_name,
                                    'rx': 'rx_' + chan_g_name,
                                    'f_GHz': chan_g.attrs['frequency'],
                                    'pol': chan_g.attrs['polarisation']}
    return tx_rx_pairs


def _read_channels_data(cml_g):
    data_dict = {}
    for chan_g_name, chan_g in cml_g.items():
        data_dict['rx_' + chan_g_name] = chan_g['RX'][:]
        data_dict['tx_' + chan_g_name] = chan_g['TX'][:]
    data = pd.DataFrame(data=data_dict, index=pd.DatetimeIndex(chan_g['time'][:] * 1e9, tz='UTC'))

    return data


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