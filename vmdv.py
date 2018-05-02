import sys
import session
from services import network, messenger
import collections
import threading
from PyQt5.QtWidgets import QApplication

jsonSem = threading.Semaphore(0)
jsonQueue = collections.deque([])

# affectSem = threading.Semaphore(0)
affectQueue = collections.deque([])

def putJSON(data):
    jsonQueue.append(data)
    jsonSem.release()

def fetchJSON():
    # print('fetching json message')
    jsonSem.acquire()
    # print('json message fetched')
    return jsonQueue.popleft()

def putAffect(affect):
    global affectQueue
    affectQueue.append(affect)
    # affectSem.release()

def fetchAffect():
    # print('fetching affect object')
    # affectSem.acquire()
    # print('fetched affect object')
    global affectQueue
    if len(affectQueue) != 0:
        return affectQueue.popleft()
    else:
        return None

sessions = {}

def findSession(sid):
    return sessions[sid]

def initSession(sid, descr, attris, graphType):
    global sessions
    if graphType == 'Tree':
        s = session.TreeSession(descr, attris)
        sessions[sid] = s
        s.showViewer()
        print('Showed a Tree:', sid)
    else:
        s = session.DiGraphSession(descr, attris)
        sessions[sid] = s
        s.showViewer()
        print('Showed a DiGraph', sid)

def handleAffect(a):
    # a = fetchAffect()
    if a != None:
        a.affect()
        print('main thread performed an affect')
    else:
        print('Main thread fetched a None affect')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    jsonThread = threading.Thread(target=network.listen, args=(3333,))
    # affectThread = threading.Thread(target=messenger.parseJSON, args=())
    affectThread = messenger.Messenger()
    affectThread.initSessionSignal.connect(initSession)
    affectThread.affectSignal.connect(handleAffect)
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
