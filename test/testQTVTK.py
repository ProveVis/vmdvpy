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

        self.colors = GradualColoring(RGB(0,1,0), RGB(0,0,1))

        self.frame = QFrame()

        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)
        

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        
        self.foregroundContextMenu = QMenu()
        self.backgroundContextMenu = QMenu()
        self.createContextMenu()
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.view = vtk.vtkGraphLayoutView()
        self.tree = vtk.vtkTree()
        self.graph = vtk.vtkMutableDirectedGraph()
        self.view.SetRenderWindow(self.vtkWidget.GetRenderWindow())
        self.view.AddRepresentationFromInput(self.tree)
        self.view.SetInteractionModeTo3D()
        self.view.SetLayoutStrategyToCone()

        self.colorArray = vtk.vtkIntArray()
        self.colorArray.SetNumberOfComponents(1)
        self.colorArray.SetName('color')
        self.colorTable = vtk.vtkLookupTable()
        self.colorTable.SetNumberOfColors(2)
        self.colorTable.SetTableValue(0,0,238/255,0)
        self.colorTable.SetTableValue(1,0,238/255,0)
        self.colorTable.Build()
        
        # self.colorArray.Fill(0)
        self.colorArray.InsertValue(0, 0)
        self.colorArray.InsertValue(1, 1)
        self.graph.GetVertexData().AddArray(self.colorArray)
        self.view.SetVertexColorArrayName('color')
        self.view.ColorVerticesOn()

        self.view.SetColorVertices(True)
        self.view.SetEdgeSelection(False)
        theme = vtk.vtkViewTheme.CreateOceanTheme()
        theme.SetCellLookupTable(self.colorTable)
        # theme.SetLineWidth(4)
        # theme.SetPointSize(32)
        self.view.ApplyViewTheme(theme)
        # theme.FastDelete()

        vid = self.graph.AddVertex()
        vid2 = self.graph.AddVertex()
        self.vids.append(vid)
        self.vids.append(vid2)
        self.vertexHeight[vid] = 0
        self.vertexHeight[vid2] = 1
        self.graph.AddEdge(vid, vid2)
        self.children[vid] = [vid2]
        self.tree.CheckedShallowCopy(self.graph)
        

        self.rightClickStart = QCursor.pos()
        self.rightClickEnd = QCursor.pos()



        # fromVertexId = self.graph.AddVertex()
        # toVertexId = self.graph.AddVertex()
        # toVertexId2 = self.graph.AddVertex()
        # self.graph.AddEdge(fromVertexId, toVertexId)
        # self.graph.AddEdge(fromVertexId, toVertexId2)
        # self.graph.GetVertexData().AddArray(self.color1)
        # self.color1.InsertValue(toVertexId2,0)
        # self.tree.CheckedShallowCopy(self.graph)
        # self.view.ResetCamera()
        # self.view.Render()
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

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        # def keypress(interactor, event):


        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonPressEvent, self.selfRightMousePress)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonReleaseEvent, self.selfRightMouseRelease)

        def selection(obj, e):
            # print('selection triggered')
            selected = []
            sel = obj.GetCurrentSelection()
            selvs = sel.GetNode(0).GetSelectionList()
            print('selected', selvs.GetNumberOfTuples(),'nodes')
            for idx in range(selvs.GetNumberOfTuples()):
                selected.append(selvs.GetValue(idx))
                # print('node', selvs.GetValue(idx))
            self.selected = selected
            # print('selected vids:', selected)
            # print('selected nids:', self.selectedNids)


        self.view.GetRepresentation(0).GetAnnotationLink().AddObserver("AnnotationChangedEvent", selection)

        # self.show()

    # def mouseMoveEvent(self,event):
    #     if event.button == Qt.RightButton and event.:

    def selfRightMousePress(self, obj, event):
        print('setting rightClickStart')
        self.rightClickStart = QCursor.pos()
    
    def selfRightMouseRelease(self, obj, event):
        print('Showing context menu')
        if posEqual(self.rightClickStart, QCursor.pos()):
            if len(self.selected) == 0:
                self.backgroundContextMenu.exec_(QCursor.pos())
            else:
                self.foregroundContextMenu.exec_(QCursor.pos())

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

    def addChild(self):
        selected = self.selected
        if len(selected) != 0:
            vid = self.graph.AddVertex()
            self.vids.append(vid)
            self.vertexHeight[vid] = self.vertexHeight[selected[0]]+1
            if self.vertexHeight[vid] > self.treeHeight:
                self.treeHeight = self.vertexHeight[vid]
            self.graph.AddEdge(selected[0], vid)
            if selected[0] not in self.children:
                self.children[selected[0]] = [vid]
            else:
                self.children[selected[0]].append(vid)
            print('added an edge', selected[0],'-->',vid)

            self.colorArray.InsertValue(vid, self.vertexHeight[vid])
            self.colors.updateLookupTable(self.colorTable, self.treeHeight)

            self.tree.CheckedShallowCopy(self.graph)

    def removeNode(self):
        selected = self.selected
        if len(selected) != 0:
            self.graph.RemoveVertex(selected[0])
            self.vids.remove(selected[0])
            self.vertexHeight.pop(selected[0])

    def clearColor(self):
        for vid in self.vertexHeight:
            self.colors.updateVertexColor(self.colorArray, vid, self.vertexHeight[vid])
        self.tree.CheckedShallowCopy(self.graph)

    def highlightChildren(self):
        childrenIds = self.children[self.selected[0]]
        cid = self.colors.colorIndex('green')
        # for vid in childrenIds:
        #     self.colorArray.SetValue(vid, cid)
        self.colors.updateVerticesColor(self.colorArray,childrenIds, self.vertexHeight, cid)
        self.tree.CheckedShallowCopy(self.graph)

    def createContextMenu(self):
        # addAction = QAction("Add Node", self)
        removeAction = QAction("Remove Node", self)
        addAction = QAction('Add Child', self)
        closeAction = QAction('Close', self)
        clearColorAction = QAction('Clear Color', self)
        highlightChildrenAction = QAction('Highlight Children', self)
        self.backgroundContextMenu.addAction(closeAction)
        self.backgroundContextMenu.addAction(clearColorAction)
        self.foregroundContextMenu.addAction(addAction)
        self.foregroundContextMenu.addAction(removeAction)
        self.foregroundContextMenu.addAction(highlightChildrenAction)
        # self.contextMenu.addAction(actionAddChild)
        addAction.triggered.connect(lambda x: self.addChild())
        removeAction.triggered.connect(lambda x: self.removeNode())
        closeAction.triggered.connect(lambda x: self.close())
        clearColorAction.triggered.connect(lambda x: self.clearColor())
        highlightChildrenAction.triggered.connect(lambda x: self.highlightChildren())
    # def showContexMenu(self, pos):
    #     print('Showing context menu')
    #     pass



