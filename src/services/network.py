import sys
sys.path.append('..')
import vmdv
import socket
import json
from PyQt5.QtCore import QThread
from affects import affect, affectImpl


class Network(QThread):
    def __init__(self, v, port, parent=None):
        super(Network, self).__init__(parent)
        self.v = v
        self.port = port

    initSessionSignal = PyQt5.QtCore.pyqtSignal(str, str, list, str)

    def run(self):
        print('Network thread start...')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', self.port))
            s.listen()
            connection, address = s.accept()
            print('Connection established with a prover: ', address)
            with connection:
                while True:
                    recvdBytes = connection.recv(40960)
                    if not recvdBytes:
                        print('network receiving data error')
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
                                    self.initSessionSignal.emit(
                                        data['session_id'], data['session_descr'], attris, 'Tree')
                                elif data['graph_type'] == 'DiGraph':
                                    attris = []
                                    if 'attributes' in data:
                                        attris = data['attributes']
                                    self.initSessionSignal.emit(
                                        data['session_id'], data['session_descr'], attris, 'DiGraph')
                                else:
                                    print('Unknown graph type:',
                                          data['graph_type'])
                            elif t == 'remove_session':
                                self.v.sessions.pop(data['session_id'])
                            elif t == 'add_node':
                                # vmdv.putAffect(AddNodeAffect(data['session_id'], data['node']['id'], data['node']['label'], data['node']['state']))
                                a = affectImpl.AddNodeAffect(
                                    data['session_id'], data['node']['id'], data['node']['label'], data['node']['state'])
                                # self.affectSignal.emit(data['session_id'], a)
                                self.v.putAffect(data['session_id'], a)
                            elif t == 'add_edge':
                                a = None
                                if 'label' in data:
                                    # vmdv.putAffect(AddEdgeAffect(data['session_id'], data['from_id'], data['to_id'], data['label']))
                                    a = affectImpl.AddEdgeAffect(
                                        data['session_id'], data['from_id'], data['to_id'], data['label'])
                                else:
                                    # vmdv.putAffect(AddEdgeAffect(data['session_id'], data['from_id'], data['to_id']))
                                    a = affectImpl.AddEdgeAffect(
                                        data['session_id'], data['from_id'], data['to_id'])
                                self.v.putAffect(data['session_id'],a)
                                # self.affectSignal.emit(data['session_id'], a)
                            elif t == 'feedback':
                                if data['status'] == 'OK':
                                    print('Session received feedback from the prover:',
                                          data['session_id'], ',', data['status'])
                                else:
                                    print('Session received feedback from the prover:',
                                          data['session_id'], ',', data['status'], ',', data['error_msg'])
                        except json.decoder.JSONDecodeError:
                            pass