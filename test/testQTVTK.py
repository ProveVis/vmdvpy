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

        # self.view.SetGlyphType(vtk.vtkGraphToGlyphs.SPHERE)

        self.colorArray = vtk.vtkIntArray()
        self.colorArray.SetNumberOfComponents(1)
        self.colorArray.SetName('color')
        self.colorTable = vtk.vtkLookupTable()
        # self.colorTable.SetNumberOfTableValues(2)
        # self.colorTable.SetTableValue(0,0,238/255,0,1)
        # self.colorTable.SetTableValue(1,0,238/255,0,1)
        self.colorTable.Build()
        
        # self.colorArray.InsertValue(0, 0)
        # self.colorArray.InsertValue(1, 1)
        self.graph.GetVertexData().AddArray(self.colorArray)
        self.view.SetVertexColorArrayName('color')
        self.view.ColorVerticesOn()

        self.view.SetColorVertices(True)
        self.view.SetEdgeSelection(False)
        theme = vtk.vtkViewTheme.CreateOceanTheme()
        theme.FastDelete()
        theme.SetPointLookupTable(self.colorTable)
        self.view.ApplyViewTheme(theme)


        vid = self.graph.AddVertex()
        self.colorArray.InsertValue(vid, vid)
        self.vids.append(vid)
        self.vertexHeight[vid] = 0
        self.treeHeight = 1
        self.colors.setGrades(1)
        self.colors.insertColorTuple(vid, 0)
        self.colors.updateLookupTable(self.colorTable)
        self.tree.CheckedShallowCopy(self.graph)
        

        self.rightClickStart = QCursor.pos()
        self.rightClickEnd = QCursor.pos()

        self.camera = self.view.GetRenderer().GetActiveCamera()
        self.camera.SetPosition(0, 1, 0)
        self.camera.SetFocalPoint(0, 0, 0)
        self.camera.SetViewUp(0, 0, 1)

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
            # print('selected', selvs.GetNumberOfTuples(),'nodes')
            for idx in range(selvs.GetNumberOfTuples()):
                selected.append(selvs.GetValue(idx))
                # print('node', selvs.GetValue(idx))
            self.selected = selected
            # print('selected vids:', selected)
            # print('selected nids:', self.selectedNids)


        self.view.GetRepresentation(0).GetAnnotationLink().AddObserver("AnnotationChangedEvent", selection)

    def selfRightMousePress(self, obj, event):
        # print('setting rightClickStart')
        self.rightClickStart = QCursor.pos()
    
    def selfRightMouseRelease(self, obj, event):
        # print('Showing context menu')
        if posEqual(self.rightClickStart, QCursor.pos()):
            if len(self.selected) == 0:
                self.backgroundContextMenu.exec_(QCursor.pos())
            else:
                self.foregroundContextMenu.exec_(QCursor.pos())

    def mousePressEvent(self, event):
        print('Mouse press', event.button(), event.pos())
        if event.button() == QtCore.Qt.RightButton:
            # print('setting rightClickStart')
            self.rightClickStart = event.pos()

    def mouseReleaseEvent(self, event):
        print('Mouse release', event.button(), event.pos())
        if event.button() == QtCore.Qt.RightButton and posEqual(event.pos(), self.rightClickStart):
            # print('Showing context menu')
            self.contextMenu.exec_(QCursor.pos())

    def addChild(self):
        selected = self.selected
        if len(selected) != 0:
            vid = self.graph.AddVertex()
            self.colorArray.InsertValue(vid, vid)
            self.vids.append(vid)
            self.vertexHeight[vid] = self.vertexHeight[selected[0]]+1
            if self.vertexHeight[vid]+1 > self.treeHeight:
                self.treeHeight = self.vertexHeight[vid]+1
            self.graph.AddEdge(selected[0], vid)
            if selected[0] not in self.children:
                self.children[selected[0]] = [vid]
            else:
                self.children[selected[0]].append(vid)
            # print('added an edge', selected[0],'-->',vid)

            # self.colorArray.InsertValue(vid, 1)
            self.colors.setGrades(self.treeHeight)
            self.colors.insertColorTuple(vid, self.vertexHeight[vid])
            self.colors.updateLookupTable(self.colorTable)

            # self.colors.updateLookupTable(self.colorTable, self.treeHeight+1)
            # self.colors.updateVertexColor(self.colorArray, vid, self.vertexHeight[vid])

            self.tree.CheckedShallowCopy(self.graph)
            self.view.ResetCamera()

    def removeNode(self):
        selected = self.selected
        if len(selected) != 0:
            self.colorArray.RemoveTuple(selected[0])
            self.graph.RemoveVertex(selected[0])
            self.vids.remove(selected[0])
            self.vertexHeight.pop(selected[0])
            self.tree.CheckedShallowCopy(self.graph)

    def clearColor(self):
        self.colors.resetAllColorTuples()
        self.colors.updateLookupTable(self.colorTable)
        self.tree.CheckedShallowCopy(self.graph)
        # for vid in self.vertexHeight:
        #     self.colors.updateVertexColor(self.colorArray, vid, self.vertexHeight[vid])
        # self.tree.CheckedShallowCopy(self.graph)
        # self.view.GetInteractor().Render()
        # print('size of colorArray:', self.colorArray.GetNumberOfTuples(), self.colorArray)
        

    def highlightChildren(self):
        childrenIds = self.children[self.selected[0]]
        cid = self.colors.colorIndex('red')
        for vid in childrenIds:
            self.colors.updateColorTuple(vid, 'red')
            # self.colorArray.InsertValue(vid, cid)
        # self.colors.updateVerticesColor(self.colorArray,childrenIds, self.vertexHeight, cid)
        self.colors.updateLookupTable(self.colorTable)
        self.tree.CheckedShallowCopy(self.graph)

    def printColorData(self):
        print('ColorArray:', self.colorArray.GetNumberOfTuples())
        for i in range(self.colorArray.GetNumberOfTuples()):
            print('(',i,',', self.colorArray.GetValue(i) ,')', end=';')
        print('\nColorTable:', self.colorTable.GetNumberOfTableValues())
        for j in range(self.colorTable.GetNumberOfTableValues()):
            print('(', j, self.colorTable.GetTableValue(j), ')', end=';\n')
        print('\nvertexHeight:\n', self.vertexHeight)
        # for vid in self.treeHeight:



    def createContextMenu(self):
        # addAction = QAction("Add Node", self)
        removeAction = QAction("Remove Node", self)
        addAction = QAction('Add Child', self)
        closeAction = QAction('Close', self)
        clearColorAction = QAction('Clear Color', self)
        highlightChildrenAction = QAction('Highlight Children', self)
        printColorDataAction = QAction('Print Color Data', self)
        # self.backgroundContextMenu.addAction(closeAction)
        self.backgroundContextMenu.addAction(clearColorAction)
        self.backgroundContextMenu.addAction(printColorDataAction)
        self.foregroundContextMenu.addAction(addAction)
        self.foregroundContextMenu.addAction(removeAction)
        self.foregroundContextMenu.addAction(highlightChildrenAction)
        self.foregroundContextMenu.addAction(printColorDataAction)
        
        # self.contextMenu.addAction(actionAddChild)
        addAction.triggered.connect(lambda x: self.addChild())
        removeAction.triggered.connect(lambda x: self.removeNode())
        # closeAction.triggered.connect(lambda x: self.close())
        clearColorAction.triggered.connect(lambda x: self.clearColor())
        highlightChildrenAction.triggered.connect(lambda x: self.highlightChildren())
        printColorDataAction.triggered.connect(lambda x: self.printColorData())

