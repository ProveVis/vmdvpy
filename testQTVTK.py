
import sys
import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
# from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.frame = QFrame()

        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        
        self.contextMenu = QMenu()
        self.createContextMenu()
        # self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # # Create source
        # source = vtk.vtkSphereSource()
        # source.SetCenter(0, 0, 0)
        # source.SetRadius(5.0)

        # # Create a mapper
        # mapper = vtk.vtkPolyDataMapper()
        # mapper.SetInputConnection(source.GetOutputPort())

        # # Create an actor
        # actor = vtk.vtkActor()
        # actor.SetMapper(mapper)

        # self.ren.AddActor(actor)

        # self.ren.ResetCamera()

        # self.frame.setLayout(self.vl)
        # self.setCentralWidget(self.frame)

        # self.show()
        # self.iren.Initialize()
        self.view = vtk.vtkGraphLayoutView()
        self.tree = vtk.vtkTree()
        self.graph = vtk.vtkMutableDirectedGraph()
        self.view.SetRenderWindow(self.vtkWidget.GetRenderWindow())
        self.view.AddRepresentationFromInput(self.tree)
        self.view.SetInteractionModeTo3D()
        self.view.SetLayoutStrategyToCone()

        self.view.SetColorVertices(True)
        self.view.SetEdgeSelection(False)
        theme = vtk.vtkViewTheme.CreateOceanTheme()
        # theme.SetLineWidth(4)
        # theme.SetPointSize(32)
        self.view.ApplyViewTheme(theme)
        theme.FastDelete()

        # rep = self.view.GetRepresentation(0)

        # link = rep.GetAnnotationLink()

        fromVertexId = self.graph.AddVertex()
        toVertexId = self.graph.AddVertex()
        toVertexId2 = self.graph.AddVertex()
        self.graph.AddEdge(fromVertexId, toVertexId)
        self.graph.AddEdge(fromVertexId, toVertexId2)
        self.tree.CheckedShallowCopy(self.graph)
        self.view.ResetCamera()
        self.view.Render()

        camera = self.view.GetRenderer().GetActiveCamera()
        camera.SetPosition(0, 1, 0)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)

        self.view.ResetCamera()
        self.view.Render()
        self.view.GetInteractor().Start()

        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)
        
        self.show()
    
    def contextMenuEvent(self, event):
        print('Showing context menu')
        self.contextMenu.exec_(QCursor.pos())

    def createContextMenu(self):
        action1 = QAction("action1", self)
        action2 = QAction("action2", self)
        action3 = QAction('Close', self)
        self.contextMenu.addAction(action1)
        self.contextMenu.addAction(action2)
        self.contextMenu.addAction(action3)
        action1.triggered.connect(lambda x: print ('action1 triggered', type(x)))
        action2.triggered.connect(lambda x: print ('action2 triggered', type(x)))
        action3.triggered.connect(lambda x: self.close())
    # def showContexMenu(self, pos):
    #     print('Showing context menu')
    #     pass


if __name__ == "__main__":

    app = QApplication(sys.argv)
    # QtGui.Q

    window = MainWindow()
    window2 = MainWindow()

    sys.exit(app.exec_())