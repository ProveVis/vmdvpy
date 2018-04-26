import sys
sys.path.append('..')
import session

class Affect:

    def __init__(self):
        pass
    
    @abstractmethod
    def affect(viewer):
        pass