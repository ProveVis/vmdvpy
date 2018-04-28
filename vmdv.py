import sys
import session
from services import network, messenger, handleAffect
import collections
import threading
from PyQt5.QtWidgets import QApplication

jsonSem = threading.Semaphore(0)
jsonQueue = collections.deque([])

affectSem = threading.Semaphore(0)
affectQueue = collections.deque([])

def putJSON(data):
    jsonQueue.append(data)
    jsonSem.release()

def fetchJSON():
    jsonSem.acquire()
    return jsonQueue.popleft()

def putAffect(affect):
    affectQueue.append(affect)
    affectSem.release()

def fetchAffect():
    affectSem.acquire()
    return affectQueue.popleft()

sessions = {}

# def 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    jsonThread = threading.Thread(target=network.listen, args=(3333,))
    affectThread = threading.Thread(target=messenger.parseJSON, args=())
    handleAffectThread = threading.Thread(target=handleAffect.handle, args=())
    jsonThread.start()
    affectThread.start()    
    handleAffectThread.start()
    # QtGui.Q

    # session = TreeSession('hello',[])
    # session.showViewer()

    # digraphSession = DiGraphSession('digraph viewer',[])
    # digraphSession.showViewer()

    sys.exit(app.exec_())