class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

def slicingColor(c1, c2, total, index):
    r = c1.r + index/total*(c2.r-c1.r)
    g = c1.g + index/total*(c2.g-c1.g)
    b = c1.b + index/total*(c2.b-c1.b)
    return RGB(round(r*100)/100,round(g*100)/100,round(b*100)/100)
    
class Coloring:
    def __init__(self):
        self.reservedColor = [('red', RGB(1.0, 0, 0)), ('green', RGB(0, 1.0, 0.0)), ('blue', RGB(0.0, 0.0, 1.0))]
        # self.reservedColor = [('red', RGB(1,1,0))]
        # self.reservedColor = []
        
        # Each element in allColors has the form (int, int, RGB), 
        # where the first int specifies specifies the vid, the second int specifies the index, 
        # and RGB specifies the color
        self.allColors = []

    def getColorByName(self, cname):
        for i in range(len(self.reservedColor)):
            nc, c = self.reservedColor[i]
            if nc == cname:
                return c
        return None

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
        self.grades = 0

    def setGrades(self, newGrades):
        self.grades = newGrades
    def incrGrades(self):
        self.grades = self.grades + 1
    def decrGrades(self):
        self.grades = self.grades - 1

    def calculateColorByIndex(self, total, index):
        c1 = self.startingRgb
        c2 = self.endingRgb
        r = c1.r + index/total*(c2.r-c1.r)
        g = c1.g + index/total*(c2.g-c1.g)
        b = c1.b + index/total*(c2.b-c1.b)
        return RGB(round(r*100)/100,round(g*100)/100,round(b*100)/100)

    def updateColorTuple(self, updatedVid, cname):
        c = self.getColorByName(cname)
        if c == None:
            print('Cannot find color', cname)
        else:
            updated = False
            for i in range(len(self.allColors)):
                tmpVid, tmpIndex, tmpC = self.allColors[i]
                if tmpVid == updatedVid:
                    self.allColors[i] = (tmpVid, tmpIndex, c)
                    updated = True
                    break
            if not updated:
                print('Cannot update color tuple with vid:', updatedVid)

    def resetColorTuple(self, resetVid):
        reset = False
        for i in range(len(self.allColors)):
            tmpVid, tmpIndex, tmpC = self.allColors[i]
            if tmpVid == resetVid:
                self.allColors[i] = (tmpVid, tmpIndex, self.calculateColorByIndex(self.grades, index))
                reset = True
                break
        if not reset:
            print('Cannot reset color tuple with vid:', resetVid)

    def resetAllColorTuples(self):
        for i in range(len(self.allColors)):
            tmpVid, tmpIndex, tmpC = self.allColors[i]
            self.allColors[i] = (tmpVid, tmpIndex, self.calculateColorByIndex(self.grades, tmpIndex))

    def insertColorTuple(self, newVid, newIndex, gradesChanged=True):
        inserted = False
        if gradesChanged:
            for i in range(len(self.allColors)):
                vid, index, c = self.allColors[i]
                self.allColors[i] = (vid, index, self.calculateColorByIndex(self.grades, index))
                if vid == newVid:
                    inserted = True
                elif vid > newVid and not inserted:
                    self.allColors.insert(i, (newVid, newIndex, self.calculateColorByIndex(self.grades, newIndex)))
                    inserted = True
        else:
            for i in range(len(self.allColors)):
                vid, index, c = self.allColors[i]
                if vid == newVid:
                    inserted = True
                    break
                elif vid > newVid and not inserted:
                    self.allColors.insert(i, (newVid, newIndex, self.calculateColorByIndex(self.grades, newIndex)))
                    inserted = True
                    break
        if not inserted:
            self.allColors.append((newVid, newIndex, self.calculateColorByIndex(self.grades, newIndex)))
            inserted = True

    def removeColorTuple(self, removedVid, gradesChanged=True):
        removed = False
        if gradesChanged:
            for i in range(len(self.allColors)):
                vid, index, c = self.allColors[i]
                self.allColors[i] = (vid, index, self.calculateColorByIndex(self.grades, index))
                if vid == removedVid:
                    self.allColors.pop(i)
                    removed = True
        else:
            for i in range(len(self.allColors)):
                vid, index, c = self.allColors[i]
                if vid == removedVid:
                    self.allColors.pop(i)
                    removed = True
                    break
        if not removed:
            print('Cannot remove color tuple with vid:', removedVid)
            removed = True

    def updateLookupTable(self, lookupTable):
        nt = len(self.allColors)
        lookupTable.SetNumberOfTableValues(nt)
        i = 0
        for ct in self.allColors:
            c = ct[2]
            lookupTable.SetTableValue(i, c.r, c.g, c.b)
            i = i + 1

    # def updateLookupTable(self, lookupTable, grades):
    #     nr = len(self.reservedColor)
    #     lookupTable.SetNumberOfTableValues(nr+grades)
    #     for i in range(nr):
    #         (nc,c) = self.reservedColor[i]
    #         lookupTable.SetTableValue(i,c.r,c.g,c.b) 
    #     for j in range(grades):
    #         c = slicingColor(self.startingRgb, self.endingRgb, grades, j)
    #         lookupTable.SetTableValue(j+nr, c.r, c.g, c.b,1)
    #     # lookupTable.Build()

    # def updateVertexColor(self, colorArray, vid, nodeHeight):
    #     nr = len(self.reservedColor)
    #     colorArray.InsertValue(vid, nr+nodeHeight)
    #     # colorArray.InsertValue(vid, self.colorIndex('green'))
        
    # def updateVerticesColor(self, colorArray, vids, vertexHeight, cid):
    #     for vid in vids:
    #         colorArray.SetValue(vid, cid)
    #     for vid in vertexHeight :
    #         if vid not in vids:
    #             colorArray.SetValue(vid, vertexHeight[vid])

class FixedColoring(Coloring):
    def updateLookupTable(self, lookupTable):
        nr = len(self.reservedColor)
        lookupTable.SetNumberOfTableValues(nr)
        for i in range(nr):
            (nc,c) = self.reservedColor[i]
            lookupTable.SetTableValue(i,c.r,c.g,c.b) 

    def updateVertexColor(self, colorArray, vid, cid):
        # (nc, c) = self.reservedColor[0]
        colorArray.SetValue(vid, cid)
        

if __name__ == "__main__":

    app = QApplication(sys.argv)
    # QtGui.Q

    window = MainWindow()
    window.show()
    # window2 = MainWindow()

    sys.exit(app.exec_())