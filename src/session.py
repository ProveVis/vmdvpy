import json
import vtk
import abc
import graph
import sys
from viewers import viewer, treeviewer, digraphviewer, utils
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
import threading

class Session:
    def __init__(self, v, sid, descr, graphType, attributes, colors):
        self.v = v
        self.sid = sid
        self.descr = descr
        self.graphType = graphType
        self.attributes = attributes
        self.colors = colors
    @abc.abstractmethod
    def showViewer(self):
        pass

    @abc.abstractmethod
    def closeViewer(self):
        pass
    
    def handleAffect(self, a):
        a.affect(self)


class TreeSession(Session):
    def __init__(self, v, sid, descr, attributes, colors):
        Session.__init__(self, v, sid, descr, 'Tree', attributes, colors)
        self.tree = graph.Tree(attributes)
        self.viewer = treeviewer.TreeViewer(self)
        self.viewer.setWindowTitle(descr)
    
    def getSelectedNids(self):
        return self.viewer.selectedNids
    
    def showViewer(self):
        self.viewer.show()

    def closeViewer(self):
        self.viewer.close()

    def addNode(self, node):
        nid = node.getProperty('id')
        self.tree.addNode(nid, node)
        self.viewer.addViewerNode(nid)
        # self.colors.updateVertexColor(self.viewer.colorArray, self.viewer.nid2Vertex[nid], node)
        # self.viewer.colorArray.InsertNextValue(0)

    def addEdge(self, fromId, toId, label):
        heightBefore = self.tree.height
        self.tree.addEdge(fromId, toId)
        self.viewer.addViewerEdge(fromId, toId, label)
        heightAfter = self.tree.height
        # if heightAfter > heightBefore:
        #     self.colors.updateLookupTable(self.viewer.lookupTable, heightAfter)
        node = self.tree.getNode(toId)
        vtoId = self.viewer.nid2Vertex[toId]
        # print('tree height:', self.tree.height, 'and node height:', node.height)
        # self.colors.updateVertexColor(self.viewer.colorArray, vtoId, node)
        self.colors.insertColorOfVertex(self.viewer.lookupTable, vtoId, node.height, heightAfter)
        self.viewer.updateRendering()

    def resetGraphColor(self):
        self.colors.resetColorsOfAllVertices(self.viewer.lookupTable)
        # for nid in self.tree.nodes:
        #     self.colors.updateVertexColor(self.viewer.colorArray, self.viewer.nid2Vertex[nid], self.tree.nodes[nid])
        self.viewer.updateRendering()

class DiGraphSession(Session):
    def __init__(self, v, sid, descr, attributes, colors):
        Session.__init__(self, v, sid, descr, 'DiGraph', attributes, colors)
        self.digraph = graph.DiGraph(attributes)
        self.viewer = digraphviewer.DiGraphViewer(self)
        self.colors.updateLookupTable(self.viewer.lookupTable)
    
    def getSelectedNids(self):
        return self.viewer.selectedNids
    
    def showViewer(self):
        self.viewer.show()

    def closeViewer(self):
        self.viewer.close()

    def addNode(self, node):
        nid = node.getProperty('id')
        self.digraph.addNode(nid, node)
        self.viewer.addViewerNode(nid)
        # self.colors.updateVertexColor(self.viewer.colorArray, self.viewer.nid2Vertex[nid], node)
        # self.viewer.updateRendering()

    def addEdge(self, fromId, toId, label):
        self.digraph.addEdge(fromId, toId)
        self.viewer.addViewerEdge(fromId, toId, label)
        node = self.digraph.getNode(toId)
        vtoId = self.viewer.nid2Vertex[toId]
        # self.colors.updateVertexColor(self.viewer.colorArray, vtoId, node)
        # self.viewer.updateRendering()
    
    def resetGraphColor(self):
        for nid in self.digraph.nodes:
            self.colors.updateVertexColor(self.viewer.colorArray, self.viewer.nid2Vertex[nid], self.digraph.nodes[nid])
        self.viewer.updateRendering()

def initTreeSession(s):
    s.showViewer()
    node = graph.Node()
    node.setProperty('id', '0')
    node.setProperty('state', 'Proved')
    s.addNode(node)
    node2 = graph.Node()
    node2.setProperty('id', '1')
    node2.setProperty('state', 'Proved')
    s.addNode(node2)
    s.addEdge('0','1','')
    node3 = graph.Node()
    node3.setProperty('id', '3')
    node3.setProperty('state', 'Proved')
    s.addNode(node3)
    s.addEdge('0','3','')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    s = TreeSession('hello',[])
    initTreeSession(s)
    sys.exit(app.exec_())