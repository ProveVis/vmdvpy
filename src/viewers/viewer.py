import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class Viewer(QMainWindow):
    nid2Vertex = {}
    vertex2Nid = {}
    selectedNids = []

    def __init__(self, sesion, parent=None):
        QMainWindow.__init__(self, parent)
        
        # self.colors = colors
        self.sesion = sesion
        self.frame = QFrame()

        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)
        
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.edgeLabel = {}


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

        self.view.ApplyViewTheme(theme)
        theme.FastDelete()

        self.rightClickStart = QCursor.pos()
        self.rightClickEnd = QCursor.pos()

        self.dummyVertex = self.graphUnder.AddVertex()
        self.dummyVertexExists = True

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

        def selection(obj, e):
            # print('selection triggered')
            selected = []
            sel = obj.GetCurrentSelection()
            selvs = sel.GetNode(0).GetSelectionList()
            print('selected', selvs.GetNumberOfTuples(),'nodes')
            for idx in range(selvs.GetNumberOfTuples()):
                selected.append(selvs.GetValue(idx))
                # print('node', selvs.GetValue(idx))
            self.selectedNids = selected


        self.view.GetRepresentation(0).GetAnnotationLink().AddObserver("AnnotationChangedEvent", selection)


    def addViewerNode(self, nid):
        if self.dummyVertexExists:
            # self.graphUnder.RemoveVertex(self.dummyVertex)
            self.nid2Vertex[nid] = self.dummyVertex
            self.vertex2Nid[self.dummyVertex] = nid
            self.dummyVertexExists = False
        if nid not in self.nid2Vertex:
            vertex = self.graphUnder.AddVertex()
            self.nid2Vertex[nid] = vertex
            self.vertex2Nid[vertex] = nid
        else:
            # print('Viewer:',nid, 'has already been added')
            pass

    def addViewerEdge(self, fromId, toId, label):
        if fromId in self.nid2Vertex and toId in self.nid2Vertex and (fromId, toId) not in self.edgeLabel:
            self.graphUnder.AddEdge(self.nid2Vertex[fromId], self.nid2Vertex[toId])
            self.graph.CheckedShallowCopy(self.graphUnder)
            self.view.ResetCamera()
            self.view.Render()
            self.edgeLabel[(fromId, toId)] = label
        elif fromId not in self.nid2Vertex:
            print('Node (from)', fromId, 'is not added')
        elif toId not in self.nid2Vertex:
            print('Node (to)', toId, 'is not added')

    def setVertexColorByName(self, vid, cname):
        cidx = self.sesion.colors.colorIndex(cname)
        self.vertexColors.InsertValue(vid,cidx)
        self.graph.CheckedShallowCopy(self.graphUnder)