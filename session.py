import json
import vtk
import abc
import graph

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
# from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class Session:
    def __init__(self, descr, graphType, attributes):
        self.descr = descr
        self.graphType = graphType
        self.attributes = attributes
        if graphType == 'Tree':
            self.viewer = TreeViewer(attributes)
        elif graphType == 'DiGraph':
            self.viewer = DiGraphViewer(attributes)
        else:
            print ("Unknown graph type:", graphType)
    
    def parseJSON(self, data):
        pass

    def showViewer(self):
        pass
    
    def hideViewer(self):
        pass

class Viewer:
    @abc.abstractmethod
    def parseJSON(self, data):
        pass
    @abc.abstractmethod
    def showView(self):
        pass
    @abc.abstractmethod
    def hideView(self):
        pass

class TreeViewer(Viewer):
    def __init__(self, attributes):
        self.tree = graph.Tree(attributes)
    def parseJSON(self, data):
        pass
    def showView(self):
        pass
    def hideView(self):
        pass

class DiGraphViewer(Viewer):
    def __init__(self, attributes):
        self.digraph = graph.DiGraph(attributes)
        
    def parseJSON(self, data):
        pass
    def showView(self):
        pass
    def hideView(self):
        pass