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
    @abc.abstractmethod
    def parseJSON(self, data):
        pass
    @abc.abstractmethod
    def showViewer(self):
        pass
    @abc.abstractmethod
    def closeViewer(self):
        pass

class TreeSession(Session):
    def __init__(self, descr, attributes, rootNid):
        Session.__init__(self, descr, 'Tree', attributes)
        self.tree = graph.Tree(attributes)
        self.viewer = treeviewer.TreeViewer(rootNid)
        self.viewer.setWindowTitle(descr)
    
    def parseJSON(self, data):
        pass
    
    def showViewer(self):
        self.viewer.show()

    def closeViewer(self):
        self.viewer.close()

class DiGraphSession(Session):
    def __init__(self, descr, attributes, startNid):
        Session.__init__(self, descr, 'DiGraph', attributes)
        self.digraph = graph.DiGraph(attributes)
        self.viewer = digraphviewer.DiGraphViewer(startNid)
    
    def parseJSON(self, data):
        pass
    
    def showViewer(self):
        self.viewer.show()

    def closeViewer(self):
        self.viewer.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # QtGui.Q

    session = TreeSession('hello',[],0)
    session.showViewer()

    digraphSession = DiGraphSession('digraph viewer',[],0)
    digraphSession.showViewer()

    sys.exit(app.exec_())