terminal_dictionary = {}


class Terminal(object):
    def __init__(self, trm_id, name, comp_parent=None):
        self._name = name
        self._id = trm_id
        self._comp_parent = comp_parent
        terminal_dictionary[self._id] = self

    @property
    def comp_parent(self):
        return self._comp_parent

    @comp_parent.setter
    def comp_parent(self, value):
        self._comp_parent = value

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id
