from affects import affect
import sys
sys.path.append('..')
import session
import vmdv
import graph
from viewers import utils
from services import messenger
from operations import trigger

class InitSessionAffect(affect.Affect):
    def __init__(self, v, sid, descr, attris, graphType):
        self.v = v
        self.sid = sid
        self.descr = descr
        self.attris = attris
        self.graphType = graphType

    def affect(self, s = None):
        if self.graphType == 'Tree':
            s = session.TreeSession(self, self.sid, self.descr, self.attris, utils.GradualColoring(utils.RGB(44/255,82/255,68/255), utils.RGB(0,1,0)))
            s.viewer.addBackgroundMenuItem(trigger.ClearColorTrigger(s))
            s.viewer.addForegroundMenuItem(trigger.HighlightChildrenTrigger(s))
            s.viewer.addForegroundMenuItem(trigger.HighlightAncestorsTrigger(s))
            self.v.sessions[self.sid] = s
            s.showViewer()
            print('Showed a Tree:', self.sid)
        else:
            s = session.DiGraphSession(self, self.sid, self.descr, self.attris, utils.FixedColoring())
            s.viewer.addBackgroundMenuItem(trigger.ClearColorTrigger(s))
            self.v.sessions[self.sid] = s
            s.showViewer()
            print('Showed a DiGraph', self.sid)
        # self.v.affectThread.start()

class AddNodeAffect(affect.Affect):
    def __init__(self, nid, label, state):
        self.nid = nid
        # self.sid = sid
        self.label = label
        self.state = state

    def affect(self,s):
        # session = v.findSession(self.sid)
        node = graph.Node()
        node.setProperty('id', self.nid)
        node.setProperty('label', self.label)
        node.setProperty('state', self.state)
        s.addNode(node)
        # print('Adding node', self.nid)
        # pass
        
class AddEdgeAffect(affect.Affect):
    def __init__(self, fromId, toId, label=''):
        # self.sid = sid
        self.fromId = fromId
        self.toId = toId
        self.label = label

    def affect(self,s):
        # s = v.findSession(self.sid)
        if s.__class__.__name__ == session.TreeSession.__name__:
            s.addEdge(self.fromId, self.toId, self.label)
            # print('Adding tree edge', self.fromId, '-->', self.toId)
        elif s.__class__.__name__ == session.DiGraphSession.__name__:
            s.addEdge(self.fromId, self.toId, self.label)
            # print('Adding digraph edge', self.fromId, '-->', self.toId)
        else:
            print("Unknown session type in AddEdgeAffect:", s.__class__.__name__)

class HighlightChildrenAffect(affect.Affect):
    def __init__(self, nids):
        # pass
        # self.sesion = sesion
        self.nids = nids

    def affect(self,s):
        if s.__class__.__name__ == session.DiGraphSession.__name__:
            print('Cannot highlight children nodes for DiGraphs')
        elif s.__class__.__name__ == session.TreeSession.__name__:
            childrenIds = []
            for nid in self.nids:
                childrenIds = childrenIds + s.tree.getChildren(nid)
            vids = map(lambda x: s.viewer.nid2Vertex[x], childrenIds)
            for vid in vids:
                s.viewer.setVertexColorByName(vid, 'red')

            # selectedNids = s.getSelectedNids()


class HighlightAncestorsAffect(affect.Affect):
    def __init__(self, nids):
        self.nids = nids
    def affect(self,s):
        if s.__class__.__name__ == session.DiGraphSession.__name__:
            print('Cannot highlight children nodes for DiGraphs')
        elif s.__class__.__name__ == session.TreeSession.__name__:
            ancestorsIds = []
            for nid in self.nids:
                ancestorsIds = ancestorsIds + s.tree.getAncestors(nid)
            vids = map(lambda x: s.viewer.nid2Vertex[x], ancestorsIds)
            for vid in vids:
                s.viewer.setVertexColorByName(vid, 'red')     


class ClearColorAffect(affect.Affect):
    def affect(self, s):
        s.v.putMsg(messenger.ClearColorMessage(s.sid))
        s.resetGraphColor()