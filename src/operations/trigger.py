from PyQt5.QtWidgets import QAction
import abc
import sys
sys.path.append('..')
from affects import affectImpl

class Trigger:
    def __init__(self, viewer, label):
        self.viewer = viewer
        self.label = label
    @abc.abstractmethod
    def action(self):
        pass

class HighlightChildrenTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Highlight Children')
    # will return a list of affect objects
    def action(self):
        return [affectImpl.HighlightChildrenAffect(self.viewer.selected)]

class HighlightAncestorsTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Highlight Ancestors')
    def action(self):
        return [affectImpl.HighlightAncestorsAffect(self.viewer.selected)]

class ClearColorTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Clear Color')
    def action(self):
        return [affectImpl.ClearColorAffect()]

class PrintColorDataTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Print Color Data')
    def action(self):
        return [affectImpl.PrintColorDataAffect()]
