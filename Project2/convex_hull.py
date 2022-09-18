from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 2

class Node:
	def __init__(self, data=None):
		self.data = data
		self.cwNode = None
		self.ccwNode = None

class Hull:
	def __init__(self, origPoints):
		self.origPoints = origPoints
		self.leftMost = None
		self.rightMost = None

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False
		
# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)
		
	def eraseHull(self,polygon):
		self.view.clearLines(polygon)
		
	def showText(self,text):
		self.view.displayStatusText(text)
	



# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		t1 = time.time()

		def getX(e):
			return e.x()

		points.sort(key=getX)
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		#polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		finalHull = self.hullDC(points)

		mapPoints = []
		currNode = finalHull.leftMost
		while True:
			mapPoints.append(currNode.data)
			currNode = currNode.cwNode
			if currNode == finalHull.leftMost:
				break

		polygon = [QLineF(mapPoints[i], mapPoints[(i + 1) % len(mapPoints)]) for i in range(len(mapPoints))]
		self.showHull(polygon, RED)

		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		#self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))


	def hullDC(self, points): #O(n)
		splitPoints = []

		# start by splitting points into groups of 3 from left most to right most(how prof. said he did it)
		for i in range(0, len(points), 3):
			splitPoints.append(points[i:i + 3])

		# creates the lowest level hull of size 3 or less
		dividedHulls = []
		for i in range(len(splitPoints)):
			dividedHulls.append(self.createHull(splitPoints[i]))

		#combines the divided hull one by one
		finalHull = dividedHulls[0]
		for i in range (1, len(dividedHulls)):
			finalHull = self.combineHulls(finalHull, dividedHulls[i])

		return finalHull

	def createHull(self, points): #O(2) constant because at most 3 points are passed in with loops of n - 1
		hull = Hull(points);
		hull.leftMost = Node(points[0])

		if len(points) == 1: #if only one point that point is the left and right most
			hull.rightMost = hull.leftMost
			hull.leftMost.cwNode = hull.leftMost
			hull.leftMost.ccwNode = hull.leftMost
			return hull #return now, no need to find cw orientation
		hull.rightMost = Node(points[-1])

		#finds slope of leftmost point to all other points
		slopes = []
		for i in range(1, len(points)):
			slope = (points[i].y() - points[0].y())/(points[i].x() - points[0].x())
			slopes.append([slope, i])

		#sorts slope from largest to smallest
		slopes.sort(reverse=True, key=lambda k : k[0])

		#builds linked list based off of slopes for cw/ccw orientation
		currNode = hull.leftMost
		prevNode = hull.leftMost
		for i in range(len(slopes)):
			index = slopes[i][1]
			if index == len(points) - 1:
				currNode.cwNode = hull.rightMost
				prevNode = currNode
				currNode = prevNode.cwNode
				currNode.ccwNode = prevNode
			else:
				currNode.cwNode = Node(points[slopes[i][1]])
				prevNode = currNode
				currNode = prevNode.cwNode
				currNode.ccwNode = prevNode
		currNode.cwNode = hull.leftMost
		hull.leftMost.ccwNode = currNode

		return hull

	def combineHulls(self, hullL, hullR):

		return hullR