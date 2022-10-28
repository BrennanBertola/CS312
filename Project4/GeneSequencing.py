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

	def unrestrictedRun(self, iLen, jLen, seq1, seq2):
		matrix = {}
		for i in range(iLen):
			matrix[i, 0] = i*5
			self.backArrows[i, 0] = (i-1, 0)
		for j in range(jLen):
			matrix[0, j] = j*5
			self.backArrows[0, j] = (0, j-1)
		for i in range(1, iLen):
			for j in range(1, jLen):
				minVal = self.diff(seq1[i - 1], seq2[j - 1]) + matrix[i - 1, j - 1]
				backArrow = (i-1, j-1)
				if (5+matrix[i-1,j] <= minVal):
					minVal = 5+matrix[i-1,j]
					backArrow = (i-1, j)
				if (5 + matrix[i, j - 1] <= minVal):
					minVal = 5 + matrix[i, j - 1]
					backArrow = (i, j-1)
				matrix[i,j] = minVal
				self.backArrows[i, j] = backArrow

		return matrix[iLen-1, jLen-1]

	def bandedRun(self, iLen, jLen, seq1, seq2):
		matrix = {}
		d = 3

		for i in range(d+1):
			matrix[i, 0] = i*5
			self.backArrows[i, 0] = (i-1, 0)
		for j in range(d+1):
			matrix[0, j] = j*5
			self.backArrows[0, j] = (0, j-1)
		for i in range(1, iLen):
			for j in range(-d + i, d + i + 1):
				if(j < 1):
					continue
				if (j > jLen - 1):
					continue

				minVal = self.diff(seq1[i - 1], seq2[j - 1]) + matrix[i - 1, j - 1]
				backArrow = (i-1, j-1)
				if (i-1, j) in matrix:
					if (5+matrix[i-1,j] <= minVal):
						minVal = 5+matrix[i-1,j]
						backArrow = (i-1, j)
				if (i, j-1) in matrix:
					if (5 + matrix[i, j - 1] <= minVal):
						minVal = 5 + matrix[i, j - 1]
						backArrow = (i, j-1)
				matrix[i,j] = minVal
				self.backArrows[i, j] = backArrow

		return matrix[iLen-1, jLen-1]

	def getAlign(self, iLen, jLen, seq1, seq2):
		newSeq1 = seq1
		newSeq2 = seq2
		operations = []

		currCell = (iLen-1, jLen-1)

		while currCell != (0, 0): #builds a list for what operations were used at what index of the seq
			fromCell = self.backArrows.get(currCell)
			iDiff = currCell[0] - fromCell[0]
			jDiff = currCell[1] - fromCell[1]

			if iDiff == 1 and jDiff == 1: #if match or sub where used
				operations = [0] + operations
			elif iDiff == 1: #if insertion on seq2 was used
				operations = [2] + operations
			elif jDiff == 1: #if insertion on seq1 was used
				operations = [1] + operations

			currCell = fromCell

		length = 100
		if len(operations) < length:
			length = len(operations)

		for i in range(length):
			if operations[i] == 0:
				pass
			elif operations[i] == 1:
				newSeq1 = newSeq1[:i] + "-" + newSeq1[i:]
			elif operations[i] == 2:
				newSeq2 = newSeq2[:i] + "-" + newSeq2[i:]

		newSeq1 = newSeq1[:100]
		newSeq2 = newSeq2[:100]
		return newSeq1, newSeq2


	def align( self, seq1, seq2, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length
		self.backArrows = {}


		iLen = align_length + 1
		jLen = align_length + 1
		if(len(seq1) < iLen): iLen = len(seq1) + 1
		if(len(seq2) < jLen): jLen = len(seq2) + 1




		if iLen - jLen > 3 or jLen - iLen > 3:
			score = float("inf")
			alignment1 = "No Alignment Possible."
			alignment2 = "No Alignment Possible."
		elif banded:
			score = self.bandedRun(iLen, jLen, seq1, seq2)
			alignment1, alignment2 = self.getAlign(iLen, jLen, seq1, seq2)
		else:
			score = self.unrestrictedRun(iLen, jLen, seq1, seq2)
			alignment1, alignment2 = self.getAlign(iLen, jLen, seq1, seq2)


###################################################################################################
# your code should replace these three statements and populate the three variables: score, alignment1 and alignment2

###################################################################################################					
		
		return {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}


