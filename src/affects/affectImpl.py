from affects import affect
import sys
sys.path.append('..')
import session
import vmdv
import graph
from viewers import *

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
            # selectedNids = s.getSelectedNids()


class HighlightAncestorsAffect(affect.Affect):
    def __init__(self, nids):
        self.nids = nids
    def affect(self,s):
        if s.__class__.__name__ == session.DiGraphSession.__name__:
            print('Cannot highlight children nodes for DiGraphs')
        elif s.__class__.__name__ == session.TreeSession.__name__:
            # selectedNids = s.getSelectedNids()        


class ClearColorAffect(affect.Affect):
    