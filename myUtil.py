#! /usr/bin/env python
import sys
import os
import os.path
import glob
import re
from optparse import OptionParser


import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.widgets import Button

# ---- prompt options --------------------------
def yesOrNo(question):
	answer = ''
	while answer != 'y' and answer != 'n':
		answer = raw_input("%s (y/n)"%question)
	return answer

def getNumCasDat(cas_raw,dat_raw):
	cas = cas_raw
	dat = dat_raw
	num = cas.split('-',1)[0]
	dir = os.getcwd()
	caseName = cas
	dataName = dat
	fileExt = 'gz'
	while (fileExt == 'gz' or  fileExt == 'dat' or fileExt == 'cas'):
		fileExt = dataName.split('.').pop()
 		dataName = dataName.rsplit('.',1)[0]		
	fileExt = 'gz'
	while (fileExt == 'gz' or  fileExt == 'dat' or fileExt == 'cas'):
		fileExt = caseName.split('.').pop()
 		caseName = caseName.rsplit('.',1)[0]		
	return (num,caseName,dataName)
