import vtk


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
        self.reservedColor = [('red', RGB(1.0, 0.0, 0.0)), ('green', RGB(0.0, 1.0, 0.0)), ('blue', RGB(0.0, 1.0, 0.0))]

    def colorIndex(self, cname):
        for i in len(self.reservedColor):
            nc = self.reservedColor[i]
            if nc[0] == cname:
                return i
        return -1

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
            c = self.reservedColor[i]
            lookupTable.SetTableValue(i,c.r,c.g,c.b) 
        for j in range(grades):
            c = slicingColor(self.startingRgb, self.endingRgb, grades, j)
            lookupTable.SetTableValue(j+nr, c.r, c.g, c.b)

    def updateColorArray(self, colorArray, vid, node):
        nstate = node.getProperty('state')
        if nstate == 'Proved':
            colorArray.InsertValue(vid, node.height)
        else:
            print('Don\'t know to color node with state', nstate)

class FixedColoring(Coloring):
    def updateLookupTable(self, lookupTable):
        nr = len(self.reservedColor)
        lookupTable.SetNumberOfTableValues(nr)
        for i in range(nr):
            c = self.reservedColor[i]
            lookupTable.SetTableValue(i,c.r,c.g,c.b) 

    def updateColorArray(self, colorArray, vid, node):
        # (nc, c) = self.reservedColor[0]
        colorArray.InsertValue(vid, 1)
        
