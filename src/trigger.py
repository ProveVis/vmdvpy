from PyQt5.QtWidgets import QAction
import abc
import sys
import affect

class Trigger:
    def __init__(self, viewer, label):
        self.viewer = viewer
        self.label = label
    @abc.abstractmethod
    def action(self):
        pass

class HighlightNodesTrigger(Trigger):
    def __init__(self, gviewer):
        Trigger.__init__(self, gviewer, 'Highlight Selected')
    def action(self):
        selectedNids = [self.viewer.vertices[x].getProperty('id') for x in self.viewer.selectedVids]
        return [affect.HighlightNodeAffect(x) for x in selectedNids]

class HighlightChildrenTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Highlight Children')
    # will return a list of affect objects
    def action(self):
        return [affect.HighlightChildrenAffect(self.viewer.selectedVids)]

class HighlightAncestorsTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Highlight Ancestors')
    def action(self):
        return [affect.HighlightAncestorsAffect(self.viewer.selectedVids)]

class HighlightSubtreeTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Highlight Subtree')
    def action(self):
        return [affect.HighlightSubtreeAffect(self.viewer.selectedVids)]

class ClearColorTrigger(Trigger):
    def __init__(self, viewer, fromVMDV=False):
        Trigger.__init__(self, viewer, 'Clear Color')
        self.fromVMDV = fromVMDV
    def action(self):
        return [affect.ClearColorAffect(self.fromVMDV)]

class PrintColorDataTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Print Color Data')
    def action(self):
        return [affect.PrintColorDataAffect()]
