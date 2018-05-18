import vtk
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from affects import affect
import abc

class Node:
    '''
    A Node represents information of a vertex in a 3D graph.
    '''
    def __init__(self):
        self.props = {}
    def setProperty(self, key, value):
        self.props[key] = value
    def getProperty(self, key):
        return self.props[key]

def posEqual(pos1, pos2):
    return pos1.x() == pos2.x() and pos1.y() ==  pos2.y()

class Viewer(QMainWindow):
    affectSignal = QtCore.pyqtSignal(str, affect.Affect)
    def __init__(self, vmdv, sid, descr, attributes, colors, parent=None):
        # Initial the UI components
        QMainWindow.__init__(self, parent)
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

        # Data structures that record graphs
        self.vertexNumber = 0
        self.vertices = {}
        self.selectedVids = []
        self.nid2Vid = {}
        self.edgeLabel = {}

        # Other data structures 
        self.vmdv = vmdv
        self.sid = sid
        self.descr = descr
        self.attributes = attributes
        self.colors = colors

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
        # self.lookupTable.SetNumberOfTableValues(4)
        # self.lookupTable.SetTableValue(0,1.0,0.0,0.0)    # red
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
        theme.FastDelete()
        theme.SetLineWidth(1)
        theme.SetPointSize(10)
        theme.SetPointLookupTable(self.lookupTable)
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
            # self.selectedNids = [self.vi for x in selected]
            # list(map(lambda x: self.vertex2Nid[x],selected))
            print('selected vids:', selected)
            # print('selected Nodes:', self.selectedNids)
            # print('selected nids:', self.selectedNids)
            self.selectedVids = selected


        self.view.GetRepresentation(0).GetAnnotationLink().AddObserver("AnnotationChangedEvent", selection)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonPressEvent, self.selfRightMousePress)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonReleaseEvent, self.selfRightMouseRelease)


    def updateRendering(self):
        self.graph.CheckedShallowCopy(self.graphUnder)
        self.view.ResetCamera()

    def selfRightMousePress(self, obj, event):
        self.rightClickedPos = QCursor.pos()
    def selfRightMouseRelease(self, obj, event):
        if self.rightClickedPos == None or posEqual(self.rightClickedPos, QCursor.pos()):
            if len(self.selectedVids) == 0:
                self.backgroundMenu.exec_(QCursor.pos())
            else:
                self.foregroundMenu.exec_(QCursor.pos())
    
    def performAction(self, trgr):
        afects = trgr.action()
        for a in afects:
            # self.sesion.v.putAffect(self.sesion.sid, a)
            a.affect(self)
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

    def handleAffect(self, a):
        a.affect(self)

    @abc.abstractmethod
    def addNode(self, nid):
        pass
    @abc.abstractmethod
    def addEdge(self, fromId, toId, label):
        pass

    def resetGraphColor(self):
        self.colors.resetColorsOfAllVertices(self.lookupTable)
        self.updateRendering()
    def setVertexColorByName(self, vid, cname):
        cidx = self.colors.colorIndex(cname)
        self.colorArray.SetValue(vid,cidx)
        self.graph.CheckedShallowCopy(self.graphUnder)