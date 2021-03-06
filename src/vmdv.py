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

        self.requestId = 0
        # Each pair in pendingRequests has the form (k: str, v: (str, dict))
        self.pendingRequests = {}

        # Each pair in responseCache has the form (k: (str, str), v: dict)
        self.responseCache = {}

    def newRequestId(self):
        newId = str(self.requestId)
        self.requestId += 1
        return newId
    def addPendingRequest(self, rid, rname, rargs):
        self.pendingRequests[rid] = (rname, rargs)
        
    def putAffect(self, sid, a):
        self.affectQueue.append((sid, a))
        self.affectSem.release()

    def fetchAffect(self):
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
        # print('showing viewer in thread:', threading.current_thread())
        if graphType == 'Tree':
            tviewer = viewer.TreeViewer(self, sid, descr, attris, utils.GradualColoring(utils.RGB(0,0,1), utils.RGB(0,1,0)))
            tviewer.addBackgroundMenuItem(trigger.ClearColorTrigger(tviewer, fromVMDV=True))
            tviewer.addForegroundMenuItem(trigger.ShowNodeLabelTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.HighlightNodesTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.HighlightChildrenTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.HighlightAncestorsTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.HighlightSubtreeTrigger(tviewer))
            # tviewer.addForegroundMenuItem(trigger.SubFormulaTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.RemoveSubproofTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.HideProofTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.RestoreProofTrigger(tviewer))
            tviewer.addBackgroundMenuItem(trigger.ShowHideRulesTrigger(tviewer))
            tviewer.addBackgroundMenuItem(trigger.HighlightCutNodesTrigger(tviewer))
            tviewer.addForegroundMenuItem(trigger.ExpandCutTrigger(tviewer))
            # tviewer.addBackgroundMenuItem(trigger.ShowRuleTrigger(tviewer, '/\\-R'))
            # tviewer.addBackgroundMenuItem(trigger.ShowRuleTrigger(tviewer, 'EU-R1'))
            # tviewer.addBackgroundMenuItem(trigger.ShowRuleTrigger(tviewer, 'EU-R2'))
            tviewer.affectSignal.connect(self.handleAffect)
            self.viewers[sid] = tviewer
            tviewer.show()
            print('Showed a Tree:', sid)
        else:
            gviewer = viewer.DiGraphViewer(self, sid, descr, attris, utils.FixedColoring())
            gviewer.addBackgroundMenuItem(trigger.ClearColorTrigger(gviewer))
            gviewer.addForegroundMenuItem(trigger.ShowNodeLabelTrigger(gviewer))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'holding3_right'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'holding3_left'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'holding2_right'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'holding2_left'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'lez_right'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'lez_left'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'base_right'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'base_left'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'intermediate'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'final'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'runway'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'maz_right'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'maz_left'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'departure_right'))
            # gviewer.addBackgroundMenuItem(trigger.ZoneAircraftNumberTrigger(gviewer, 'departure_left'))
            gviewer.affectSignal.connect(self.handleAffect)
            self.viewers[sid] = gviewer
            gviewer.show()
            print('Showed a DiGraph', sid)
        
    def handleAffect(self, sid, a):
        if sid == '':
            a.affect()
        else:    
            viewer = self.viewers[sid]
            viewer.handleAffect(a)

    def closeAllViewers(self):
        # viewer = self.viewers.pop(sid)
        # if len(self.viewers) == 0:
        #     self.jsonThread.stop()
        # viewer.close()
        self.viewers.clear()
        if self.jsonThread != None:
            self.jsonThread.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # os.system('rm -f log/globalLog.txt')
    # fileLogger = logging.getLogger('file')
    # fileLogger.addHandler(logging.FileHandler('log/globalLog.txt'))
    # fileLogger.setLevel(logging.DEBUG)
    cliLogger = logging.getLogger('cli')
    cliLogger.addHandler(logging.StreamHandler(sys.stdout))
    v = VMDV()

    if len(sys.argv) > 1:
        fileReader = messenger.FileReader(v, sys.argv[1])
        fileReader.initSessionSignal.connect(v.initSession)
        fileReader.affectSignal.connect(v.handleAffect)
        fileReader.start()
    else:
        jsonThread = messenger.Receiver(v)
        jsonThread.initSessionSignal.connect(v.initSession)
        jsonThread.affectSignal.connect(v.handleAffect)
        jsonThread.start()

    app.aboutToQuit.connect(v.closeAllViewers)
    sys.exit(app.exec_())
