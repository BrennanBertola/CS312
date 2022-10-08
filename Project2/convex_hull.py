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
	def __init__(self):
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


	def hullDC(self, points): #a=2 b=2 d=1 O(nlog(n))

		#if there is only 1 point then it is ready to make the hull
		if len(points) <= 1:
			return self.createHull(points[0])

		#finds half the length then calls itself recursively on each half
		l = len(points)//2
		hullL = self.hullDC(points[:l])
		hullR = self.hullDC(points[l:])

		return self.combineHulls(hullL, hullR) #O(n)

	def createHull(self, point): #O(1)
		hull = Hull()

		#creates hull out of 1 point so that one point is both right and left most within divided hull
		hull.leftMost = Node(point)
		hull.rightMost = hull.leftMost

		#since hull is only 1 point it is cw and ccw to itself
		hull.leftMost.cwNode = hull.leftMost
		hull.leftMost.ccwNode = hull.leftMost
		return hull

	def combineHulls(self, hullL, hullR): #O(n)
		newHull = hullL

		topR, topL = self.upperTangent(hullL, hullR) #finds 2 Nodes of upper tangent
		botR, botL = self.lowerTangent(hullL, hullR) #finds 2 Nodes of lower tangent

		#connects the Nodes of the upper and lower tangents within the linked list
		topR.cwNode = topL
		topL.ccwNode = topR
		botR.ccwNode = botL
		botL.cwNode = botR

		newHull.rightMost = hullR.rightMost

		return newHull

	def upperTangent(self, hullL, hullR): #O(n)
		lPoint = hullL.rightMost
		rPoint = hullR.leftMost

		prevLine = self.line(lPoint.data, rPoint.data)
		done = 0

		while True: #repeats inner process till no changes are made
			done = 1
			while True: #rotates ccw around left hull until tmp line is no longer smaller then prev line
				tmpPoint = lPoint.ccwNode
				tmpLine = self.line(tmpPoint.data, rPoint.data)

				if tmpLine < prevLine:
					lPoint = tmpPoint
					prevLine = tmpLine
					done = 0
				else:
					break

			while True: #rotates cw around right hull until tmp line is no longer bigger then prev line
				tmpPoint = rPoint.cwNode
				tmpLine = self.line(lPoint.data, tmpPoint.data)

				if tmpLine > prevLine:
					rPoint = tmpPoint
					prevLine = tmpLine
					done = 0
				else:
					break

			if done:
				break

		return lPoint, rPoint

	def lowerTangent(self, hullL, hullR): #O(n)
		lPoint = hullL.rightMost
		rPoint = hullR.leftMost

		prevLine = self.line(lPoint.data, rPoint.data)
		done = 0

		while True: #repeats inner process till no changes are made
			done = 1
			while True: #rotates cw around left hull until tmp line is no longer bigger then prev line
				tmpPoint = lPoint.cwNode
				tmpLine = self.line(tmpPoint.data, rPoint.data)

				if tmpLine > prevLine:
					lPoint = tmpPoint
					prevLine = tmpLine
					done = 0
				else:
					break

			while True: #rotates ccw around right hull until tmp line is no longer smaller then prev line
				tmpPoint = rPoint.ccwNode
				tmpLine = self.line(lPoint.data, tmpPoint.data)

				if tmpLine < prevLine:
					rPoint = tmpPoint
					prevLine = tmpLine
					done = 0
				else:
					break

			if done: #breaks outer while loop because no changes were made
				break

		return lPoint, rPoint

	def line(self, l, r): #O(1), returns slope between 2 points
		return (r.y() - l.y()) / (r.x() - l.x())