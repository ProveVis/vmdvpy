from affects import affect
import sys
sys.path.append('..')
import session
import vmdv
import graph

class AddNodeAffect(affect.Affect):
    def __init__(self, sid, nid, label, state):
        self.nid = nid
        self.sid = sid
        self.label = label
        self.state = state

    def affect(self):
        session = vmdv.findSession(self.sid)
        node = graph.Node()
        node.setProperty('id', self.nid)
        node.setProperty('label', self.label)
        node.setProperty('state', self.state)
        session.addNode(node)
        # pass
        
class AddEdgeAffect(affect.Affect):
    def __init__(self, sid, fromId, toId, label=None):
        self.sid = sid
        self.fromId = fromId
        self.toId = toId
        self.label = label

    def affect(self):
        s = vmdv.findSession(self.sid)
        if s.__class__ == 'TreeSession':
            s.addEdge(self.fromId, self.toId, self.label)
        elif s.__class__ == 'DiGraphSession':
            s.addEdge(self.fromId, self.toId)
        else:
            print("Unknown session type in AddEdgeAffect:", s.__class__.name)