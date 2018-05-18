
import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from viewers import viewer
import sys

class TreeViewer(viewer.Viewer):
    def __init__(self, vmdv, sid, descr, attributes, colors):
        viewer.Viewer.__init__(self, vmdv, sid, descr, attributes, colors)
        viewer.Viewer.initViewerWindow(self, vtk.vtkTree(), 'Cone')
        
        # Data structures that represent a tree, in addition to the following ones
        # self.vertexNumber = 0
        # self.vertices = {}
        # self.selectedVids = []
        # self.nid2Vid = {}
        # self.edgeLabel = {}
        self.vertexHeight = {}
        self.treeHeight = 0
        self.children = {}
        self.parent = {}

    def addNode(self, node):
        nid = node.getProperty('id')
        if self.dummyVertexExists:
            self.vertexNumber += 1
            self.vertices[self.dummyVertex] = node
            self.nid2Vid[nid] = self.dummyVertex
            self.vertexHeight[self.dummyVertex] = 0
            self.treeHeight = 1
            self.children[self.dummyVertex] = []
            self.dummyVertexExists = False
            self.colorArray.InsertValue(self.dummyVertex, self.dummyVertex)
            self.colors.insertColorOfVertex(self.lookupTable, self.dummyVertex, 0, 1)
        if nid not in self.nid2Vid:
            vid = self.graphUnder.AddVertex()
            self.vertexNumber += 1
            self.vertices[vid] = node
            self.nid2Vid[nid] = vid
            self.children[vid] = []
            self.colorArray.InsertValue(vid, vid)
        else:
            print('Viewer:',nid, 'has already been added')
            pass

    def addEdge(self, fromNid, toNid, label):
        if fromNid not in self.nid2Vid:
            print('From node', fromNid, 'has not been added')
            return
        elif toNid not in self.nid2Vid:
            print('To node', toNid, 'has not been added')
            return
        else:
            fromVid = self.nid2Vid[fromNid]
            toVid = self.nid2Vid[toNid]
            if (fromVid, toVid) not in self.edgeLabel:
                if fromVid not in self.vertexHeight:
                    print('From node', fromNid, 'was not in an edge')
                    sys.exit(1)
                self.vertexHeight[toVid] = self.vertexHeight[fromVid] + 1
                if self.vertexHeight[toVid] + 1 > self.treeHeight:
                    self.treeHeight = self.vertexHeight[toVid] + 1
                self.children[fromVid].append(toVid)
                self.parent[toVid] = fromVid
                self.edgeLabel[(fromVid, toVid)] = label
                self.graphUnder.AddEdge(fromVid, toVid)
                self.colors.insertColorOfVertex(self.lookupTable, toVid, self.vertexHeight[toVid], self.treeHeight)
                self.updateRendering()