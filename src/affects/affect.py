import sys
import abc
sys.path.append('..')
import session

class Affect:

    def __init__(self):
        # self.session = session
        pass
    
    @abc.abstractmethod
    def affect(self,s):
        pass