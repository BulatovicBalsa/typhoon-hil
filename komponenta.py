component_dictionary = {}


class Component(object):
    def __init__(self, cmp_id, name, terminals, parent, type, construction=None):
        self._name = name
        self._id = cmp_id
        self._terminals = terminals
        self._parent = parent
        self._construction = construction
        self._type = type

        self.set_terminal_origin()
        component_dictionary[cmp_id] = self

    def set_terminal_origin(self):
        for term in self._terminals:
            term.comp_parent = self

    def equals(self, other):
        if self._id == other._id:
            return True
        return False

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type


def get_component_by_id(comp_id):
    return component_dictionary[comp_id]


def get_type_by_id(c_id):
    return component_dictionary[c_id].type
