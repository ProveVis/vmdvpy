import sys
sys.path.append('..')
import vmdv
import session
from affects.affectImpl import *
from affects import affect
from PyQt5.QtCore import QThread
from PyQt5 import QtCore
import abc


class Receiver(QThread):
    def __init__(self, v, parent = None):
        super(Receiver, self).__init__(parent)
        self.v = v

    def run(self):
        print('Receiver thread start...')
        while True:
            (sid, a) = self.v.fetchAffect()
            if sid != '':
                self.v.handleAffect(sid, a)
            else:
                print('Affect cannot be sent to a session')

class Message:
    @abc.abstractmethod
    def toJson(self):
        pass
class ClearColorMessage(Message):
    def __init__(self, sid):
        self.sid = sid
    def toJson(self):
        return json.dumps({'type':'clear_color', 'session_id': self.sid})


class Sender(QThread):
    def __init__(self, v, parent = None):
        QThread.__init__(self, parent)
        self.v = v

    def run(self):
        print('Sender thread start...')
        while True:

            