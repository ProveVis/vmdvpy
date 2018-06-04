from PyQt5.QtWidgets import QAction
import abc
import sys
import affect
import messenger

class Trigger:
    def __init__(self, viewer, label):
        self.viewer = viewer
        self.label = label
    @abc.abstractmethod
    def action(self):
        pass

class ShowNodeLabelTrigger(Trigger):
    def __init__(self, gviewer):
        Trigger.__init__(self, gviewer, 'Show Node Label')
    def action(self):
        return [affect.ShowNodeLabelAffect(self.viewer.selectedVids)]

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

class ZoneAircraftNumberTrigger(Trigger):
    def __init__(self, viewer, zone):
        Trigger.__init__(self, viewer, 'Highlight By Zone ('+zone+')')
        self.zone = zone

    def action(self):
        rid = self.viewer.vmdv.newRequestId()
        rname = 'zone_aircraft_number'
        rargs = {'zone': self.zone}
        self.viewer.vmdv.putMsg(messenger.RequestMessage(self.viewer.sid, rname, rid, rargs))
        self.viewer.vmdv.addPendingRequest(rid, rname, rargs)
        return []