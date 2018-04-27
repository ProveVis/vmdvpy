
import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from viewers import viewer

class TreeViewer(viewer.Viewer):
    def __init__(self, rootNid):
        viewer.Viewer.__init__(self)
        viewer.Viewer.initViewerWindow(self, rootNid, vtk.vtkTree(), 'Cone')




