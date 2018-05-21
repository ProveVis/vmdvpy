from affects import affect
import sys
sys.path.append('..')
from viewers import treeviewer, digraphviewer
import vmdv
import graph
from viewers import utils
from services import messenger
from operations import trigger

# class InitSessionAffect(affect.Affect):
#     def __init__(self, v, sid, descr, attris, graphType):
#         self.v = v
#         self.sid = sid
#         self.descr = descr
#         self.attris = attris
#         self.graphType = graphType

#     def affect(self, s = None):
#         if self.graphType == 'Tree':
#             s = session.TreeSession(self, self.sid, self.descr, self.attris, utils.GradualColoring(utils.RGB(44/255,82/255,68/255), utils.RGB(0,1,0)))
#             s.viewer.addBackgroundMenuItem(trigger.ClearColorTrigger(s))
#             s.viewer.addForegroundMenuItem(trigger.HighlightChildrenTrigger(s))
#             s.viewer.addForegroundMenuItem(trigger.HighlightAncestorsTrigger(s))
#             self.v.sessions[self.sid] = s
#             s.showViewer()
#             print('Showed a Tree:', self.sid)
#         else:
#             s = session.DiGraphSession(self, self.sid, self.descr, self.attris, utils.FixedColoring())
#             s.viewer.addBackgroundMenuItem(trigger.ClearColorTrigger(s))
#             self.v.sessions[self.sid] = s
#             s.showViewer()
#             print('Showed a DiGraph', self.sid)

class AddNodeAffect(affect.Affect):
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
        
class AddEdgeAffect(affect.Affect):
    def __init__(self, fromId, toId, label=''):
        self.fromId = fromId
        self.toId = toId
        self.label = label

    def affect(self, viewer):
        viewer.addEdge(self.fromId, self.toId, self.label)

class HighlightChildrenAffect(affect.Affect):
    def __init__(self, vids):
        self.vids = vids

    def affect(self, viewer):
        if viewer.__class__.__name__ == digraphviewer.DiGraphViewer.__name__:
            print('Cannot highlight children nodes for DiGraphs')
        elif viewer.__class__.__name__ == treeviewer.TreeViewer.__name__:
            childrenVids = []
            for vid in self.vids:
                childrenVids = childrenVids + viewer.children[vid]
            viewer.colors.updateColorsOfVertices(viewer.lookupTable, childrenVids, 'red')
            viewer.colors.updateLookupTable(viewer.lookupTable)
            viewer.updateRendering()
            

class HighlightAncestorsAffect(affect.Affect):
    def __init__(self, vids):
        self.vids = vids
    def affect(self, viewer):
        if viewer.__class__.__name__ == digraphviewer.DiGraphViewer.__name__:
            print('Cannot highlight children nodes for DiGraphs')
        elif viewer.__class__.__name__ == treeviewer.TreeViewer.__name__:
            ancestorsVids = []
            for vid in self.vids:
                if vid in viewer.parent:
                    tmpVid = viewer.parent[vid]
                    while True:
                        ancestorsVids.append(tmpVid)
                        if tmpVid in viewer.parent:
                            tmpVid = viewer.parent[tmpVid]
                        else:
                            break
                # ancestorsVids.append(viewer.parent[vid])
            viewer.colors.updateColorsOfVertices(viewer.lookupTable, ancestorsVids, 'red')
            viewer.colors.updateLookupTable(viewer.lookupTable)
            viewer.updateRendering()


class ClearColorAffect(affect.Affect):
    def affect(self, viewer):
        viewer.vmdv.putMsg(messenger.ClearColorMessage(viewer.sid))
        viewer.resetGraphColor()

class PrintColorDataAffect(affect.Affect):
    def affect(self, viewer):
        print('ColorArray:', viewer.colorArray.GetNumberOfTuples())
        for i in range(viewer.colorArray.GetNumberOfTuples()):
            print('(',i,',', viewer.colorArray.GetValue(i) ,')', end=';')
        print('\nColorTable:', viewer.lookupTable.GetNumberOfTableValues())
        for j in range(viewer.lookupTable.GetNumberOfTableValues()):
            print('(', j, viewer.lookupTable.GetTableValue(j), ')', end=';\n')