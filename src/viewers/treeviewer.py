
import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from viewers import viewer

class TreeViewer(viewer.Viewer):
    # edgeLabel = {}
    def __init__(self, sesion):
        viewer.Viewer.__init__(self, sesion)
        # self.sesion = sesion
        viewer.Viewer.initViewerWindow(self, vtk.vtkTree(), 'Cone')

    def addViewerNode(self, nid):
        if self.dummyVertexExists:
            # self.graphUnder.RemoveVertex(self.dummyVertex)
            self.nid2Vertex[nid] = self.dummyVertex
            self.vertex2Nid[self.dummyVertex] = nid
            self.dummyVertexExists = False
            self.colorArray.InsertValue(self.dummyVertex, self.dummyVertex)
            self.sesion.colors.insertColorOfVertex(self.lookupTable, self.dummyVertex, 0, 1)
        if nid not in self.nid2Vertex:
            vertex = self.graphUnder.AddVertex()
            self.nid2Vertex[nid] = vertex
            self.vertex2Nid[vertex] = nid
            self.colorArray.InsertValue(vertex, vertex)
        else:
            # print('Viewer:',nid, 'has already been added')
            pass


