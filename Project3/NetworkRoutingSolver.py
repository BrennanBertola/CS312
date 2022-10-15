#!/usr/bin/python3


from CS312Graph import *
import time


class arrayQueue:
    def __init__(self):
        pass

    def make(self, dist): #O(n)
        self.amountDeleted = 0
        self.queue = []
        for i in range (len(dist)):
            self.queue.append(dist[i])

    def insert(self, key, item): #O(1)
        self.queue[key] = item

    def deleteMin(self): #O(n)
        minIndex = 0

        for i in range (len(self.queue)):
            if(self.queue[i] < self.queue[minIndex]):
                minIndex = i

        self.amountDeleted += 1
        # can't actually delete because index is key and doing so would throw off indexes
        self.queue[minIndex] = float ('inf')
        return minIndex


    def decreaseKey(self, key, item): #O(n)
        self.queue[key] = item

    def isEmpty(self):
        if self.amountDeleted >= len(self.queue): return True
        else: return False

class heapQueue:

    class info:#used so we can store both the index and distance in the heap array
        def __init__(self, index, dist):
            self.index = index
            self.dist = dist

    def __init__(self):
        self.items = [0] #actual binary tree
        self.pointer = [] #tracks nodes location(index) within the heap array

    def __len__(self):
        return len(self.items) - 1

    def make(self, dist): #O(n)
        self.items = [0]
        self.pointer = []
        for i in range (len(dist)):
            self.items.append(self.info(i, dist[i]))
            self.pointer.append(i+1)

        i = len(dist) // 2
        while i > 0:
            self.shiftDown(i)
            i = i-1

    def insert(self, key, item): #O(log(n))
        self.items.append(self.info(key, item))
        self.pointer[key] = len(self)
        self.shiftUp()

    def deleteMin(self): #O(log(n))
        retVal = self.items[1]
        self.items[1] = self.items[len(self)]
        self.pointer[self.items[1].index] = 1
        self.items.pop()
        self.pointer[retVal.index] = None

        self.shiftDown(1)
        return retVal.index


    def decreaseKey(self, key, item): #O(log(n))
        heapI = self.pointer[key]
        self.items[heapI].dist = item
        self.shiftUp(heapI)

    def isEmpty(self):
        if len(self) <= 0:
            return True
        else:
            return False

    def shiftUp(self, i=-1): #O(log(n))
        if i == -1:
            i = len(self)
        while i //2 > 0:
            if self.items[i].dist < self.items[i//2].dist:
                parentI = self.items[i//2].index #used for updating pointer array
                childI = self.items[i].index
                self.items[i//2], self.items[i] = self.items[i], self.items[i//2] #updates the heap array
                self.pointer[parentI], self.pointer[childI] = self.pointer[childI], self.pointer[parentI] #updates pointer array

            i = i//2

    def shiftDown(self, i): #O(log(n))
        while i * 2 <= len(self):
            minI = self.min(i)
            if self.items[i].dist > self.items[minI].dist:
                largeI = self.items[i].index #used for updating pointer array
                smallI = self.items[minI].index
                self.items[i], self.items[minI] = self.items[minI], self.items[i] #updates the heap array
                self.pointer[largeI], self.pointer[smallI] = self.pointer[smallI], self.pointer[largeI] #updates pointer array

            i = minI

    def min(self, i):
        if i*2+1 > len(self):
            return i*2
        elif self.items[i*2].dist < self.items[i*2+1].dist:
            return i*2
        else:
            return i*2+1


class NetworkRoutingSolver:
    def __init__( self):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network


    def getShortestPath( self, destIndex ):
        self.dest = destIndex

        path_edges = []
        total_length = 0
        nodes = self.network.getNodes()
        currNode = nodes[destIndex]
        while True:
            edge = self.prev[currNode.node_id]#the prev list stores the edge to the previous node

            # if there is no path to the source sets total cost to infinite
            if edge == None:
                return{'cost':float('inf'), 'path':[]}

            path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
            total_length += edge.length
            currNode = edge.src
            if (currNode.node_id == self.source):
                break

        return {'cost':total_length, 'path':path_edges}

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        t1 = time.time()

        self.dist = [None] * len(self.network.getNodes())
        self.prev = [None] * len(self.network.getNodes())

        queue = None

        if use_heap:#decides which type of queue to use
            queue = heapQueue()
        else:
            queue = arrayQueue()

        #Dijkstra's Algorithm
        for i in range (len(self.dist)):
            self.dist[i] = float('inf')
            self.prev[i] = None

        self.dist[self.source] = 0
        queue.make(self.dist)

        while not queue.isEmpty():
            u = self.network.getNodes()[queue.deleteMin()]
            edges = u.neighbors
            for i in range (len(edges)):
                v = edges[i].dest
                if self.dist[v.node_id] > self.dist[u.node_id] + edges[i].length:
                    self.dist[v.node_id] = self.dist[u.node_id] + edges[i].length
                    self.prev[v.node_id] = edges[i]
                    queue.decreaseKey(v.node_id, self.dist[v.node_id])


        t2 = time.time()
        return (t2-t1)