class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

def slicingColor(c1, c2, total, index):
    r = c1.r + index/total*(c2.r-c1.r)
    g = c1.g + index/total*(c2.g-c1.g)
    b = c1.b + index/total*(c2.b-c1.b)
    return RGB(r,g,b)
    
class Coloring:
    def __init__(self):
        # self.reservedColor = [('red', RGB(1.0, 0.0, 0.0)), ('green', RGB(0.0, 1.0, 0.0)), ('blue', RGB(0.0, 0.0, 1.0))]
        self.reservedColor = []

    def colorIndex(self, cname):
        for i in range(len(self.reservedColor)):
            # print('color', i,':', self.reservedColor[i][0])
            nc = self.reservedColor[i]
            if nc[0] == cname:
                return i
        return 0

class GradualColoring(Coloring):
    def __init__(self, startingRgb, endingRgb):
        Coloring.__init__(self)
        self.startingRgb = startingRgb
        self.endingRgb = endingRgb
        # self.reservedRgb

    def updateLookupTable(self, lookupTable, grades):
        nr = len(self.reservedColor)
        lookupTable.SetNumberOfTableValues(nr+grades)
        for i in range(nr):
            (nc,c) = self.reservedColor[i]
            lookupTable.SetTableValue(i,c.r,c.g,c.b) 
        for j in range(grades):
            c = slicingColor(self.startingRgb, self.endingRgb, grades, j)
            lookupTable.SetTableValue(j+nr, c.r, c.g, c.b)
        lookupTable.Build()

    def updateVertexColor(self, colorArray, vid, nodeHeight):
        nr = len(self.reservedColor)
        # nstate = node.getProperty('state')
        # if nstate == 'Proved':
        colorArray.SetValue(vid, nr+nodeHeight)
        # else:
        #     print('Don\'t know to color node with state', nstate)

    def updateVerticesColor(self, colorArray, vids, vertexHeight, cid):
        for vid in vids:
            colorArray.SetValue(vid, cid)
        for vid in vertexHeight :
            if vid not in vids:
                colorArray.SetValue(vid, vertexHeight[vid])

class FixedColoring(Coloring):
    def updateLookupTable(self, lookupTable):
        nr = len(self.reservedColor)
        lookupTable.SetNumberOfTableValues(nr)
        for i in range(nr):
            (nc,c) = self.reservedColor[i]
            lookupTable.SetTableValue(i,c.r,c.g,c.b) 

    def updateVertexColor(self, colorArray, vid, node):
        # (nc, c) = self.reservedColor[0]
        colorArray.SetValue(vid, 0)
        

if __name__ == "__main__":

    app = QApplication(sys.argv)
    # QtGui.Q

    window = MainWindow()
    window.show()
    # window2 = MainWindow()

    sys.exit(app.exec_())