import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class Viewer(QMainWindow):
    nid2Vertex = {}
    vertex2Nid = {}

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        
        self.frame = QFrame()

        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)
        
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        # self.vtkComponentInitialed = False

    # def initVtkComponent(self, rootNid):


    def initViewerWindow(self, graph, layoutStrategy):
        self.view = vtk.vtkGraphLayoutView()
        self.graph = graph
        self.graphUnder = vtk.vtkMutableDirectedGraph()
        self.view.SetRenderWindow(self.vtkWidget.GetRenderWindow())
        self.view.AddRepresentationFromInput(self.graph)
        self.view.SetInteractionModeTo3D()
        self.view.SetLayoutStrategy(layoutStrategy)

        self.view.SetColorVertices(True)
        self.view.SetEdgeSelection(False)
        theme = vtk.vtkViewTheme.CreateOceanTheme()
        # theme.SetLineWidth(4)
        # theme.SetPointSize(32)
        self.view.ApplyViewTheme(theme)
        theme.FastDelete()

        self.rightClickStart = QCursor.pos()
        self.rightClickEnd = QCursor.pos()

        # fromVertexId = self.graph.AddVertex()
        # toVertexId = self.graph.AddVertex()
        # toVertexId2 = self.graph.AddVertex()
        # self.graph.AddEdge(fromVertexId, toVertexId)
        # self.graph.AddEdge(fromVertexId, toVertexId2)
        self.dummyVertex = self.graphUnder.AddVertex()
        self.dummyVertexExists = True
        # self.nid2Vertex[rootNid] = rootVertex
        # self.vertex2Nid[rootVertex] = rootNid
        self.graph.CheckedShallowCopy(self.graphUnder)
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

        # self.vtkComponentInitialed = True


    def addViewerNode(self, nid):
        if nid not in self.nid2Vertex:
            vertex = self.graphUnder.AddVertex()
            self.nid2Vertex[nid] = vertex
            self.vertex2Nid[vertex] = nid
        else:
            print('Viewer: ',nid, 'has already been added')
        if self.dummyVertexExists:
            self.graphUnder.RemoveVertex(self.dummyVertex)
            self.dummyVertexExists = False


    def addViewerEdge(self, fromId, toId):
        if fromId in self.nid2Vertex and toId in self.nid2Vertex:
            self.graph.AddEdge(self.nid2Vertex[fromId], self.nid2Vertex[toId])
            self.tree.CheckedShallowCopy(self.graphUnder)
