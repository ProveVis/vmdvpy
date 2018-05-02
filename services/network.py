import sys
sys.path.append('..')
import vmdv
import socket
import json
from PyQt5.QtCore import QThread

class Network(QThread):
    def __init__(self, v, port, parent=None):
        super(Network, self).__init__(parent)
        self.v = v
        self.port = port

# s = None

    def run(self):
        print('Network thread start...')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('',self.port))
            s.listen()
            connection, address = s.accept()
            print('Connection established with a prover: ',address)
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
                            self.v.putJSON(data)
                            # print('Network received json object:', data)
                        except json.decoder.JSONDecodeError:
                            # print('Network received false json object:', recvdStr)
                            pass
                            # print('Json decode error:', recvdStr)
                    
        
                
    # def exit():
    #     s.close()