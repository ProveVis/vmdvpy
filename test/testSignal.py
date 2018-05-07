from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import threading
import sys


class TestQThread(QThread):
    def __init__(self, parent=None):
        super(TestQThread,self).__init__(parent)

    testSignal = QtCore.pyqtSignal(str, QThread)

    def run(self):
        print('Thread', threading.current_thread().name, 'is emitting a signal')
        self.testSignal.emit("test hello", self)
        print('emit complete')
        # self.terminate()

    def test(self, msg, t):
        print('Thread', threading.current_thread().name, 'is performing')
        print(msg)
    # threading.current_thread().join()
    

if __name__ == '__main__':
    qa = QApplication(sys.argv)
    t = TestQThread()
    t.testSignal.connect(t.test)
    t.start()
    sys.exit(qa.exec_())