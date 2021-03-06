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

class SubFormulaTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Highlight Sub-formulae')
        self.viewer = viewer

    def action(self):
        vids = self.viewer.selectedVids
        nids = [self.viewer.vertices[x].getProperty('id') for x in vids]
        for nid in nids:
            rid = self.viewer.vmdv.newRequestId()
            rname = 'sub_formula'
            rargs = {'nid':nid}
            self.viewer.vmdv.putMsg(messenger.RequestMessage(self.viewer.sid, rname, rid, rargs))
            self.viewer.vmdv.addPendingRequest(rid, rname, rargs)
        return []

class ShowRuleTrigger(Trigger):
    def __init__(self, viewer, rule):
        Trigger.__init__(self, viewer, 'Show Rule '+rule)
        self.viewer = viewer
        self.rule = rule

    def action(self):
        rid = self.viewer.vmdv.newRequestId()
        rname = 'show_rule'
        rargs = {'rule':self.rule}
        self.viewer.vmdv.putMsg(messenger.RequestMessage(self.viewer.sid, rname, rid, rargs))
        self.viewer.vmdv.addPendingRequest(rid, rname, rargs)
        return []

class RemoveSubproofTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self,viewer, 'Remove Proof')
        self.viewer = viewer
    def action(self):
        vid = self.viewer.selectedVids[0]
        nid = self.viewer.vertices[vid].getProperty('id')
        self.viewer.vmdv.putMsg(messenger.RemoveSubproofMessage(self.viewer.sid, nid))
        self.viewer.vertices[vid].setProperty("state", "Chosen")
        parent = self.viewer.parent[vid]
        while parent != -1:
            self.viewer.vertices[parent].setProperty("state", "Not_proved")
            if parent not in self.viewer.parent:
                break
            pp = self.viewer.parent[parent]
            if pp == parent:
                parent = -1
            else:
                parent = pp

        return [affect.RemoveSubproofAffect(nid)]

class HideProofTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Hide Proof')
        self.viewer = viewer
    def action(self):
        vid = self.viewer.selectedVids[0]
        nid = self.viewer.vertices[vid].getProperty('id')
        return [affect.HideProofAffect(nid)]

class RestoreProofTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Restore Proof')
        self.viewer = viewer
    def action(self):
        vid = self.viewer.selectedVids[0]
        nid = self.viewer.vertices[vid].getProperty('id')
        return [affect.RestoreProofAffect(nid)]

class ShowHideRulesTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Show/Hide Rules')
        self.viewer = viewer
    def action(self):
        return [affect.HideShowRulesAffect()]

class HighlightCutNodesTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Find Applications of Lemmas')
        self.viewer = viewer
    def action(self):
        return [affect.HighlightCutNodesAffect()]

class ExpandCutTrigger(Trigger):
    def __init__(self, viewer):
        Trigger.__init__(self, viewer, 'Expand Lemma')
    def action(self):
        vid = self.viewer.selectedVids[0]
        nid = self.viewer.vertices[vid].getProperty('id')
        rule = self.viewer.rules[nid]
        split1 = rule.split('.')
        split2 = split1[0].split(' ')
        if len(split2) == 2 and split2[0] == 'apply':
            pvid = self.viewer.parent[vid]
            pnid = self.viewer.vertices[pvid].getProperty('id')
            return [affect.ExpandCutAffect(pnid, split2[1])]
        else:
            return []

