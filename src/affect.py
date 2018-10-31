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
    def __init__(self, nodeProps):
        self.nodeProps = nodeProps
        # self.nid = nid
        # self.label = label
        # self.state = state

    def affect(self,viewer):
        # session = v.findSession(self.sid)
        node = graph.Node()
        for k in self.nodeProps:
            node.setProperty(k, self.nodeProps[k])
        # node.setProperty('id', self.nid)
        # node.setProperty('label', self.label)
        # node.setProperty('state', self.state)
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
        viewer.labelArray.InsertValue(viewer.nid2Vid[self.toId], '')
        # viewer.resetGraphColor()
        # viewer.updateRendering()

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
        # vid = viewer.nid2Vid[self.nid]
        viewer.rules[self.nid] = self.rule
        viewer.labelArray.InsertValue(viewer.nid2Vid[self.nid], self.rule)
        # viewer.vertices[vid].setProperty('label', self.rule)

class RemoveSubproofAffect(Affect):
    def __init__(self, nid):
        self.nid = nid
    def affect(self,viewer):
        viewer.removeNode(self.nid)

class ChangeNodePropAffect(Affect):
    def __init__(self, nid, key, value):
        self.nid = nid
        self.key = key
        self.value = value
    def affect(self,viewer):
        vid = viewer.nid2Vid[self.nid]
        viewer.vertices[vid].setProperty(self.key, self.value)
        viewer.resetGraphColor()

class HideProofAffect(Affect):
    def __init__(self, nid):
        self.nid = nid
    def affect(self,tv):
        print('hiding proof from node', self.nid)
        vid = tv.nid2Vid[self.nid]
        prooftree = viewer.ProofTree(tv.vertices[vid])
        tmpQ = deque([])
        tmpQ.append(vid)
        while len(tmpQ) != 0:
            tmpVid = tmpQ.popleft()
            tmpNid = tv.vertices[tmpVid].getProperty('id')
            prooftree.addRule(tmpNid, tv.rules[tmpNid])
            for cvid in tv.children[tmpVid]:
                prooftree.addChild(tmpNid, tv.vertices[cvid], tv.rules[tmpNid])
                tmpQ.append(cvid)
        tv.hiddenProofs[self.nid] = prooftree
        tv.removeNode(self.nid)

class RestoreProofAffect(Affect):
    def __init__(self, nid):
        self.nid = nid

    def affect(self,viewer):
        print('restoring proof from node', self.nid)
        if self.nid not in viewer.hiddenProofs:
            return
        prooftree = viewer.hiddenProofs[self.nid]
        tmpQ = deque([])
        tmpQ.append(self.nid)
        while len(tmpQ) != 0:
            tmpNid = tmpQ.popleft()
            if tmpNid in prooftree.children:
                for cNid in prooftree.children[tmpNid]:
                    viewer.addNode(prooftree.nodes[cNid])
                    viewer.addEdge(tmpNid, cNid, prooftree.rules[tmpNid])
                    tmpQ.append(cNid)
            elif tmpNid in prooftree.rules:
                # tmpVid = viewer.nid2Vid[tmpNid]
                viewer.rules[tmpNid] = (prooftree.rules[tmpNid])

        # del viewer.hiddenProofs[self.nid]


class HideShowRulesAffect(Affect):
    def affect(self,viewer):
        viewer.view.SetVertexLabelVisibility(not viewer.view.GetVertexLabelVisibility())

class HighlightCutNodesAffect(Affect):
    def affect(self,tviewer):
        cutNodes = []
        for nid in tviewer.rules:
            vid = tviewer.nid2Vid[nid]
            rule = tviewer.rules[nid]
            splt1 = rule.split('.')
            splt2 = splt1[0].split(' ')
            if len(splt2) == 2 and splt2[0] == 'apply':
                cutNodes.append(vid)
        tviewer.colors.updateColorsOfVertices(tviewer.lookupTable, cutNodes, 'red')
        tviewer.colors.updateLookupTable(tviewer.lookupTable)
        tviewer.updateRendering()

class ExpandCutAffect(Affect):
    def __init__(self, nid, cutname):
        self.nid = nid
        self.cutname = cutname

    def affect(self, tviewer):
        tviewer.vmdv.putMsg(messenger.ExpandCutMessage(tviewer.sid, self.nid, self.cutname))

