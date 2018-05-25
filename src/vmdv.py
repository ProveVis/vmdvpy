import sys
import messenger
import collections
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import utils, viewer
import trigger
import socket
import logging
import os

class VMDV:
    def __init__(self):
        self.affectSem = threading.Semaphore(0)
        self.affectQueue = collections.deque([])

        self.msgSem = threading.Semaphore(0)
        self.msgQueue = collections.deque([])

        self.viewers = {}
        self.jsonThread = None
        

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

    def putMsg(self, m):
        self.msgQueue.append(m)
        self.msgSem.release()

    def fetchMsg(self):
        self.msgSem.acquire()
        return self.msgQueue.popleft()

    def findViewer(self, sid):
        return self.viewers[sid]

    def initSession(self, sid, descr, attris, graphType):
        print('showing viewer in thread:', threading.current_thread())
        if graphType == 'Tree':
            tviewer = viewer.TreeViewer(self, sid, descr, attris, utils.GradualColoring(utils.RGB(0,0,1), utils.RGB(0,1,0)))
            tviewer.addBackgroundMenuItem(trigger.ClearColorTrigger(tviewer, fromVMDV=True))
            tviewer.addForegroundMenuItem(trigger.HighlightNodesTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.HighlightChildrenTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.HighlightAncestorsTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.HighlightSubtreeTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.PrintColorDataTrigger(tviewer))
            tviewer.addBackgroundMenuItem(trigger.PrintColorDataTrigger(tviewer))
            tviewer.affectSignal.connect(self.handleAffect)
            self.viewers[sid] = tviewer
            tviewer.show()
            print('Showed a Tree:', sid)
        else:
            gviewer = viewer.DiGraphViewer(self, sid, descr, attris, utils.FixedColoring())
            gviewer.addBackgroundMenuItem(trigger.ClearColorTrigger(viewer))
            gviewer.affectSignal.connect(self.handleAffect)
            self.viewers[sid] = gviewer
            gviewer.show()
            print('Showed a DiGraph', sid)
        
    def handleAffect(self, sid, a):
        # print('handling affect')
        if sid == '':
            a.affect()
        else:    
            viewer = self.viewers[sid]
            viewer.handleAffect(a)

    def closeViewer(self, sid):
        viewer = self.viewers.pop(sid)
        if len(self.viewers) == 0:
            self.jsonThread.stop()
        viewer.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # os.system('rm -f log/globalLog.txt')
    # fileLogger = logging.getLogger('file')
    # fileLogger.addHandler(logging.FileHandler('log/globalLog.txt'))
    # fileLogger.setLevel(logging.DEBUG)
    cliLogger = logging.getLogger('cli')
    cliLogger.addHandler(logging.StreamHandler(sys.stdout))
    v = VMDV()
    # affectThread = messenger.AffectParser(v)
    # affectThread.affectSignal.connect(v.handleAffect)
    # affectThread.start()
    jsonThread = messenger.Receiver(v)
    jsonThread.initSessionSignal.connect(v.initSession)
    jsonThread.affectSignal.connect(v.handleAffect)
    jsonThread.start()

    sys.exit(app.exec_())
