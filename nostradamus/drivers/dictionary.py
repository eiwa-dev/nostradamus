from . import Driver

class DictionaryDriver(Driver):
    def __init__(self, dictionary=None):
        dictionary = dictionary or {}
        self.d = dict(dictionary)

    def getitem(self, k):
        section_name, name = k
        section = self.d.setdefault(section_name, {})
        return section[name]
    
    def setitem(self, k, v):
        section_name, name = k
        section = self.d.setdefault(section_name, {})
        section[name] = v
        

