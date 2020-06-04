from ...engines.light import SpOffset
from ...code_location import CodeLocation
from .atoms import Atom, MemoryLocation, Register
from .dataset import DataSet

class Tag:
    """
    A tag for a Definition that can carry 
    different kind of metadata.
    """

    def __init__(self, name: str='', metadata: object=None):
        self.name = name
        self.metadata = metadata

    def __str__(self):
        return '<Definition Tag {Log:%s, Metadata:%s}>' % (self.log, self.metadata)

class Definition:
    """
    An atom definition.

    :ivar atom:     The atom being defined.
    :ivar codeloc:  Where this definition is created in the original binary code.
    :ivar data:     A concrete value (or many concrete values) that the atom holds when the definition is created.
    :ivar dummy:    Tell whether the definition should be considered dummy or not. During simplification by AILment,
                    definitions marked as dummy will not be removed.
    """

    __slots__ = ('atom', 'codeloc', 'data', 'dummy', 'tag')

    def __init__(self, atom: Atom, codeloc: CodeLocation, data: DataSet, dummy: bool=False, tag: Tag=None):

        self.atom: Atom = atom
        self.codeloc: CodeLocation = codeloc
        self.dummy: bool = dummy
        self.data: DataSet = data
        self.tag = tag

    def __eq__(self, other):
        return self.atom == other.atom and self.codeloc == other.codeloc

    def __repr__(self):
        if not self.tag:
            return '<Definition {Atom:%s, Codeloc:%s, Data:%s%s}>' % (self.atom, self.codeloc, self.data,
                                                                  "" if not self.dummy else " dummy")
        else:
            return '<Definition {Tag:%s, Atom:%s, Codeloc:%s, Data:%s%s}>' % (self.tag.name, self.atom, self.codeloc, self.data,
                                                                  "" if not self.dummy else " dummy")
    def __hash__(self):
        return hash((self.atom, self.codeloc))

    @property
    def offset(self) -> int:
        if isinstance(self.atom, Register):
            return self.atom.reg_offset
        elif isinstance(self.atom, MemoryLocation):
            if isinstance(self.atom.addr, SpOffset):
                return self.atom.addr.offset
            else:
                return self.atom.addr
        else:
            raise ValueError('Unsupported operation offset on %s.' % type(self.atom))

    @property
    def size(self) -> int:
        if isinstance(self.atom, Register):
            return self.atom.size
        elif isinstance(self.atom, MemoryLocation):
            return self.atom.bits // 8
        else:
            raise ValueError('Unsupported operation size on %s.' % type(self.atom))
