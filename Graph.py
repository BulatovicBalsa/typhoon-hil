import myvalidator.komponenta as komponenta
import myvalidator.Terminal as Terminal

class Node(object):
    def __init__(self, component):
        self._component = component

    @property
    def component(self):
        return self._component


class Edge(object):
    def __init__(self, origin, destination):
        self._origin = origin
        self._destination = destination

    def opposite(self, v):
        if self._destination == v:
            return self._origin
        elif self._origin == v:
            return self._destination

    @property
    def origin(self):
        return self._origin

    @property
    def destination(self):
        return self._destination


class Graph(object):
    def __init__(self):
        self._outgoing = {}
        self._edges = []

    @property
    def edges(self):
        return self._edges

    @property
    def outgoing(self):
        return self._outgoing

    @edges.setter
    def edges(self, v):
        self._edges = v

    @outgoing.setter
    def outgoing(self, v):
        self._outgoing = v

    def incident_edges(self, v):
        for elem in self.edges:
            if v == elem._origin or v == elem._destination:
                yield elem

    def _validate_vertex(self, v):
        # if not isinstance(v, Node):
        #     raise TypeError('Očekivan je objekat klase Node')
        if v not in self._outgoing:
            raise ValueError('Vertex ne pripada ovom grafu.')

    def _find_node(self, comp):
        for node in self._outgoing:
            if node.component.equals(comp):
                return node
        return None

    def find_node(self, comp):
        if comp.id in self._outgoing:
            return comp
        return None

    def insert_vertex(self, component=None):
        """ Ubacuje i vraća novi čvor (Vertex) sa elementom x"""
        v = Node(component)
        self._outgoing[v.component.id] = {}
        return v

    def insert_edge(self, terminal_v, terminal_u):
        tmp = terminal_v.comp_parent
        v = self.find_node(tmp)
        tmp = terminal_u.comp_parent
        u = self.find_node(tmp)

        self._validate_vertex(v.id)
        self._validate_vertex(u.id)

        terminal_u = terminal_u.id
        terminal_v = terminal_v.id

        u = u.id
        v = v.id

        e = Edge(u, v)
        self.edges.append(e)

        if v in self._outgoing[u]:
            self._outgoing[u][v].append(terminal_u)
        else:
            self._outgoing[u][v] = [terminal_u]
        if u in self._outgoing[v]:
            self._outgoing[v][u].append(terminal_v)
        else:
            self._outgoing[v][u] = [terminal_v]

    def set_labels(self):
        labels = {}
        for elem in self._outgoing:
            labels[elem] = "UNEXPLORED"
        for elem in self.edges:
            labels[elem] = "UNEXPLORED"
        return labels

    def dfs(self, v):
        labels = self.set_labels()
        self._dfs(v, labels)
        return labels

    def _dfs(self, v, labels):
        labels[v] = "VISITED"
        for elem in self.incident_edges(v):
            if labels[elem] == "UNEXPLORED":
                w = elem.opposite(v)
                if labels[w] == "UNEXPLORED":
                    labels[elem] = "DISCOVERY"
                    self._dfs(w, labels)
                else:
                    labels[elem] = "BACK"

    def divide_by_sub_graphs(self):
        labels = self.set_labels()
        new_graphs_list = []
        sub_graphs_parts = []
        for vertex in self._outgoing:
            if vertex in sub_graphs_parts:
                continue
            self._dfs(vertex, labels)
            g = remove_explored(self, labels, sub_graphs_parts)
            new_graphs_list.append(g)
        return new_graphs_list


def remove_explored(graph, labels, sgp_list):
    g = Graph()
    rem_list = []
    for elem in labels:
        if not labels[elem] == "UNEXPLORED":
            if labels[elem] == "VISITED":
                g.outgoing[elem] = graph.outgoing[elem]
            else:
                e = Edge(elem._origin, elem._destination)
                g.edges.append(e)
            sgp_list.append(elem)
            rem_list.append(elem)

    for elem in rem_list:
        labels.pop(elem)
    return g


def get_components_by_dfs_state(graph, v, state):
    labels = graph.dfs(v)
    ret_list = []
    for key in labels.keys():
        if labels[key] == state.upper():
            ret_list.append(key)
    return ret_list


def get_near_constant(graph, cmp_id, container):
    # for key in graph.outgoing[cmp_id].keys():
    #     term_id = graph.outgoing[cmp_id][key][0]
    #     term = Terminal.terminal_dictionary[term_id]
    #     if "out" in term.name:
    #         continue
    #     if "Constant" in komponenta.component_dictionary[key].name:
    #         return komponenta.component_dictionary[key]
    #     return get_near_constant(graph, key, cmp_id)

    for edge in graph.incident_edges(cmp_id):
        w_id = edge.opposite(cmp_id)
        if w_id not in container:
            continue
        if "Constant" in komponenta.component_dictionary[w_id].name:
            return komponenta.component_dictionary[w_id]
        return get_near_constant(graph, w_id, container)

