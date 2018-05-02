import json
import vtk
import abc
import graph
import sys
from viewers import viewer, treeviewer, digraphviewer
# from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
# from PyQt5.QtGui import QCursor
# from PyQt5 import QtCore
# from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import threading

class Session:
    def __init__(self, descr, graphType, attributes):
        self.descr = descr
        self.graphType = graphType
        self.attributes = attributes
        # if graphType == 'Tree':
        #     self.viewer = TreeViewer(attributes)
        # elif graphType == 'DiGraph':
        #     self.viewer = DiGraphViewer(attributes)
        # else:
        #     print ("Unknown graph type:", graphType, 'exit!')
        #     sys.exit(1)
    # @abc.abstractmethod
    # def parseJSON(self, data):
    #     pass
    @abc.abstractmethod
    def showViewer(self):
        pass
    @abc.abstractmethod
    def closeViewer(self):
        pass

class TreeSession(Session):
    def __init__(self, descr, attributes):
        Session.__init__(self, descr, 'Tree', attributes)
        self.tree = graph.Tree(attributes)
        self.viewer = treeviewer.TreeViewer()
        self.viewer.setWindowTitle(descr)
    
    # def parseJSON(self, data):
    #     pass
    
    def showViewer(self):
        self.viewer.show()

    def closeViewer(self):
        self.viewer.close()

    def addNode(self, node):
        self.tree.addNode(node.getProperty('id'), node)
        self.viewer.addViewerNode(node.getProperty('id'))

    def addEdge(self, fromId, toId, label):
        self.tree.addEdge(fromId, toId)
        self.viewer.addViewerEdge(fromId, toId, label)

class DiGraphSession(Session):
    def __init__(self, descr, attributes):
        Session.__init__(self, descr, 'DiGraph', attributes)
        self.digraph = graph.DiGraph(attributes)
        self.viewer = digraphviewer.DiGraphViewer()
    
    # def parseJSON(self, data):
    #     pass
    
    def showViewer(self):
        self.viewer.show()

    def closeViewer(self):
        self.viewer.close()

    def addNode(self, node):
        self.digraph.addNode(node.getProperty('id'), node)
        self.viewer.addViewerNode(node.getProperty('id'))

    def addEdge(self, fromId, toId, label):
        self.digraph.addEdge(fromId, toId)
        self.viewer.addViewerEdge(fromId, toId, label)


def initTreeSession(s):
    
    s.showViewer()
    node = graph.Node()
    node.setProperty('id', '0')
    s.addNode(node)
    node2 = graph.Node()
    node2.setProperty('id', '1')
    s.addNode(node2)
    s.addEdge('0','1','')
    node3 = graph.Node()
    node3.setProperty('id', '3')
    s.addNode(node3)
    s.addEdge('0','3','')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # QtGui.Q

    
    # thread = threading.Thread(target=initTreeSession, args=())
    # thread.start()
    s = TreeSession('hello',[])
    initTreeSession(s)
    # session.showViewer()

    # digraphSession = DiGraphSession('digraph viewer',[])
    # digraphSession.showViewer()

    sys.exit(app.exec_())