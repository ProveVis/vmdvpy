
import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from viewers import viewer

class TreeViewer(viewer.Viewer):
    edgeLabel = {}
    def __init__(self):
        viewer.Viewer.__init__(self)
        viewer.Viewer.initViewerWindow(self, vtk.vtkTree(), 'Cone')

    def addViewerNode(self, nid):
        # if not self.vtkComponentInitialed:
        #     self.initViewerWindow(nid, vtk.vtkTree(), 'Cone')
        viewer.Viewer.addViewerNode(self, nid)

    # def addViewerEdge(self, fromId, toId, label):
    #     viewer.Viewer.addViewerEdge(self, fromId, toId)
    #     self.edgeLabel[(fromId, toId)] = label



