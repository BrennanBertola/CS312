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
	def diff(self, val1, val2): #O(1) used to check if it's a match or subsitution
		if val1 == val2: return -3
		else: return 1

	def unrestrictedRun(self, iLen, jLen, seq1, seq2): #O(mn)
		matrix = {}
		for i in range(iLen): #base cases
			matrix[i, 0] = i*5
			self.backArrows[i, 0] = (i-1, 0)
		for j in range(jLen): #base cases
			matrix[0, j] = j*5
			self.backArrows[0, j] = (0, j-1)
		for i in range(1, iLen): #by row
			for j in range(1, jLen): #by col
				#order of checked cells matters to enforce precedence(default is diagonal)
				minVal = self.diff(seq1[i - 1], seq2[j - 1]) + matrix[i - 1, j - 1]
				backArrow = (i-1, j-1)
				if (5+matrix[i-1,j] <= minVal): #checks cell above
					minVal = 5+matrix[i-1,j]
					backArrow = (i-1, j)
				if (5 + matrix[i, j - 1] <= minVal): #checks cell to left
					minVal = 5 + matrix[i, j - 1]
					backArrow = (i, j-1)
				matrix[i,j] = minVal
				self.backArrows[i, j] = backArrow #trace used for alignment

		return matrix[iLen-1, jLen-1]

	def bandedRun(self, iLen, jLen, seq1, seq2): #O(kn) where k = 2d+1
		matrix = {}
		d = 3

		for i in range(d+1): #base case
			matrix[i, 0] = i*5
			self.backArrows[i, 0] = (i-1, 0)
		for j in range(d+1): #base case
			matrix[0, j] = j*5
			self.backArrows[0, j] = (0, j-1)
		for i in range(1, iLen): #row
			for j in range(-d + i, d + i + 1): #cols (only 2d+1 cols per row)
				#next 2 if statements are used to ensure j is within the table
				if(j < 1):
					continue
				if (j > jLen - 1):
					continue

				#order of checked cells matters to enforce precedence(default is diagonal)
				minVal = self.diff(seq1[i - 1], seq2[j - 1]) + matrix[i - 1, j - 1]
				backArrow = (i-1, j-1)
				if (i-1, j) in matrix: #ensure cell above was calculated
					if (5+matrix[i-1,j] <= minVal): #checks cell above
						minVal = 5+matrix[i-1,j]
						backArrow = (i-1, j)
				if (i, j-1) in matrix: #ensure cell to the left was calculated
					if (5 + matrix[i, j - 1] <= minVal): #checks cell to left
						minVal = 5 + matrix[i, j - 1]
						backArrow = (i, j-1)
				matrix[i,j] = minVal
				self.backArrows[i, j] = backArrow #trace used for alignment

		return matrix[iLen-1, jLen-1]

	def getAlign(self, iLen, jLen, seq1, seq2): #O(n)
		newSeq1 = seq1
		newSeq2 = seq2
		operations = []

		currCell = (iLen-1, jLen-1)

		# builds a list for what operations were used at what index of the seq
		while currCell != (0, 0): #O(n) where n is the longer of the 2 sequences
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

		#O(100) ~ O(1) fixed loop that can't iterate more than 100 times
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


	def align( self, seq1, seq2, banded, align_length): #banded: O(kn), unrestricted: O(n^2)
		self.banded = banded
		self.MaxCharactersToAlign = align_length
		self.backArrows = {}


		iLen = align_length + 1
		jLen = align_length + 1
		if(len(seq1) < iLen): iLen = len(seq1) + 1
		if(len(seq2) < jLen): jLen = len(seq2) + 1




		if iLen - jLen > 3 or jLen - iLen > 3: #O(1)
			score = float("inf")
			alignment1 = "No Alignment Possible."
			alignment2 = "No Alignment Possible."
		if banded: #O(kn + n) ~ O(kn)
			if iLen - jLen > 3 or jLen - iLen > 3:
				score = float("inf")
				alignment1 = "No Alignment Possible."
				alignment2 = "No Alignment Possible."
			else:
				score = self.bandedRun(iLen, jLen, seq1, seq2) #O(kn)
				alignment1, alignment2 = self.getAlign(iLen, jLen, seq1, seq2) #O(n)
		else: #O(mn + n) ~ O(mn)
			score = self.unrestrictedRun(iLen, jLen, seq1, seq2) #O(mn)
			alignment1, alignment2 = self.getAlign(iLen, jLen, seq1, seq2) #O(n)


###################################################################################################
# your code should replace these three statements and populate the three variables: score, alignment1 and alignment2

###################################################################################################					
		
		return {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}


