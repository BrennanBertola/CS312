#!/usr/bin/python3
import copy
import math

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))




import time
import numpy as np
from TSPClasses import *
import heapq
import itertools



class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''
	
	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		self.randomBSSF = bssf
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

	def greedy( self,time_allowance=60.0 ): #O(n^3)
		cities = self._scenario.getCities()
		bssf = None
		results = {}
		start_time = time.time()
		startCity = 0
		count = 0

		while startCity < len(cities) and time.time()-start_time < time_allowance: #tries to find a solution starting at each city
			route = [cities[startCity]]
			visted = {cities[startCity]}
			currCity = cities[startCity]

			while len(route) < len(cities): #loops till all cities have been added
				min = math.inf
				minCity = currCity
				for j in range(len(cities)): #finds cheapest edge
					city = cities[j]
					if visted.__contains__(city):
						continue
					if currCity.costTo(city)<min:
						min = currCity.costTo(city)
						minCity = city
				route.append(minCity)
				visted.add(minCity)
				currCity = minCity

			solution = TSPSolution(route)
			if solution.cost < np.inf: #checks if its a valid route
				count += 1
			if bssf == None: #if no bssf then set bssf regarless of solution
				bssf = solution
			elif solution.cost < bssf.cost: #if solution is better than current bssf
				bssf = solution
			startCity += 1

		end_time = time.time()
		results['cost'] = bssf.cost
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None

		self.greedyBSSF = bssf
		return results
	
	
	
	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints: 
		max queue size, total number of states created, and number of pruned states.</returns> 
	'''

	def genRCM(self): #used to make initial reduce cost matrix
		cites = self._scenario.getCities()
		mat = {}

		for i in range(len(cites)):
			for j in range(len(cites)):
				mat[i,j] = cites[i].costTo(cites[j])

		return self.reduceRCM(mat)

	def reduceRCM(self, mat): #is given a cost matrix to reduce
		cites = self._scenario.getCities()
		bound = 0

		for i in range(len(cites)):
			min = math.inf
			for j in range(len(cites)): #finds the min value in each row
				if mat[i,j] < min:
					min = mat[i,j]
			if min == math.inf: #if entire row is is infinity no point in subtracting
				continue
			for j in range(len(cites)): #subtract min value from all other values in row
				mat[i,j] -= min
			bound += min

		for i in range(len(cites)):
			min = math.inf
			for j in range(len(cites)): #finds the min value in each col
				if mat[j,i] < min:
					min = mat[j,i]
			if min == math.inf: #if entire col is is infinity no point in subtracting
				continue
			for j in range(len(cites)): #subtract min value from all other values in col
				mat[i,j] -= min
				mat[j,i] -= min
			bound += min

		return mat, bound
	def expand(self, state): #expands given state by generateing possible children states
		childStates = []
		cities = self._scenario.getCities()
		row = state.city._index

		for col in range(len(cities)): #generates the cost matrix for each child state
			if state.contains(col): #if city is already visted in the current state don't generate a child state
				continue

			rcm = copy.deepcopy(state.rcm)
			bound = state.lowBound
			bound += rcm[row, col]

			for i in range(len(cities)):
				rcm[row, i] = math.inf
				rcm[i, col] = math.inf
			rcm[col, row] = math.inf

			rcm, tmp = self.reduceRCM(rcm)
			bound += tmp
			childStates.append(StateObj(rcm, bound, cities[col], copy.deepcopy(state.route))) #creates and stores child

		return childStates

	def test(self, state): #tests if state is a valid route
		route = state.route
		if len(route) < len(self._scenario.getCities()): #can't be a valid route if it hasn't visted all cities
			return math.inf
		return TSPSolution(route).cost

	def queueSize(self, queues): #used to get the total states stored across all priority queues
		total = 0;
		for queue in queues:
			total += queue.size()
		return total

	def branchAndBound( self, time_allowance=60.0):
		cities = self._scenario.getCities()
		rcm, bound = self.genRCM()
		startState = StateObj(rcm, bound, cities[0], []) #start at city index 0 and no route

		queue = PrioQueue()
		queue.insert(startState, bound)
		levelQueues = []
		levelQueues.append(queue)

		maxSize = 0
		totalStates = 1 #starts at one because we start with one state
		prunedStates = 0
		numSolutions = 0
		start_time = time.time()

		self.greedy(time_allowance) #solid starting bssf, faster than random for more cities
		bssf = self.greedyBSSF
		while not len(levelQueues) == 0 and time.time()-start_time < time_allowance:
			totSize = self.queueSize(levelQueues)
			if totSize > maxSize: #checks if curr size is bigger than max size
				maxSize = totSize
			queue = levelQueues[len(levelQueues)-1] #curr queue is set to lowest level queue to enforce digging
			newLevel = PrioQueue()
			empty = False
			while queue.isEmpty(): #if curr queue has no more states remove it from array of queues and try again
				levelQueues.pop(len(levelQueues)-1)
				if len(levelQueues) == 0:
					empty = True
					break
				queue = levelQueues[len(levelQueues) - 1]
			if empty: #if no more states continue to top while loop which will now exit
				continue

			minState = queue.deleteMin()
			if minState.lowBound < bssf.cost:
				childStates = self.expand(minState)
				for currState in childStates:
					if self.test(currState) < bssf.cost: #we have found a better solution
						numSolutions += 1
						bssf = TSPSolution(currState.route)
					elif currState.lowBound < bssf.cost: #no solution yet but could still lead to a better solution
						totalStates += 1
						newLevel.insert(currState, currState.lowBound)
					else: #worse solution was found or it is no longer a possible solution
						totalStates += 1
						prunedStates += 1
				levelQueues.append(newLevel)
			else: #lower bound is no longer smaller then BSSF so the state is pruned
				prunedStates += 1

		prunedStates += self.queueSize(levelQueues) #add all the states that we didn't have time for
		end_time = time.time()
		results = {}
		results['cost'] = bssf.cost
		results['time'] = end_time - start_time
		results['count'] = numSolutions
		results['soln'] = bssf
		results['max'] = maxSize
		results['total'] = totalStates
		results['pruned'] = prunedStates

		return results



	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	'''
		
	def fancy( self,time_allowance=60.0 ):
		pass
		



