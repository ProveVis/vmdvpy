from collections import deque


class Node:
    def __init__(self):
        self.props = {}
        self.height = 0
    def setProperty(self, key, value):
        # if key not in props:
        self.props[key] = value
    def getProperty(self, key):
        return self.props[key]
    def incrHeight(self):
        self.height = self.height + 1
    def decrHeight(self):
        self.height = self.height - 1
    def setHeight(self, height):
        self.height = height

class Tree:
    def __init__(self, attributes):
        self.attributes = attributes
        self.nodes = {}
        self.children = {}
        self.parent = {}
        self.state = 'NotProved'
        self.height = 0
        self.root = ''

    def reset(self):
        self.nodes.clear()
        self.children.clear()
        self.parent.clear()
        self.state = 'NotProved'
        self.height = 0
        self.root = ''

    def treeHeight(self):
        return self.height

    def nodeHeight(self, nid):
        n = self.nodes[nid]
        return n.height

    def updateHeight(self):
        if self.root == '':
            print('Cannot update height of the tree: root not found')
        else:
            maxNodeHeight = 0
            queue = deque([self.root])
            while len(queue) != 0:
                nid = queue.popleft()
                if nid == self.root:
                    self.getNode(nid).setHeight(0)
                    if nid in self.children:
                        for childId in self.children[nid]:
                            queue.append(childId)
                else:
                    if nid in self.children:
                        for childId in self.children[nid]:
                            queue.append(childId)
                    parentHeight = self.getNode(self.parent[nid]).height
                    self.getNode(nid).setHeight(parentHeight + 1)
                    if parentHeight+1>maxNodeHeight:
                        maxNodeHeight = parentHeight + 1
            self.height = maxNodeHeight
            print('Now tree has height', self.height)
                    
    def addNode(self, nid, node):
        if len(self.nodes) == 0:
            # self.setRoot(nid)
            self.root = nid
        if nid not in self.nodes:
            self.nodes[nid] = node
        else:
            # print('Cannot add tree node', nid, 'twice')
            pass
        # self.updateHeight()
    
    def setRoot(self, nid):
        self.root = nid
        self.updateHeight()
    
    def getNode(self, nid):
        return self.nodes[nid]

    def addEdge(self, fromId, toId):
        if (fromId not in self.nodes) or (toId not in self.nodes):
            print('Cannot add edge', fromId, '->', toId)
        else:
            if fromId not in self.children:
                self.children[fromId] = []
            childrenIds = self.children[fromId]
            if toId not in childrenIds:
                childrenIds.append(toId)
                toNode = self.getNode(toId)
                fromNode = self.getNode(fromId)
                toNode.setHeight(fromNode.height+1)
                # update height of the tree
                if toNode.height > self.height:
                    self.height = toNode.height
                # self.getNode(toId).setHeight(self.getNode(fromId).height+1)
            self.parent[toId] = fromId

    def changeState(self, state):
        self.state = state

    def removeNode(self, nid):
        if nid == self.root:
            self.reset()
        else:
            parentId = self.parent[nid]
            queue = deque([nid])
            while len(queue) != 0:
                tmpNid = queue.popleft()
                if tmpNid in self.children:
                    for childId in self.children[tmpNid]:
                        queue.append(childId)
                self.nodes.pop(tmpNid)
                if tmpNid in self.children:
                    self.children.pop(tmpNid)
                self.parent.pop(tmpNid)
            if nid in self.children[parentId]:
                self.children[parentId].remove(nid)
                # print('removing', parentId, '->', nid)
            # else:
            #     print(nid, 'is not in', self.children[parentId])
            self.updateHeight()
            # pass

    def removeEdge(self, fromId, toId):
        fromNodeChildren = self.children[fromId]
        fromNodeChildren.remove(toId)
        self.removeNode(toId)
        self.parent.pop(toId)
        # pass

    def removeChildren(self, nid):
        for childId in self.children[nid]:
            self.removeEdge(nid, childId)
        # pass
    def removeSubtree(self, nid):
        self.removeNode(nid)

    def nodesOfSubtree(self, nid):
        nids = []
        queue = deque([nid])
        while len(queue) != 0:
            currentNid = queue.popleft()
            nids.append(currentNid)
            for childId in self.children[currentNid]:
                queue.append(childId)
        return nids

    def getAncestors(self, nid):
        nids = []
        tmpNid = self.parent[nid]
        while tmpNid != self.root:
            nids.append(tmpNid)
            tmpNid = self.parent[tmpNid]
        nids.append(self.root)
        return nids

    def getChildren(self, nid):
        if nid in self.children:
            return self.children[nid]
        else:
            return []

    def getDescendants(self, nid):
        nids = []
        queue = deque([nid])
        while len(queue) != 0:
            currentNid = queue.popleft()
            if currentNid in self.children:
                for childId in self.children[currentNid]:
                    nids.append(childId)
                    queue.append(childId)
        return nids
        # pass
    # pass

    def strStructure(self):
        return ''

    def printInfo(self):
        print('attributes:', self.attributes)
        print('height:', self.height)
        print('root:', self.root)
        print('children:', self.children)
        print('parent:', self.parent)


class DiGraph:
    def __init__(self, attributes):
        self.attributes = attributes
        self.nodes = {}
        self.post = {}
        self.pre = {}
        # self.state = 'NotProved'
        # self.height = 0
        self.start = ''

    def reset(self):
        self.nodes.clear()
        # self.nodes.clear()
        self.post.clear()
        self.pre.clear()
        self.start = ''

    def addNode(self, nid, node):
        if self.start == '':
            self.start = nid
        if nid in self.nodes:
            print('Cannot add digraph node', nid, "twice")
        else:
            self.nodes[nid] = node
        
    def getNode(self,nid):
        return self.nodes[nid]
        # pass
    def addEdge(self, fromId, toId):
        # 1. update the post edges of fromId
        if fromId in self.post:
            posts = self.post[fromId]
            if toId not in posts:
                posts.append(toId)
        else:
            self.post[fromId] = [toId]
        # 2. update the pre edges of toId
        if toId in self.pre:
            pres = self.pre[toId]
            if fromId not in pres:
                pres.append(fromId)
        else:
            self.pre[toId] = [fromId]
