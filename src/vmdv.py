import sys
import session
from services import messenger
import collections
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from viewers import utils
from operations import trigger
import socket

class VMDV:
    def __init__(self):
        self.affectSem = threading.Semaphore(0)
        self.affectQueue = collections.deque([])

        self.msgSem = threading.Semaphore(0)
        self.msgQueue = collections.deque([])

        self.sessions = {}
        

    # def putJSON(self, data):
    #     self.jsonQueue.append(data)
    #     self.jsonSem.release()

    # def fetchJSON(self):
    #     self.jsonSem.acquire()
    #     return self.jsonQueue.popleft()

    def putAffect(self, sid, a):
        # global affectQueue
        self.affectQueue.append((sid, a))
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

    def putMsg(self, m):
        self.msgQueue.append(m)
        self.msgSem.release()

    def fetchMsg(self):
        self.msgSem.acquire()
        return self.msgQueue.popleft()

    def findSession(self, sid):
        return self.sessions[sid]

    def initSession(self, sid, descr, attris, graphType):
        # global sessions
    # public static final RGBColor fromColor = new RGBColor(44.0f/255,82.0f/255,68.0f/255);
	# public static final RGBColor toColor = new RGBColor(0,1,0);
        print('showing viewer in thread:', threading.current_thread())
        if graphType == 'Tree':
            s = session.TreeSession(self, sid, descr, attris, utils.GradualColoring(utils.RGB(44/255,82/255,68/255), utils.RGB(0,1,0)))
            s.viewer.addBackgroundMenuItem(trigger.ClearColorTrigger(s))
            s.viewer.addForegroundMenuItem(trigger.HighlightChildrenTrigger(s))
            s.viewer.addForegroundMenuItem(trigger.HighlightAncestorsTrigger(s))
            s.viewer.affectSignal.connect(self.handleAffect)
            self.sessions[sid] = s
            s.showViewer()
            print('Showed a Tree:', sid)
        else:
            s = session.DiGraphSession(self, sid, descr, attris, utils.FixedColoring())
            s.viewer.addBackgroundMenuItem(trigger.ClearColorTrigger(s))
            s.viewer.affectSignal.connect(self.handleAffect)
            self.sessions[sid] = s
            s.showViewer()
            print('Showed a DiGraph', sid)
        
        # self.affectThread.start()    

    def handleAffect(self, sid, a):
        print('handling affect')
        if sid == '':
            a.affect()
        else:    
            s = self.sessions[sid]
            s.handleAffect(a)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    v = VMDV()
    affectThread = messenger.AffectParser(v)
    affectThread.affectSignal.connect(v.handleAffect)
    affectThread.start()
    jsonThread = messenger.Receiver(v)
    jsonThread.initSessionSignal.connect(v.initSession)
    jsonThread.affectSignal.connect(v.handleAffect)
    # affectThread.affectSignal.connect(v.handleAffect)
    jsonThread.start()

    sys.exit(app.exec_())
