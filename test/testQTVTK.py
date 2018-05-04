
import sys
import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore, Qt
# from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


def posEqual(pos1, pos2):
    return pos1.x() == pos2.x() and pos1.y() ==  pos2.y()

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
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

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
        # theme.FastDelete()

        self.color1 = vtk.vtkIntArray()
        self.color1.SetNumberOfComponents(1)
        self.color1.SetName('Color')
        colorTable = vtk.vtkLookupTable()
        colorTable.SetNumberOfColors(2)
        colorTable.SetTableValue(0,0.0,238.0/255.0,0.0)
        colorTable.SetTableValue(1,0.0,238.0/255.0,0.0)
        colorTable.Build()
        theme.SetCellLookupTable(colorTable)
        self.color1.InsertNextValue(0)
        self.color1.InsertNextValue(1)
        self.view.SetVertexColorArrayName('Color')
        

        self.rightClickStart = QCursor.pos()
        self.rightClickEnd = QCursor.pos()


        fromVertexId = self.graph.AddVertex()
        toVertexId = self.graph.AddVertex()
        toVertexId2 = self.graph.AddVertex()
        self.graph.AddEdge(fromVertexId, toVertexId)
        self.graph.AddEdge(fromVertexId, toVertexId2)
        self.graph.GetVertexData().AddArray(self.color1)
        self.color1.InsertValue(toVertexId2,0)
        self.tree.CheckedShallowCopy(self.graph)
        self.view.ResetCamera()
        self.view.Render()
        self.currentVertexId = None

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

        # def keypress(interactor, event):


        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonPressEvent, self.selfRightMousePress)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonReleaseEvent, self.selfRightMouseRelease)

        self.show()

    # def mouseMoveEvent(self,event):
    #     if event.button == Qt.RightButton and event.:

    def selfRightMousePress(self, obj, event):
        print('setting rightClickStart')
        self.rightClickStart = QCursor.pos()
    
    def selfRightMouseRelease(self, obj, event):
        print('Showing context menu')
        if posEqual(self.rightClickStart, QCursor.pos()):
            self.contextMenu.exec_(QCursor.pos())

    def mousePressEvent(self, event):
        print('Mouse press', event.button(), event.pos())
        if event.button() == QtCore.Qt.RightButton:
            print('setting rightClickStart')
            self.rightClickStart = event.pos()

    def mouseReleaseEvent(self, event):
        print('Mouse release', event.button(), event.pos())
        if event.button() == QtCore.Qt.RightButton and posEqual(event.pos(), self.rightClickStart):
            print('Showing context menu')
            self.contextMenu.exec_(QCursor.pos())

        
    
    # def contextMenuEvent(self, event):
    #     print('Showing context menu')
    #     self.contextMenu.exec_(QCursor.pos())

    def createContextMenu(self):
        action1 = QAction("action1", self)
        action2 = QAction("action2", self)
        actionAddChild = QAction('AddChild', self)
        action3 = QAction('Close', self)
        self.contextMenu.addAction(action1)
        self.contextMenu.addAction(action2)
        self.contextMenu.addAction(action3)
        self.contextMenu.addAction(actionAddChild)
        action1.triggered.connect(lambda x: print ('action1 triggered', type(x)))
        action2.triggered.connect(lambda x: print ('action2 triggered', type(x)))
        action3.triggered.connect(lambda x: self.close())
        actionAddChild.triggered.connect(self.addChild)
    # def showContexMenu(self, pos):
    #     print('Showing context menu')
    #     pass

    def addChild(self, b):
        if self.currentVertexId == None:
            self.currentVertexId = self.graph.AddVertex()
        self.graph.AddEdge(self.currentVertexId, self.graph.AddVertex())
        self.tree.CheckedShallowCopy(self.graph)
        # self.currentVertexId.
        # self.view.ResetCamera()
        # self.view.Render()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    # QtGui.Q

    window = MainWindow()
    window2 = MainWindow()

    sys.exit(app.exec_())