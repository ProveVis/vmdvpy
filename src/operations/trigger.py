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
    def __init__(self, sesion):
        Trigger.__init__(self, sesion, 'Highlight Children')
    # will return a list of affect objects
    def action(self):
        return [affectImpl.HighlightChildrenAffect(self.sesion.getSelectedNids())]

class HighlightAncestorsTrigger(Trigger):
    def __init__(self, sesion):
        Trigger.__init__(self, sesion, 'Highlight Ancestors')
    def action(self):
        return [affectImpl.HighlightAncestorsAffect(self.sesion.getSelectedNids())]

class ClearColorTrigger(Trigger):
    def __init__(self, sesion):
        Trigger.__init__(self, sesion, 'Clear Color')
    def action(self):
        return [affectImpl.ClearColorAffect()]

