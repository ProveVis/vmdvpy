import vtk
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore, Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

def posEqual(pos1, pos2):
    return pos1.x() == pos2.x() and pos1.y() ==  pos2.y()

class MainWindow(QMainWindow):    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.vids = []
        self.vertexHeight = {}
        self.children = {}
        self.selected = []
        self.treeHeight = 0
        self.frame = QFrame()
        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)

        self.view = vtk.vtkGraphLayoutView()
        self.tree = vtk.vtkTree()
        self.graph = vtk.vtkMutableDirectedGraph()
        self.view.SetRenderWindow(self.vtkWidget.GetRenderWindow())
        self.view.AddRepresentationFromInput(self.tree)
        self.view.SetInteractionModeTo3D()
        self.view.SetLayoutStrategyToCone()
        self.view.ColorVerticesOn()
        self.view.SetEdgeSelection(False)
        self.view.SetColorVertices(True)

        self.vertexColors = vtk.vtkIntArray()
        self.vertexColors.SetNumberOfComponents(1)
        self.vertexColors.SetName("color")
        self.lookup = vtk.vtkLookupTable()
        self.lookup.Build()

        # graph to render

        v1 = self.graph.AddVertex()
        v2 = self.graph.AddVertex()
        v3 = self.graph.AddVertex()
        v4 = self.graph.AddVertex()
        self.vids.append(v1)
        self.vids.append(v2)
        self.vids.append(v3)
        self.vids.append(v4)

        self.vertexColors.InsertValue(v1,0)
        self.vertexColors.InsertValue(v2,0)
        self.vertexColors.InsertValue(v3,0)
        self.vertexColors.InsertValue(v4,0)

        print(v1,",",v2,",",v3,",",v4)

        self.graph.AddEdge(v1,v2)
        self.graph.AddEdge(v1,v3)
        self.graph.AddEdge(v2,v4)

        self.graph.GetVertexData().AddArray(self.vertexColors)
        self.view.SetVertexColorArrayName("color")
        self.view.ColorVerticesOn()
        theme = vtk.vtkViewTheme.CreateOceanTheme()
        theme.SetLineWidth(1)
        theme.SetPointSize(20)
        theme.SetPointLookupTable(self.lookup)
        self.view.ApplyViewTheme(theme)

        v5 = self.graph.AddVertex()
        self.vertexColors.InsertValue(v5,0)
        self.vids.append(v5)
        print(v5)
        self.graph.AddEdge(v1, v5)
        # self.tree.CheckedShallowCopy(self.graph)
        v6 = self.graph.AddVertex()
        self.vertexColors.InsertValue(v6,0)
        self.vids.append(v6)
        print(v6)
        self.graph.AddEdge(v5, v6)
        self.tree.CheckedShallowCopy(self.graph)

        v01 = self.graph.AddVertex()
        v02 = self.graph.AddVertex()
        v03 = self.graph.AddVertex()
        v04 = self.graph.AddVertex()
        v05 = self.graph.AddVertex()
        v06 = self.graph.AddVertex()
        v07 = self.graph.AddVertex()
        self.vertexColors.InsertValue(v01,v01)
        self.vertexColors.InsertValue(v02,v02)
        self.vertexColors.InsertValue(v03,v03)
        self.vertexColors.InsertValue(v04,v04)
        self.vertexColors.InsertValue(v05,v05)
        self.vertexColors.InsertValue(v06,v06)
        self.vertexColors.InsertValue(v07,v07)

        # end graph to render

        # init context menu
        def resetColor():
            self.lookup.SetNumberOfTableValues(6)
            # self.lookup.SetTableValue(0,1.0,0.0,0.0)    
            # self.lookup.SetTableValue(1,0.0,1.0,0.0)    
            # self.lookup.SetTableValue(2,0.0,0.0,1.0)    
            # self.lookup.SetTableValue(3,1.0,1.0,1.0)
            # self.lookup.SetTableValue(4,0.5,0.8,0.5)   
            # self.lookup.SetTableValue(5,0.1,0.2,0.5)  
            self.lookup.SetTableValue(0,0.0,1.0,0.0)    
            self.lookup.SetTableValue(1,0.0,1.0,0.0)    
            self.lookup.SetTableValue(2,0.0,1.0,0.0)    
            self.lookup.SetTableValue(3,1.0,1.0,0.0)
            self.lookup.SetTableValue(4,0.0,1.0,0.0)   
            self.lookup.SetTableValue(5,0.0,1.0,0.0)   
            self.vertexColors.InsertValue(v1,0)
            self.vertexColors.InsertValue(v2,1)
            self.vertexColors.InsertValue(v3,2)
            self.vertexColors.InsertValue(v4,3)
            self.vertexColors.InsertValue(v5, 4)
            self.vertexColors.InsertValue(v6, 5)
            self.tree.CheckedShallowCopy(self.graph)

        self.contextMenu = QMenu()
        resetColorAction = QAction('Reset Color', self)
        self.contextMenu.addAction(resetColorAction)
        resetColorAction.triggered.connect(lambda x: resetColor())
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # end init context menu

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
        self.rightClickStart = QCursor.pos()

        def selection(obj, e):
            # print('selection triggered')
            selected = []
            sel = obj.GetCurrentSelection()
            selvs = sel.GetNode(0).GetSelectionList()
            # print('selected', selvs.GetNumberOfTuples(),'nodes')
            for idx in range(selvs.GetNumberOfTuples()):
                selected.append(selvs.GetValue(idx))
            self.selected = selected
            print('selected vids:', self.selected)
            # print('selected nids:', self.selectedNids)

        self.view.GetRepresentation(0).GetAnnotationLink().AddObserver("AnnotationChangedEvent", selection)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonPressEvent, self.selfRightMousePress)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonReleaseEvent, self.selfRightMouseRelease)
    
    def selfRightMousePress(self, obj, event):
        self.rightClickStart = QCursor.pos()
    
    def selfRightMouseRelease(self, obj, event):
        if posEqual(self.rightClickStart, QCursor.pos()):
            if len(self.selected) == 0:
                self.contextMenu.exec_(QCursor.pos())
            else:
                self.contextMenu.exec_(QCursor.pos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())