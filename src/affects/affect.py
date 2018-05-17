import sys
import abc
sys.path.append('..')
import session

class Affect:
    def __init__(self):
        pass
    @abc.abstractmethod
    def affect(self,viewer):
        pass