from enum import Enum

class Kind(Enum):
    NONE = 0
    STATIC = 1
    FIELD = 2
    ARG = 3
    VAR = 4

class SymbolTable():
    def __init__(self):
        self.entries = []

    def startSubroutine(self):
        self.entries = []

    def define(self, name, type, kind):
        self.entries.append(Entry(name, type, kind, self.varCount(kind)))

    def varCount(self, kind):
        count = 0
        for entry in self.entries:
            if entry.kind == kind:
                count += 1
        return count

    def kindOf(self, name):
        for entry in self.entries:
            if entry.name == name:
                return entry.kind
        return Kind.NONE

    def typeOf(self, name):
        for entry in self.entries:
            if entry.name == name:
                return entry.type
        return None

    def indexOf(self, name):
        for entry in self.entries:
            if entry.name == name:
                return entry.index
        return None

    def contains(self, name):
        for entry in self.entries:
            if entry.name == name:
                return True
        return False

class Entry():
    def __init__(self, name, type, kind, index):
        self.name = name
        self.type = type
        self.kind = kind
        self.index = index
