import sys
import abc
sys.path.append('..')
import session

class Affect:

    def __init__(self, session):
        self.session = session
        pass
    
    @abc.abstractmethod
    def affect(self,v):
        pass