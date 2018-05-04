from PyQt5.QtWidgets import QAction
import abc

class Trigger:
    def __init__(self, label):
        self.label = label

    @abc.abstractmethod
    def action(self):
        pass


class HighlightChildrenTrigger(Trigger):
    
    def action(self):
        

