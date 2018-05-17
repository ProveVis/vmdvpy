import sys
sys.path.append('..')
import vmdv
import session
from affects import affect, affectImpl
# from affects import affect
from PyQt5.QtCore import QThread
from PyQt5 import QtCore
import abc
import json
import socket

class Receiver(QThread):
    def __init__(self, v, parent=None):
        super(Receiver, self).__init__(parent)
        self.v = v
        # self.sock = sock

    initSessionSignal = QtCore.pyqtSignal(str, str, list, str)
    affectSignal = QtCore.pyqtSignal(str, affect.Affect)

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 3333))
        s.listen()
        connSock, address = s.accept()
        print('Connection established with a prover: ', address)
        
        msgThread = Sender(self.v, connSock)
        
        msgThread.start()
        while True:
            recvdBytes = connSock.recv(40960)
            if not recvdBytes:
                print('network receiving data error')
                sys.exit(1)
                break
            # else:
            #     print('Received Json object:', recvdStr)
            recvdStrs = recvdBytes.decode('utf-8').split('\n')
            for recvdStr in recvdStrs:
                try:
                    data = json.loads(recvdStr)
                    t = data['type']
                    # print('Received a json object:', t)
                    if t == 'create_session':
                        if data['graph_type'] == 'Tree':
                            attris = []
                            if 'attributes' in data:
                                attris = data['attributes']
                            # self.v.putAffect('', affectImpl.InitSessionAffect(self.v, data['session_id'], data['session_descr'], attris, 'Tree'))
                            # self.v.initSession(data['session_id'], data['session_descr'], attris, 'Tree')
                            self.initSessionSignal.emit(data['session_id'], data['session_descr'], attris, 'Tree')
                        elif data['graph_type'] == 'DiGraph':
                            attris = []
                            if 'attributes' in data:
                                attris = data['attributes']
                            # self.v.putAffect('', affectImpl.InitSessionAffect(self.v, data['session_id'], data['session_descr'], attris, 'DiGraph'))    
                            # self.v.initSession(data['session_id'], data['session_descr'], attris, 'DiGraph')
                            self.initSessionSignal.emit(data['session_id'], data['session_descr'], attris, 'DiGraph')
                        else:
                            print('Unknown graph type:', data['graph_type'])
                    elif t == 'remove_session':
                        self.v.sessions.pop(data['session_id'])
                    elif t == 'add_node':
                        a = affectImpl.AddNodeAffect(data['node']['id'], data['node']['label'], data['node']['state'])
                        # self.v.putAffect(data['session_id'], a)
                        self.affectSignal.emit(data['session_id'], a)
                    elif t == 'add_edge':
                        a = None
                        if 'label' in data:
                            a = affectImpl.AddEdgeAffect(data['from_id'], data['to_id'], data['label'])
                        else:
                            a = affectImpl.AddEdgeAffect(
                                data['session_id'], data['from_id'], data['to_id'])
                        # self.v.putAffect(data['session_id'], a)
                        self.affectSignal.emit(data['session_id'], a)
                    elif t == 'feedback':
                        if data['status'] == 'OK':
                            print('Session received feedback from the prover:',
                                  data['session_id'], ',', data['status'])
                        else:
                            print('Session received feedback from the prover:',
                                  data['session_id'], ',', data['status'], ',', data['error_msg'])
                except json.decoder.JSONDecodeError:
                    # print('json loads error:', recvdStr)
                    pass

# class AffectParser(QThread):
#     def __init__(self, v, parent = None):
#         super(AffectParser, self).__init__(parent)
#         self.v = v

#     affectSignal = QtCore.pyqtSignal(str, affect.Affect)

#     def run(self):
#         print('Affect parser thread start...')
#         while True:
#             (sid, a) = self.v.fetchAffect()
#             self.affectSignal.emit(sid, a)



class Message:
    @abc.abstractmethod
    def toJson(self):
        pass
class ClearColorMessage(Message):
    def __init__(self, sid):
        self.sid = sid
    def toStr(self):
        return (json.dumps({'type':'clear_color', 'session_id': self.sid}))+'\n'


class Sender(QThread):
    def __init__(self, v, sock, parent = None):
        QThread.__init__(self, parent)
        self.v = v
        self.sock = sock

    def run(self):
        print('Sender thread start...')
        while True:
            m = self.v.fetchMsg()
            self.sock.sendall(m.toStr().encode('utf-8'))
            