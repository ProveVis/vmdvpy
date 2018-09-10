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

        self.vertexNumber = 0
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

        self.view.SetGlyphType(vtk.vtkGraphToGlyphs.SPHERE)

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
        theme.SetPointSize(15)
        self.view.ApplyViewTheme(theme)


        vid = self.graph.AddVertex()

        # add a pedigree array to vertex
        self.vertIds = vtk.vtkIdTypeArray()
        numVertices = self.graph.GetNumberOfVertices()
        # print("number of vertices:", numVertices)
        self.vertIds.SetNumberOfTuples(numVertices)

        # print('wtf',numVertices)
        # for i in range(0, numVertices):
        #     self.vertIds.SetValue(i, i)
        #
        # self.graph.GetVertexData().SetPedigreeIds(self.vertIds)

        self.colorArray.InsertValue(vid, vid)
        self.vertexNumber = self.vertexNumber + 1
        self.vertexHeight[vid] = 0
        self.treeHeight = 1
        self.children[vid] = []
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

        # add a pedigree array to vertex
        self.vertIds = vtk.vtkIdTypeArray()
        numVertices = self.graph.GetNumberOfVertices()
        # print("number of vertices:", numVertices)
        self.vertIds.SetNumberOfTuples(numVertices)

        print('wtf', numVertices)
        for i in range(0, numVertices):
            self.vertIds.SetValue(i, i)

        self.graph.GetVertexData().SetPedigreeIds(self.vertIds)
        self.tree.CheckedShallowCopy(self.graph)
        print('SetPedigreeIds finished.')

        self.isLeftButtonPressed = False
        self.pixelRatio = QApplication.desktop().devicePixelRatio()
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.MouseMoveEvent, self.MouseMoved, 100)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.LeftButtonPressed, 100)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent, self.LeftButtonReleased, 100)

        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonPressEvent, self.selfRightMousePress)
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.RightButtonReleaseEvent, self.selfRightMouseRelease)

        def selection(obj, e):
            # print('selection triggered')
            selected = set([])
            sel = obj.GetCurrentSelection()
            selvs = sel.GetNode(0).GetSelectionList()
            # print('selected', selvs.GetNumberOfTuples(),'nodes')
            for idx in range(selvs.GetNumberOfTuples()):
                selected.add(selvs.GetValue(idx))
                # print('node', selvs.GetValue(idx))
            self.selected = list(selected)
            print('selected vids:', selected)
            # print('selected nids:', self.selectedNids)


        self.view.GetRepresentation(0).GetAnnotationLink().AddObserver("AnnotationChangedEvent", selection)

    def LeftButtonPressed(self, obj, event):
        self.isLeftButtonPressed = True
        pos = obj.GetEventPosition()
        obj.SetEventPosition(pos[0] * self.pixelRatio, pos[1] * self.pixelRatio)

    def LeftButtonReleased(self, obj, event):
        self.isLeftButtonPressed = False
        pos = obj.GetEventPosition()
        obj.SetEventPosition(pos[0] * self.pixelRatio, pos[1] * self.pixelRatio)

    def MouseMoved(self, obj, event):
        if self.isLeftButtonPressed:
            pos = obj.GetEventPosition()
            obj.SetEventPosition(pos[0] * self.pixelRatio, pos[1] * self.pixelRatio)

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

            # add a pedigree array to vertex
            # self.vertIds = vtk.vtkIdTypeArray()
            numVertices = self.graph.GetNumberOfVertices()
            # print("number of vertices:", numVertices)
            self.vertIds.SetNumberOfTuples(numVertices)

            print('wtf',numVertices)
            for i in range(0, numVertices):
                self.vertIds.SetValue(i, i)

            self.graph.GetVertexData().SetPedigreeIds(self.vertIds)


            self.children[vid] = []
            self.colorArray.InsertValue(vid, vid)
            self.vertexNumber = self.vertexNumber + 1
            self.vertexHeight[vid] = self.vertexHeight[selected[0]]+1
            if self.vertexHeight[vid]+1 > self.treeHeight:
                self.treeHeight = self.vertexHeight[vid]+1
            self.graph.AddEdge(selected[0], vid)
            if selected[0] not in self.children:
                self.children[selected[0]] = [vid]
            else:
                self.children[selected[0]].append(vid)
            # print('added an edge', selected[0],'-->',vid)
            self.colors.insertColorOfVertex(self.colorTable, vid, self.vertexHeight[vid], self.treeHeight)

            # add a pedigree array to vertex
            self.vertIds = vtk.vtkIdTypeArray()
            numVertices = self.graph.GetNumberOfVertices()
            # print("number of vertices:", numVertices)
            self.vertIds.SetNumberOfTuples(numVertices)
            self.tree.CheckedShallowCopy(self.graph)
            self.view.ResetCamera()

    # def updateTreeHeight(self):
    #     treeHeight = 0
    #     for vid in self.vertexHeight:
    #         if self.vertexHeight[vid]+1 > treeHeight:
    #             treeHeight = self.vertexHeight[vid]+1
    #     self.treeHeight = treeHeight

    def changeVid(self, x, oldVid, newVid):
        if x == oldVid:
            return newVid
        else:
            return x
        # self.children[newVid] = self.children[oldVid]
        # self.children.pop(oldVid)
        # self.vertexHeight[newVid] = self.vertexHeight[oldVid]
        # self.vertexHeight.pop(oldVid)

    def decrAbove(self, x, above):
        if x < above:
            return x
        else:
            return x-1

    # vidMap has the form {ovid:nvid}, and the following function
    # changes the occurences of ovid to that of nvid
    def modifyVertexInfo(self, vidMap):
        for ovid in vidMap:
            nvid = vidMap[ovid]
            # if ovid in self.vertices:
            #     self.vertices[nvid] = self.vertices[ovid]
            #     self.vertices.pop(ovid)
            # for nid in self.nid2Vid:
            #     if self.nid2Vid[nid] == ovid:
            #         self.nid2Vid[nid] = nvid
            # for (fvid, tvid) in self.edgeLabel:
            #     if fvid == ovid:
            #         self.edgeLabel[(nvid, tvid)] = self.edgeLabel[(fvid, tvid)]
            #         self.edgeLabel.pop((fvid, tvid))
            #     if tvid == ovid:
            #         self.edgeLabel[(fvid, nvid)] = self.edgeLabel[(fvid, tvid)]
            #         self.edgeLabel.pop((fvid, tvid))
            if ovid in self.vertexHeight:
                self.vertexHeight[nvid] = self.vertexHeight[ovid]
                self.vertexHeight.pop(ovid)
            for tmpVid in self.children:
                ochildren = self.children[tmpVid]
                if ovid in ochildren:
                    ochildren.remove(ovid)
                    ochildren.append(nvid)
                if tmpVid == ovid:
                    self.children[nvid] = self.children[ovid]
                    self.children.pop(ovid)
            # for tmpVid in self.parent:
            #     if self.parent[tmpVid] == ovid:
            #         self.parent[tmpVid] = nvid
            #     if tmpVid == ovid:
            #         self.parent[nvid] = self.parent[tmpVid]
            #         self.parent.pop(ovid)
            # if ovid in self.rules:
            #     self.rules[nvid] = self.rules[ovid]
            #     self.rules.pop(ovid)

    def updateTreeHeight(self):
        max = 0
        for vid in self.vertexHeight:
            if self.vertexHeight[vid] > max:
                max = self.vertexHeight[vid]
        self.treeHeight = max + 1

    def clearVertexInfo(self, vid):
        # self.vertices.pop(vid)
        # for nid in self.nid2Vid:
        #     if self.nid2Vid[nid] == vid:
        #         self.nid2Vid.pop(nid)
        # for (fvid, tvid) in self.edgeLabel:
        #     if tvid == vid:
        #         self.edgeLabel.pop((fvid, tvid))
        self.vertexHeight.pop(vid)
        self.updateTreeHeight()
        self.children.pop(vid)
        for tmpVid in self.children:
            if vid in self.children[tmpVid]:
                self.children[tmpVid].remove(vid)
        # self.parent.pop(vid)
        # self.rules.pop(vid)

    def removeVertexFromGraphUnder(self, vid):
        # self.vertexNumber -= 1
        self.graph.RemoveVertex(vid)
        # add a pedigree array to vertex
        self.vertIds = vtk.vtkIdTypeArray()
        self.vertexNumber = self.graph.GetNumberOfVertices()
        # print("number of vertices:", numVertices)
        self.colors.removeColorOfVertex(self.colorTable, vid, self.treeHeight)
        self.colors.resetColorOfVertex(self.colorTable, vid)

        self.vertIds.SetNumberOfTuples(self.vertexNumber)

        # print('wtf', numVertices)
        for i in range(0, self.vertexNumber):
            self.colorArray.InsertValue(i,i)
            self.vertIds.SetValue(i, i)

        self.tree.GetVertexData().SetPedigreeIds(self.vertIds)
        self.tree.CheckedShallowCopy(self.graph)

    def removeVertex(self, vid):
        if vid < self.vertexNumber:
            topVid = self.vertexNumber - 1
            self.children[vid] = self.children[topVid]
            self.vertexHeight[vid] = self.vertexHeight[topVid]
            self.children.pop(topVid)
            self.vertexHeight.pop(topVid)
            for tmpVid in self.children:
                tmpChildren = self.children[tmpVid]
                self.children[tmpVid] = [self.changeVid(x, topVid, vid) for x in tmpChildren]
            self.vertexNumber = self.vertexNumber - 1
            if vid < self.vertexNumber:
                self.colorArray.SetValue(vid, vid)

    def removeNode(self):
        selected = self.selected
        if len(selected) != 0:
            vid = selected[0]
            if vid != 0:
                while vid in self.children and len(self.children[vid]) > 0:
                    # find a leaf of the subtree with root vid
                    leafVid = vid
                    while leafVid in self.children and len(self.children[leafVid]) > 0:
                        leafVid = self.children[leafVid][0]
                    vidMap = {(self.vertexNumber - 1): leafVid}
                    self.clearVertexInfo(leafVid)
                    self.removeVertexFromGraphUnder(leafVid)
                    self.modifyVertexInfo(vidMap)

                vidMap = {(self.vertexNumber - 1): vid}
                self.clearVertexInfo(vid)
                self.removeVertexFromGraphUnder(vid)
                self.modifyVertexInfo(vidMap)



            # self.graph.RemoveVertex(selected[0])
            # self.removeVertex(selected[0])
            # self.colors.removeColorOfVertex(self.colorTable, selected[0], self.treeHeight)
            # self.colors.resetColorOfVertex(self.colorTable, selected[0])
            # # self.colorArray.RemoveTuple(selected[0])
            # # add a pedigree array to vertex
            # self.vertIds = vtk.vtkIdTypeArray()
            # numVertices = self.graph.GetNumberOfVertices()
            # # print("number of vertices:", numVertices)
            # self.vertIds.SetNumberOfTuples(numVertices)
            #
            # print('wtf', numVertices)
            # for i in range(0, numVertices):
            #     self.vertIds.SetValue(i, i)
            #
            # self.graph.GetVertexData().SetPedigreeIds(self.vertIds)
            # self.tree.CheckedShallowCopy(self.graph)
            #
            # self.tree.CheckedShallowCopy(self.graph)

    def clearColor(self):
        self.colors.resetColorsOfAllVertices(self.colorTable)
        self.tree.CheckedShallowCopy(self.graph)

    def highlightChildren(self):
        childrenIds = self.children[self.selected[0]]
        cid = self.colors.colorIndex('red')
        self.colors.updateColorsOfVertices(self.colorTable, childrenIds, 'red')
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
    
