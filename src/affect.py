import sys
import viewer
import vmdv
import graph
import utils
import messenger
import trigger
import abc

class Affect:
    def __init__(self):
        pass
    @abc.abstractmethod
    def affect(self,viewer):
        pass

class AddNodeAffect(Affect):
    def __init__(self, nid, label, state):
        self.nid = nid
        # self.sid = sid
        self.label = label
        self.state = state

    def affect(self,viewer):
        # session = v.findSession(self.sid)
        node = graph.Node()
        node.setProperty('id', self.nid)
        node.setProperty('label', self.label)
        node.setProperty('state', self.state)
        viewer.addNode(node)
        # print('Adding node', self.nid)
        # pass
        
class AddEdgeAffect(Affect):
    def __init__(self, fromId, toId, label=''):
        self.fromId = fromId
        self.toId = toId
        self.label = label

    def affect(self, viewer):
        viewer.addEdge(self.fromId, self.toId, self.label)

class HighlightChildrenAffect(Affect):
    def __init__(self, vids):
        self.vids = vids

    def affect(self, tviewer):
        if tviewer.__class__.__name__ == viewer.DiGraphViewer.__name__:
            print('Cannot highlight children nodes for DiGraphs')
        elif tviewer.__class__.__name__ == viewer.TreeViewer.__name__:
            childrenVids = []
            for vid in self.vids:
                childrenVids = childrenVids + tviewer.children[vid]
            tviewer.colors.updateColorsOfVertices(tviewer.lookupTable, childrenVids, 'red')
            tviewer.colors.updateLookupTable(tviewer.lookupTable)
            tviewer.updateRendering()
            

class HighlightAncestorsAffect(Affect):
    def __init__(self, vids):
        self.vids = vids
    def affect(self, tviewer):
        if tviewer.__class__.__name__ == viewer.DiGraphViewer.__name__:
            print('Cannot highlight children nodes for DiGraphs')
        elif tviewer.__class__.__name__ == viewer.TreeViewer.__name__:
            ancestorsVids = []
            for vid in self.vids:
                if vid in tviewer.parent:
                    tmpVid = tviewer.parent[vid]
                    while True:
                        ancestorsVids.append(tmpVid)
                        if tmpVid in tviewer.parent:
                            tmpVid = tviewer.parent[tmpVid]
                        else:
                            break
                # ancestorsVids.append(viewer.parent[vid])
            tviewer.colors.updateColorsOfVertices(tviewer.lookupTable, ancestorsVids, 'red')
            tviewer.colors.updateLookupTable(tviewer.lookupTable)
            tviewer.updateRendering()


class ClearColorAffect(Affect):
    def affect(self, viewer):
        viewer.vmdv.putMsg(messenger.ClearColorMessage(viewer.sid))
        viewer.resetGraphColor()

class PrintColorDataAffect(Affect):
    def affect(self, viewer):
        print('ColorArray:', viewer.colorArray.GetNumberOfTuples())
        for i in range(viewer.colorArray.GetNumberOfTuples()):
            print('(',i,',', viewer.colorArray.GetValue(i) ,')', end=';')
        print('\nColorTable:', viewer.lookupTable.GetNumberOfTableValues())
        for j in range(viewer.lookupTable.GetNumberOfTableValues()):
            print('(', j, viewer.lookupTable.GetTableValue(j), ')', end=';\n')