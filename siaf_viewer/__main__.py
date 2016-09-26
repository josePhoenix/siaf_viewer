#!/usr/bin/env python
from __future__ import print_function, division
import argparse
import os
from os.path import join, exists
import glob
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
plt.style.use('ggplot')

from __init__ import SIAFViewer, NIRCAM, NIRSPEC, NIRISS, MIRI, FGS

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--nircam", default=None,
                    help="path to NIRCam XML SIAF")
parser.add_argument("-r", "--niriss", default=None,
                    help="path to NIRISS XML SIAF")
parser.add_argument("-s", "--nirspec", default=None,
                    help="path to NIRSpec XML SIAF")
parser.add_argument("-f", "--fgs", default=None,
                    help="path to FGS XML SIAF")
parser.add_argument("-m", "--miri", default=None,
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
