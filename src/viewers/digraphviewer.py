import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from viewers import viewer

class DiGraphViewer(viewer.Viewer):
    def __init__(self, vmdv, sid, descr, attributes, colors):
        viewer.Viewer.__init__(self, vmdv, sid, descr, attributes, colors)
        layout = vtk.vtkForceDirectedLayoutStrategy()
        layout.SetMaxNumberOfIterations(70)
        layout.ThreeDimensionalLayoutOn ()
        layout.AutomaticBoundsComputationOn()
        viewer.Viewer.initViewerWindow(self,vtk.vtkDirectedGraph(), layout)
        viewer.Viewer.setWindowTitle(self, 'DiGraph')
       
        # Data structures that represent a digraph, in addition to the following ones
        # self.vertexNumber = 0
        # self.vertices = {}
        # self.selectedVids = []
        # self.nid2Vid = {}
        # self.edgeLabel = {}
        self.post = {}
        self.pre = {}
    
    def addNode(self, node):
        nid = node.getProperty('id')
        if self.dummyVertexExists:
            self.vertexNumber += 1
            self.vertices[self.dummyVertex] = node
            self.nid2Vid[nid] = self.dummyVertex
            self.post[self.dummyVertex] = []
            self.pre[self.dummyVertex] = []
            self.dummyVertexExists = False
            self.colorArray.InsertValue(self.dummyVertex, 0)
        if nid not in self.nid2Vid:
            vid = self.graphUnder.AddVertex()
            self.vertexNumber += 1
            self.vertices[vid] = node
            self.nid2Vid[nid] = vid
            self.post[vid] = []
            self.pre[vid] = []
            self.colorArray.InsertValue(vid, 0)
        else:
            print('DiGraph Viewer:',nid, 'has already been added')
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
                self.post[fromVid].append(toVid)
                self.pre[toVid].append(fromVid)
                self.edgeLabel[(fromVid, toVid)] = label
                self.graphUnder.AddEdge(fromVid, toVid)
                # self.graph.CheckedShallowCopy(self.graphUnder)
                # self.view.ResetCamera()