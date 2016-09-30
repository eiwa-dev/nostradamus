from . import Driver

class DictionaryDriver(Driver):
    def __init__(self):
        self.d = {}

    def getitem(self, k):
        return self.d[k]
    
    def setitem(self, k, v):
        self.d[k] = v
        

