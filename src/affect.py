import sys
import viewer
import vmdv
import graph
import utils
import messenger
import trigger
import abc
from collections import deque

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

class ShowNodeLabelAffect(Affect):
    def __init__(self, vids):
        self.vids = vids
    def affect(self, gviewer):
        label = gviewer.vertices[self.vids[0]].getProperty('label')
        gviewer.showNodeText(label)

class HighlightNodeAffect(Affect):
    def __init__(self, nid):
        self.nid = nid
    def affect(self, gviewer):
        vid = gviewer.nid2Vid[self.nid]
        if gviewer.__class__.__name__ == viewer.TreeViewer.__name__:
            gviewer.colors.updateColorOfVertex(gviewer.lookupTable, vid, 'red')
            gviewer.colors.updateLookupTable(gviewer.lookupTable)
            gviewer.updateRendering()
            gviewer.vmdv.putMsg(messenger.HighlightNodeMessage(gviewer.sid, self.nid))
        elif gviewer.__class__.__name__ == viewer.DiGraphViewer.__name__:
            gviewer.colors.setVertexColorByName(gviewer.lookupTable, gviewer.colorArray, vid, 'red')
            gviewer.updateRendering()

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
            for vid in childrenVids:
                nid = tviewer.vertices[vid].getProperty('id')
                tviewer.vmdv.putMsg(messenger.HighlightNodeMessage(tviewer.sid, nid))

class HighlightSubtreeAffect(Affect):
    def __init__(self, vids):
        self.vids = vids

    def affect(self, tviewer):
        if tviewer.__class__.__name__ == viewer.DiGraphViewer.__name__:
            print('Cannot highlight subtree in DiGraphs')
        elif tviewer.__class__.__name__ == viewer.TreeViewer.__name__:
            hvids = set([])
            tmpQ = deque([])
            for vid in self.vids:
                tmpQ.append(vid)
                while len(tmpQ) != 0:
                    tmpVid = tmpQ.popleft()
                    hvids.add(tmpVid)
                    for cvid in tviewer.children[tmpVid]:
                        tmpQ.append(cvid)
            tviewer.colors.updateColorsOfVertices(tviewer.lookupTable, list(hvids), 'red')
            tviewer.colors.updateLookupTable(tviewer.lookupTable)
            tviewer.updateRendering()
            for vid in hvids:
                nid = tviewer.vertices[vid].getProperty('id')
                tviewer.vmdv.putMsg(messenger.HighlightNodeMessage(tviewer.sid, nid))

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
            for vid in ancestorsVids:
                nid = tviewer.vertices[vid].getProperty('id')
                tviewer.vmdv.putMsg(messenger.HighlightNodeMessage(tviewer.sid, nid))

class ClearColorAffect(Affect):
    def __init__(self, fromVMDV=False):
        self.fromVMDV = fromVMDV
    def affect(self, viewer):
        if self.fromVMDV:
            viewer.vmdv.putMsg(messenger.ClearColorMessage(viewer.sid))
        viewer.resetGraphColor()
        viewer.showNodeText('')

class PrintColorDataAffect(Affect):
    def affect(self, viewer):
        print('ColorArray:', viewer.colorArray.GetNumberOfTuples())
        for i in range(viewer.colorArray.GetNumberOfTuples()):
            print('(',i,',', viewer.colorArray.GetValue(i) ,')', end=';')
        print('\nColorTable:', viewer.lookupTable.GetNumberOfTableValues())
        for j in range(viewer.lookupTable.GetNumberOfTableValues()):
            print('(', j, viewer.lookupTable.GetTableValue(j), ')', end=';\n')

class ParseResponseAffect(Affect):
    def __init__(self, rname, rargs, result):
        self.rname = rname
        self.rargs = rargs
        self.result = result

    def affect(self, gviewer):
        if self.rname == 'zone_aircraft_number':
            for si in self.result:
                n = int(si)
                nids = self.result[si].split(',')
                # nids.remove('')
                vids = [gviewer.nid2Vid[x] for x in nids]
                if n == 0:
                    gviewer.colors.setVerticesColorByName(gviewer.lookupTable, gviewer.colorArray, vids, 'c0')
                elif n == 1:
                    gviewer.colors.setVerticesColorByName(gviewer.lookupTable, gviewer.colorArray, vids, 'c1')
                elif n == 2:
                    gviewer.colors.setVerticesColorByName(gviewer.lookupTable, gviewer.colorArray, vids, 'c2')
                elif n == 3:
                    gviewer.colors.setVerticesColorByName(gviewer.lookupTable, gviewer.colorArray, vids, 'c3')
                elif n == 4:
                    gviewer.colors.setVerticesColorByName(gviewer.lookupTable, gviewer.colorArray, vids, 'c4')
                else:
                    print('More than 4 aircraft in a zone')
                gviewer.updateRendering()
                print('Response Node color set')

class SubFormulaAffect(Affect):
    def __init__(self, rname, rargs, result):
        self.rname = rname
        self.rargs = rargs
        self.result = result

    def affect(self, tviewer):
        print('SubFormulaAffect')
        nidstr = self.result['nids']
        nids = nidstr.split(',')
        vids = [tviewer.nid2Vid[x] for x in nids]
        for vid in vids:
            print('highlighting vid', vid)
            tviewer.colors.updateColorOfVertex(tviewer.lookupTable, vid, 'red')
            tviewer.colors.updateLookupTable(tviewer.lookupTable)
        tviewer.updateRendering()

class ShowRuleAffect(Affect):
    def __init__(self, rname, rargs, result):
        self.rname = rname
        self.rargs = rargs
        self.result = result
    def affect(self, viewer):
        nidstr = self.result['nids']
        nids = nidstr.split(',')
        vids = [viewer.nid2Vid[x] for x in nids]
        for vid in vids:
            print('highlighting vid', vid)
            viewer.colors.updateColorOfVertex(viewer.lookupTable, vid, 'red')
            viewer.colors.updateLookupTable(viewer.lookupTable)
        viewer.updateRendering()
class SetProofRuleAffect(Affect):
    def __init__(self, nid, rule):
        self.nid = nid
        self.rule = rule
    def affect(self, viewer):
        vid = viewer.nid2Vid[self.nid]
        viewer.rules[vid] = self.rule
