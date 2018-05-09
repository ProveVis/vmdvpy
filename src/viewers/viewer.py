import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from affects import affect


def posEqual(pos1, pos2):
    return pos1.x() == pos2.x() and pos1.y() ==  pos2.y()

class Viewer(QMainWindow):

    affectSignal = QtCore.pyqtSignal(str, affect.Affect)

    def __init__(self, sesion, parent=None):
        QMainWindow.__init__(self, parent)
        self.nid2Vertex = {}
        self.vertex2Nid = {}
        self.selectedNids = []
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

        self.foregroundMenu = QMenu()
        self.backgroundMenu = QMenu()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.rightClickedPos = None

        self.edgeLabel = {}


    def initViewerWindow(self, graph, layoutStrategy):
        self.view = vtk.vtkGraphLayoutView()
        self.graph = graph
        self.graphUnder = vtk.vtkMutableDirectedGraph()
        self.view.SetRenderWindow(self.vtkWidget.GetRenderWindow())
        self.view.AddRepresentationFromInput(self.graph)
        self.view.SetInteractionModeTo3D()
        self.view.SetLayoutStrategy(layoutStrategy)

        # build lookup table and the vtkIntArray object
        self.colorArray = vtk.vtkIntArray()
        self.colorArray.SetNumberOfComponents(1)
        self.colorArray.SetName("color")
        self.lookupTable = vtk.vtkLookupTable()
        self.lookupTable.SetNumberOfTableValues(4)
        self.lookupTable.SetTableValue(0,1.0,0.0,0.0)    # red
        self.lookupTable.Build()
        self.colorArray.InsertValue(0,0)
        self.graphUnder.GetVertexData().AddArray(self.colorArray)
        self.view.SetVertexColorArrayName("color")
        self.view.ColorVerticesOn()
        
        # print('color array ready')
        # using a theme
        self.view.SetColorVertices(True)
        self.view.SetEdgeSelection(False)
        theme = vtk.vtkViewTheme.CreateOceanTheme()
        # theme.FastDelete()
        theme.SetLineWidth(1)
        theme.SetPointSize(10)
        theme.SetCellLookupTable(self.lookupTable)
        self.view.ApplyViewTheme(theme)

        self.dummyVertex = self.graphUnder.AddVertex()
        self.dummyVertexExists = True

        self.graph.CheckedShallowCopy(self.graphUnder)
        self.view.ResetCamera()
        self.view.Render()
        # self.currentVertexId = None

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
            self.selectedNids = list(map(lambda x: self.vertex2Nid[x],selected))
            # print('selected vids:', selected)
            # print('selected nids:', self.selectedNids)


        self.view.GetRepresentation(0).GetAnnotationLink().AddObserver("AnnotationChangedEvent", selection)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonPressEvent, self.selfRightMousePress)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonReleaseEvent, self.selfRightMouseRelease)


    def updateRendering(self):
        self.graph.CheckedShallowCopy(self.graphUnder)

    def selfRightMousePress(self, obj, event):
        self.rightClickedPos = QCursor.pos()
    def selfRightMouseRelease(self, obj, event):
        if self.rightClickedPos == None or posEqual(self.rightClickedPos, QCursor.pos()):
            if len(self.selectedNids) == 0:
                self.backgroundMenu.exec_(QCursor.pos())
            else:
                self.foregroundMenu.exec_(QCursor.pos())
    
    def performAction(self, trgr):
        afects = trgr.action()
        for a in afects:
            self.sesion.v.putAffect(self.sesion.sid, a)
            # self.affectSignal.emit(self.sesion.sid, a)

    def addForegroundMenuItem(self, trgr):
        print('Viewer adding foreground menu item', trgr.label)
        act = QAction(trgr.label, self)
        act.triggered.connect(lambda x: self.performAction(trgr))
        self.foregroundMenu.addAction(act)

    def addBackgroundMenuItem(self, trgr):
        print('Viewer adding background menu item', trgr.label)
        act = QAction(trgr.label, self)
        act.triggered.connect(lambda x: self.performAction(trgr))
        self.backgroundMenu.addAction(act)

    def addViewerNode(self, nid):
        if self.dummyVertexExists:
            # self.graphUnder.RemoveVertex(self.dummyVertex)
            self.nid2Vertex[nid] = self.dummyVertex
            self.vertex2Nid[self.dummyVertex] = nid
            self.dummyVertexExists = False
            self.colorArray.InsertNextValue(0)
        if nid not in self.nid2Vertex:
            vertex = self.graphUnder.AddVertex()
            self.nid2Vertex[nid] = vertex
            self.vertex2Nid[vertex] = nid
            self.colorArray.InsertNextValue(0)
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
        self.colorArray.SetValue(vid,cidx)
        self.graph.CheckedShallowCopy(self.graphUnder)