class Coloring:
    def __init__(self):
        self.reservedColor = [('red', RGB(1.0, 0, 0)), ('green', RGB(0, 1.0, 0.0)), ('blue', RGB(0.0, 0.0, 1.0))]
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
                self.allColors[i] = (tmpVid, tmpIndex, self.calculateColorByIndex(self.grades, tmpIndex))
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
                    lastVid, lastIndex, lastC = self.allColors[len(self.allColors)-1]
                    self.allColors[i] = (vid, lastIndex, self.calculateColorByIndex(self.grades, lastIndex))
                    removed = True
        else:
            for i in range(len(self.allColors)):
                vid, index, c = self.allColors[i]
                if vid == removedVid:
                    lastVid, lastIndex, lastC = self.allColors[len(self.allColors)-1]
                    self.allColors[i] = (vid, lastIndex, self.calculateColorByIndex(self.grades, lastIndex))
                    removed = True
                    break
        if not removed:
            print('Cannot remove color tuple with vid:', removedVid)
            removed = True
        else:
            self.allColors.pop(len(self.allColors)-1)

    def updateLookupTable(self, lookupTable):
        nt = len(self.allColors)
        lookupTable.SetNumberOfTableValues(nt)
        i = 0
        for ct in self.allColors:
            c = ct[2]
            lookupTable.SetTableValue(i, c.r, c.g, c.b)
            i = i + 1

    def updateColorOfVertex(self, lookupTable, updatedVid, cname):
        self.updateColorTuple(updatedVid, cname)
        self.updateLookupTable(lookupTable)
    def updateColorsOfVertices(self, lookupTable, updatedVids, cname):
        for vid in updatedVids:
            self.updateColorTuple(vid, cname)
        self.updateLookupTable(lookupTable)
    def resetColorOfVertex(self, lookupTable, resetVid):
        self.resetColorTuple(resetVid)
        self.updateLookupTable(lookupTable)
    def resetColorsOfAllVertices(self, lookupTable):
        self.resetAllColorTuples()
        self.updateLookupTable(lookupTable)
    def insertColorOfVertex(self, lookupTable, newVid, newIndex, newGrades):
        gradesChanged = False
        if newGrades != self.grades:
            self.setGrades(newGrades)
            gradesChanged = True
        self.insertColorTuple(newVid, newIndex, gradesChanged)
        self.updateLookupTable(lookupTable)
    def removeColorOfVertex(self, lookupTable, removedVid, newGrades):
        gradesChanged = False
        if newGrades != self.grades:
            self.setGrades(newGrades)
            gradesChanged = True
        self.removeColorTuple(removedVid, gradesChanged)
        self.updateLookupTable(lookupTable)

class FixedColoring(Coloring):
    def __init__(self):
        Coloring.__init__(self)
        self.allColors = [('green', RGB(0,1,0)), ('red', RGB(1,0,0))]

    def colorIndex(self, cname):
        for i in range(len(self.allColors)):
            # print('color', i,':', self.reservedColor[i][0])
            nc = self.allColors[i]
            if nc[0] == cname:
                return i
        return 0
    def updateLookupTable(self, lookupTable):
        nr = len(self.allColors)
        lookupTable.SetNumberOfTableValues(nr)
        for i in range(nr):
            (nc,c) = self.allColors[i]
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