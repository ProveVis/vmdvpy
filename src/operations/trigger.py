from PyQt5.QtWidgets import QAction
import abc
import sys
sys.path.append('..')
from affects import affectImpl

class Trigger:
    def __init__(self, sesion, label):
        self.sesion = sesion
        self.label = label

    @abc.abstractmethod
    def action(self):
        pass


class HighlightChildrenTrigger(Trigger):
    
    # will return a list of affect objects
    def action(self):
        return [affectImpl.HighlightChildrenAffect()]

class HighlightAncestorsTrigger(Trigger):
    def action(self):
        return [affectImpl.HighlightAncestorsAffect()]

