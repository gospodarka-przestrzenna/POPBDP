__author__ = 'Wawrzyniec Zipser, Maciej Kamiński Politechnika Wrocławska'

import os,sys
from PyQt5 import uic

def classFactory(iface):
    """invoke plugin"""
    from .plugin import POPBDP

    return POPBDP(iface)
