import vtk

class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
    
class Coloring:
    def __init__(self):
        self.reservedColor = {
            'red':      RGB(1.0, 0, 0), 
            'green':    RGB(0, 1.0, 0.0), 
            'blue':     RGB(0.0, 0.0, 1.0)
        }
        # Each element in allColors has the form (int, int, RGB), 
        # where the first int specifies specifies the vid, the second int specifies the index, 
        # and RGB specifies the color
        self.allColors = []

    def getColorByName(self, cname):
        if cname in self.reservedColor:
            return self.reservedColor[cname]
        else:
            return None

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
        # self.updateLookupTable(lookupTable)
    def updateColorsOfVertices(self, lookupTable, updatedVids, cname):
        for vid in updatedVids:
            self.updateColorTuple(vid, cname)
        # self.updateLookupTable(lookupTable)
    def resetColorOfVertex(self, lookupTable, resetVid):
        self.resetColorTuple(resetVid)
        # self.updateLookupTable(lookupTable)
    def resetColorsOfAllVertices(self, lookupTable, colorArray):
        self.resetAllColorTuples()
        # self.updateLookupTable(lookupTable)
    def insertColorOfVertex(self, lookupTable, newVid, newIndex, newGrades):
        gradesChanged = False
        if newGrades != self.grades:
            self.setGrades(newGrades)
            gradesChanged = True
        self.insertColorTuple(newVid, newIndex, gradesChanged)
        # self.updateLookupTable(lookupTable)
    def removeColorOfVertex(self, lookupTable, removedVid, newGrades):
        gradesChanged = False
        if newGrades != self.grades:
            self.setGrades(newGrades)
            gradesChanged = True
        self.removeColorTuple(removedVid, gradesChanged)
        # self.updateLookupTable(lookupTable)

class FixedColoring(Coloring):
    def __init__(self):
        Coloring.__init__(self)
        self.allColors = [('blue', RGB(0,0,1)), ('red', RGB(1,0,0))]
        self.reservedColor = {
            'red':      RGB(1.0, 0, 0), 
            'green':    RGB(0, 1.0, 0.0), 
            'blue':     RGB(0.0, 0.0, 1.0),
            'c0':       RGB(1, 100/255, 0),
            'c1':       RGB(1, 80/255, 0),
            'c2':       RGB(1, 60/255, 0),
            'c3':       RGB(1, 40/255, 0),
            'c4':       RGB(1, 20/255, 0)
        }

    def colorIndex(self, cname):
        for i in range(len(self.allColors)):
            nc = self.allColors[i]
            if nc[0] == cname:
                return i
        return 0
    def updateLookupTable(self, lookupTable):
        nr = len(self.allColors)
        lookupTable.SetNumberOfTableValues(nr)
        # print('FixedColoring.allColors:', self.allColors)
        for i in range(nr):
            nc = self.allColors[i]
            c = nc[1]
            lookupTable.SetTableValue(i,c.r,c.g,c.b) 

    def updateVertexColor(self, colorArray, vid, cid):
        # (nc, c) = self.reservedColor[0]
        colorArray.SetValue(vid, cid)

    def setVertexColorByName(self, lookupTable, colorArray, vid, cname):
        if cname in self.reservedColor:
            color = self.reservedColor[cname]
            cindex = 0
            try:
                cindex = self.allColors.index((cname, color))
            except ValueError:
                self.allColors.append((cname, color))
                cindex = len(self.allColors) - 1
            self.updateLookupTable(lookupTable)
            self.updateVertexColor(colorArray, vid, cindex)
        else:
            print('Cannot set color of vertex', vid, ': color', cname, 'does not exist')
        # self.updateLookupTable(lookupTable)
        # self.updateVertexColor(colorArray, vid, cindex)

    def setVerticesColorByName(self, lookupTable, colorArray, vids, cname):
        if cname in self.reservedColor:
            color = self.reservedColor[cname]
            cindex = 0
            try:
                cindex = self.allColors.index((cname, color))
            except ValueError:
                self.allColors.append((cname, color))
                cindex = len(self.allColors) - 1
            self.updateLookupTable(lookupTable)
            for vid in vids:
                colorArray.SetValue(vid, cindex)
            # self.updateVertexColor(colorArray, vid, cindex)
        else:
            print('Cannot set color of vertex', vid, ': color', cname, 'does not exist')
        # self.updateLookupTable(lookupTable)
        # self.updateVertexColor(colorArray, vid, cindex)

    def resetColorsOfAllVertices(self, lookupTable, colorArray):
        nt = colorArray.GetNumberOfTuples()
        for i in range(nt):
            colorArray.SetValue(i, 0)
        self.allColors = [('blue', RGB(0,0,1)), ('red', RGB(1,0,0))]
        self.updateLookupTable(lookupTable)
