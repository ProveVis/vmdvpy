import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from viewers import viewer

class DiGraphViewer(viewer.Viewer):
    def __init__(self, startNid):
        viewer.Viewer.__init__(self)
        layout = vtk.vtkForceDirectedLayoutStrategy()
        layout.ThreeDimensionalLayoutOn ()
        layout.AutomaticBoundsComputationOn()
        # view.SetLayoutStrategy(self.layout)
        viewer.Viewer.initViewerWindow(self, startNid, vtk.vtkDirectedGraph(), layout)
        viewer.Viewer.setWindowTitle(self, 'DiGraph')
        # pass
    
