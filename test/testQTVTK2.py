import vtk
import sys

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

        # graph to render
        v1 = self.graph.AddVertex()
        v2 = self.graph.AddVertex()
        v3 = self.graph.AddVertex()
        v4 = self.graph.AddVertex()
        self.vids.append(v1)
        self.vids.append(v2)
        self.vids.append(v3)
        self.vids.append(v4)

        print(v1,",",v2,",",v3,",",v4)

        self.graph.AddEdge(v1,v2)
        self.graph.AddEdge(v1,v3)
        self.graph.AddEdge(v2,v4)

        # self.view.SetGlyphType(vtk.vtkGraphToGlyphs.SPHERE)

        

        self.vertexColors = vtk.vtkIntArray()
        self.vertexColors.SetNumberOfComponents(1)
        self.vertexColors.SetName("color")
        self.lookup = vtk.vtkLookupTable()
        self.lookup.Build()

        self.graph.GetVertexData().AddArray(self.vertexColors)
        self.view.SetVertexColorArrayName("color")
        self.view.ColorVerticesOn()
        theme = vtk.vtkViewTheme.CreateOceanTheme()
        theme.SetLineWidth(1)
        theme.SetPointSize(20)
        theme.SetPointLookupTable(self.lookup)
        self.view.ApplyViewTheme(theme)

        self.lookup.SetNumberOfTableValues(6)
        self.lookup.SetTableValue(0,1.0,0.0,0.0)    
        self.lookup.SetTableValue(1,0.0,1.0,0.0)    
        self.lookup.SetTableValue(2,0.0,0.0,1.0)    
        self.lookup.SetTableValue(3,1.0,1.0,1.0)
        self.lookup.SetTableValue(4,0.5,0.8,0.5)   
        self.lookup.SetTableValue(5,0.1,0.2,0.5)   

        # self.vertexColors.InsertNextValue(0)
        # self.vertexColors.InsertNextValue(1)
        # self.vertexColors.InsertNextValue(2)
        # self.vertexColors.InsertNextValue(3)

        # self.tree.CheckedShallowCopy(self.graph)

        # self.vertexColors.InsertValue(v2, 2)
        # self.tree.CheckedShallowCopy(self.graph)


        # self.vertexColors = vtk.vtkIntArray()
        # self.vertexColors.SetNumberOfComponents(1)
        # self.vertexColors.SetName("color")
        self.vertexColors.InsertValue(v1,0)
        self.vertexColors.InsertValue(v2,2)
        self.vertexColors.InsertValue(v3,1)
        self.vertexColors.InsertValue(v4,3)
        # self.graph.GetVertexData().AddArray(self.vertexColors)
        # self.view.SetVertexColorArrayName("color")


        # updating colors of each vertex
        # self.vertexColors.InsertValue(v2,v2)  
        # self.tree.CheckedShallowCopy(self.graph)

        v5 = self.graph.AddVertex()
        self.vids.append(v5)
        print(v5)
        self.vertexColors.InsertValue(v5, v5)
 
        
        self.graph.AddEdge(v1, v5)
        self.tree.CheckedShallowCopy(self.graph)
        # self.graph.RemoveVertex(v5)
        # self.tree.CheckedShallowCopy(self.graph)
        v6 = self.graph.AddVertex()
        self.vids.append(v6)
        self.vertexColors.InsertValue(v6, v6)
        print(v6)
        self.graph.AddEdge(v5, v6)
        self.tree.CheckedShallowCopy(self.graph)
        

        # end graph to render

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

        def selection(obj, e):
            # print('selection triggered')
            selected = []
            sel = obj.GetCurrentSelection()
            selvs = sel.GetNode(0).GetSelectionList()
            # print('selected', selvs.GetNumberOfTuples(),'nodes')
            for idx in range(selvs.GetNumberOfTuples()):
                selected.append(selvs.GetValue(idx))
                # print('node', selvs.GetValue(idx))
            self.selected = selected
            print('selected vids:', self.selected)
            # print('selected nids:', self.selectedNids)


        self.view.GetRepresentation(0).GetAnnotationLink().AddObserver("AnnotationChangedEvent", selection)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    # QtGui.Q

    window = MainWindow()
    window.show()
    # window2 = MainWindow()

    sys.exit(app.exec_())