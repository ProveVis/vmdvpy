import sys
import session
from services import network, messenger
import collections
import threading
from PyQt5.QtWidgets import QApplication
from viewers import utils
from operations import trigger

class VMDV:

    jsonSem = threading.Semaphore(0)
    jsonQueue = collections.deque([])

    affectSem = threading.Semaphore(0)
    affectQueue = collections.deque([])

    sessions = {}

    def putJSON(self, data):
        self.jsonQueue.append(data)
        self.jsonSem.release()

    def fetchJSON(self):
        self.jsonSem.acquire()
        return self.jsonQueue.popleft()

    def putAffect(self, a):
        # global affectQueue
        self.affectQueue.append(a)
        self.affectSem.release()

    def fetchAffect(self):
        # print('fetching affect object')
        self.affectSem.acquire()
        return self.affectQueue.popleft()
        # print('fetched affect object')
        # global affectQueue
        # if len(self.affectQueue) != 0:
        #     return self.affectQueue.popleft()
        # else:
        #     return None



    def findSession(self, sid):
        return self.sessions[sid]

    def initSession(self, sid, descr, attris, graphType):
        # global sessions
    # public static final RGBColor fromColor = new RGBColor(44.0f/255,82.0f/255,68.0f/255);
	# public static final RGBColor toColor = new RGBColor(0,1,0);
        if graphType == 'Tree':
            s = session.TreeSession(self, sid, descr, attris, utils.GradualColoring(utils.RGB(44/255,82/255,68/255), utils.RGB(0,1,0)))
            s.viewer.addBackgroundMenuItem(trigger.ClearColorTrigger(s))
            s.viewer.addForegroundMenuItem(trigger.HighlightChildrenTrigger(s))
            s.viewer.addForegroundMenuItem(trigger.HighlightAncestorsTrigger(s))
            self.sessions[sid] = s
            s.showViewer()
            print('Showed a Tree:', sid)
        else:
            s = session.DiGraphSession(self, sid, descr, attris, utils.FixedColoring())
            s.viewer.addBackgroundMenuItem(trigger.ClearColorTrigger(s))
            self.sessions[sid] = s
            s.showViewer()
            print('Showed a DiGraph', sid)

    def handleAffect(self, sid, a):
        s = self.sessions[sid]
        s.handleAffect(a)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    v = VMDV()
    jsonThread = network.Network(v, 3333)
    affectThread = messenger.Receiver(v)
    affectThread.initSessionSignal.connect(v.initSession)
    affectThread.affectSignal.connect(v.handleAffect)
    jsonThread.start()
    affectThread.start()    
    sys.exit(app.exec_())
