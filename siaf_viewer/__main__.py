#!/usr/bin/env python
from __future__ import print_function, division
import argparse
import os
from os.path import join
import glob

# before importing, ensure the environment variable is set
if os.environ.get('WEBBPSF_PATH') is None:
    assert exists('/grp/jwst/ote/webbpsf-data')
    os.environ['WEBBPSF_PATH'] = '/grp/jwst/ote/webbpsf-data'

from __init__ import SIAFViewer, NIRCAM, NIRSPEC, NIRISS, MIRI, FGS

def _siaf_path_from_name(instrument_name):
    siaf_xml = glob.glob(join(
        os.environ.get('WEBBPSF_PATH'),
        instrument_name,
        '{}_SIAF.xml'.format(instrument_name)
    ))
    assert len(siaf_xml) == 1
    return siaf_xml[0]

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--nircam", default=_siaf_path_from_name(NIRCAM),
                    help="path to NIRCam XML SIAF")
parser.add_argument("-r", "--niriss", default=_siaf_path_from_name(NIRISS),
                    help="path to NIRISS XML SIAF")
parser.add_argument("-s", "--nirspec", default=_siaf_path_from_name(NIRSPEC),
                    help="path to NIRSpec XML SIAF")
parser.add_argument("-f", "--fgs", default=_siaf_path_from_name(FGS),
                    help="path to FGS XML SIAF")
parser.add_argument("-m", "--miri", default=_siaf_path_from_name(MIRI),
                    help="path to MIRI XML SIAF")
args = parser.parse_args()

app = SIAFViewer(instrument_filepaths={
    NIRCAM: args.nircam,
    NIRSPEC: args.nirspec,
    NIRISS: args.niriss,
    MIRI: args.miri,
    FGS: args.fgs
})
app.start()
