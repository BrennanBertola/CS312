#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import math
import time
import random
import numpy as np

# Used to compute the bandwidth for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1

class GeneSequencing:

	def __init__( self ):
		pass
	
# This is the method called by the GUI.  _seq1_ and _seq2_ are two sequences to be aligned, _banded_ is a boolean that tells
# you whether you should compute a banded alignment or full alignment, and _align_length_ tells you 
# how many base pairs to use in computing the alignment
	def diff(self, val1, val2):
		if val1 == val2: return -3
		else: return 1

	def align( self, seq1, seq2, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length
		iLen = align_length + 1
		jLen = align_length + 1
		if(len(seq1) < iLen): iLen = len(seq1) + 1
		if(len(seq2) < jLen): jLen = len(seq2) + 1
		array = np.full(shape=[iLen, jLen], fill_value=None)

		for i in range(iLen):
			array[i, 0] = i*5
		for j in range(jLen):
			array[0, j] = j*5
		for i in range(1, iLen):
			for j in range(1, jLen):
				minVal = 5 + array[i, j-1]
				if (5+array[i-1,j] < minVal):
					minVal = 5+array[i-1,j];
				if (self.diff(seq1[i-1], seq2[j-1])+ array[i-1,j-1] < minVal):
					minVal = self.diff(seq1[i-1], seq2[j-1])+ array[i-1,j-1]
				array[i,j] = minVal

###################################################################################################
# your code should replace these three statements and populate the three variables: score, alignment1 and alignment2
		score = array[iLen-1, jLen-1];
		alignment1 = 'abc-easy  DEBUG:({} chars,align_len={}{})'.format(
			len(seq1), align_length, ',BANDED' if banded else '')
		alignment2 = 'as-123--  DEBUG:({} chars,align_len={}{})'.format(
			len(seq2), align_length, ',BANDED' if banded else '')
###################################################################################################					
		
		return {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}


