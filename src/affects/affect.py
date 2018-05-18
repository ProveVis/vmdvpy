import sys
import abc

class Affect:
    def __init__(self):
        pass
    @abc.abstractmethod
    def affect(self,viewer):
        pass