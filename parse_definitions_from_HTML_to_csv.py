#!/usr/bin/env python

#----------------------------------------------------------------------------
# Name:         parse_defitions_from_HTLM_to_csv
# Purpose:      Script to parser the GoogleDoc HTML tables to CSV files
#
# Authors:      Christian Chwala
#
# Created:      12.05.2016
# Copyright:    (c) Christian Chwala 2016
# Licence:      The MIT License
#----------------------------------------------------------------------------

import re
import os
import pandas as pd
from lxml.html import parse


# This defines the file names for the tables found in the individual
# sections and subsections of the GoogleDoc HTML file
heading_names_to_file_names = {
    'data_def_channel_level.csv':       '3.2 Specifications of the arrays in the channel subgroup',
    'metadata_def_root_level.csv':      '4.1 Metadata at the root level',
    'metadata_def_cml_level.csv':       '4.2 Metadata at the CML level',
    'metadata_def_channel_level.csv':   '4.3 Metadata at the channel level',
    'metadata_def_array_level.csv':     '4.4 Metadata at the array level',
    'missing_data_convetions.csv':      '5 Missing data conventions'}

package_dirs = {
    'base': 'definitions',
    'pycmlh5': 'pycmlh5/pycmlh5/definitions'}


def get_table_as_df(table):
    """ Ugly function to extract one HTML table into a DataFrame"""

    table_contents = []
    tr_counter = 0

    # Find all <tr> elements
    for table_e in table.getiterator():
        if table_e.tag == 'tr':
            tr = table_e
            tr_counter += 1
            tr_contents = []
            td_counter = 0
            mandatory_tr = 'False'

            # Find all <td> elements
            for tr_e in tr.getiterator():
                if tr_e.tag == 'td':
                    td = tr_e
                    td_contents = ''
                    td_counter += 1

                    # Add the column 'Mandatory' to the header,
                    # which is in the first <tr> element.
                    if tr_counter == 1 and td_counter == 4:
                        tr_contents.append('Mandatory')

                    # Find all text in <td> elements. Iteration is necessary
                    # for multi-line text which has several text elements per <td>.
                    td_text_counter = 0
                    for td_e in td.getiterator():
                        if td_e.text is not None:
                            # Add up text strings
                            text = td_e.text
                            # exclude strings with short square brackets pairs, e.g. `[e]`,
                            # stemming from GoogleDoc comments when exporting to HTML
                            if not re.search(r'\[\w\]', text):
                                if td_contents.endswith('_'):
                                    td_contents = td_contents + td_e.text
                                else:
                                    td_contents = td_contents + ' ' + td_e.text

                            # check if the text element has a class, which indicates
                            # that it originally is bold text and hence is
                            # mandatory metadata. Do this only for the first column
                            # and not for the first row, which hold the header. Only
                            # do this for the first text element that was found.
                            td_text_counter += 1
                            if td_text_counter == 1:
                                if tr_counter > 1 and td_counter == 1:
                                    if ('class' in td_e.attrib.keys()) and (td_e.attrib['class'] != 'c2'):
                                        mandatory_tr = 'True'
                                    else:
                                        mandatory_tr = 'False'

                    # Build list for one <tr>
                    tr_contents.append(td_contents.strip())
                    # Add the boolean (as string) for mandatoriness
                    if tr_counter > 1 and td_counter == 3:
                        tr_contents.append(' ' + mandatory_tr)

            # Build list of <tr> lists
            table_contents.append(tr_contents)

    # Get the first line of the table, which are the column names
    header = table_contents.pop(0)
    df = pd.DataFrame(table_contents, columns=header)
    df.index = df[header[0]]
    df = df.drop(header[0], axis=1)

    return df


def get_tables_for_sections(page):
    table_dict = {}
    current_key = 'foo'

    for e in page.getiterator():
        # If we find a heading, take its text
        # as the current dict key
        if e.tag == 'h2' or e.tag == 'h1':
            print e.getchildren()[0].text
            current_key = e.getchildren()[0].text
        # If we find a table, read it to the
        # corresponding location in the dict
        if e.tag == 'table':
            table_dict[current_key] = get_table_as_df(e)
    return table_dict


def write_table_to_file(table_df, dir_path, file_name):
    full_path = os.path.join(dir_path, file_name)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print 'creating directory %s' % dir_path

    print 'writing %s' % full_path
    table_df.to_csv(full_path,  encoding='utf-8')


if __name__ == "__main__":
    page = parse('html/CMLh5whitepaper.html')

    table_dict = get_tables_for_sections(page)

    for package, dir_path in package_dirs.iteritems():
        print '\nwriting files for package %s to directory %s' % (package, dir_path)
        for file_name, heading_name in heading_names_to_file_names.iteritems():
            write_table_to_file(table_df=table_dict[heading_name],
                                dir_path=dir_path,
                                file_name=file_name)

