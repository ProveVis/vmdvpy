import sys
import session
from services import network, messenger
import collections
import threading
from PyQt5.QtWidgets import QApplication

class VMDV:

    jsonSem = threading.Semaphore(0)
    jsonQueue = collections.deque([])

    # affectSem = threading.Semaphore(0)
    affectQueue = collections.deque([])

    sessions = {}

    def putJSON(self, data):
        self.jsonQueue.append(data)
        self.jsonSem.release()

    def fetchJSON(self):
        # print('fetching json message')
        self.jsonSem.acquire()
        # print('json message fetched')
        return self.jsonQueue.popleft()

    def putAffect(self, affect):
        # global affectQueue
        self.affectQueue.append(affect)
        # affectSem.release()

    def fetchAffect(self):
        # print('fetching affect object')
        # affectSem.acquire()
        # print('fetched affect object')
        # global affectQueue
        if len(self.affectQueue) != 0:
            return self.affectQueue.popleft()
        else:
            return None



    def findSession(self, sid):
        return self.sessions[sid]

    def initSession(self, sid, descr, attris, graphType):
        # global sessions
        if graphType == 'Tree':
            s = session.TreeSession(descr, attris)
            self.sessions[sid] = s
            s.showViewer()
            print('Showed a Tree:', sid)
        else:
            s = session.DiGraphSession(descr, attris)
            self.sessions[sid] = s
            s.showViewer()
            print('Showed a DiGraph', sid)

    def handleAffect(self, a):
        # a = fetchAffect()
        if a != None:
            a.affect(self)
            # print('main thread performed an affect')
        else:
            pass
            # print('Main thread fetched a None affect')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    v = VMDV()
    # jsonThread = threading.Thread(target=network.listen, args=(v,3333,))
    jsonThread = network.Network(v, 3333)
    # affectThread = threading.Thread(target=messenger.parseJSON, args=())
    affectThread = messenger.Messenger(v)
    affectThread.initSessionSignal.connect(v.initSession)
    affectThread.affectSignal.connect(v.handleAffect)
    # handleAffectThread = threading.Thread(target=handleAffect.handle, args=())
    jsonThread.start()
    affectThread.start()    
    # handleAffectThread.start()
    # QtGui.Q

    # session = TreeSession('hello',[])
    # session.showViewer()

    # digraphSession = DiGraphSession('digraph viewer',[])
    # digraphSession.showViewer()

    sys.exit(app.exec_())
