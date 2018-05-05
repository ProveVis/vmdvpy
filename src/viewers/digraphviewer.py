import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from viewers import viewer

class DiGraphViewer(viewer.Viewer):
    def __init__(self, sesion):
        viewer.Viewer.__init__(self, sesion)
        layout = vtk.vtkForceDirectedLayoutStrategy()
        layout.ThreeDimensionalLayoutOn ()
        layout.AutomaticBoundsComputationOn()
        viewer.Viewer.initViewerWindow(self,vtk.vtkDirectedGraph(), layout)
        viewer.Viewer.setWindowTitle(self, 'DiGraph')
        # pass
    
    def addViewerNode(self, nid):
        # if not self.vtkComponentInitialed:
        viewer.Viewer.addViewerNode(self, nid)
