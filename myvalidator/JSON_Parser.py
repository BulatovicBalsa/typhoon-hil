import json
import myvalidator.komponenta as komponenta
import myvalidator.Terminal as Terminal
import myvalidator.Graph as Graph


def load_json(path):
    # path = "./models/calc_value_not_used.json"
    # path = "./models/eliminate_bus_join.json"
    # path = "./models/known_values.json"
    # path = "./models/dedup.json"
    # path = "./models/overcurrent protection contactor.json"
    with open(path, 'r') as f:
        data = json.load(f)

    return data


def load_components(doc_data):
    komps = []
    graf = Graph.Graph()

    for dev_part in doc_data["dev_partitions"]:
        for parent_component in dev_part["parent_components"]:
            comp_graf = Graph.Graph()
            create_component(graf, komps, parent_component, comp_graf, False)
        for comp in dev_part["components"]:
            if comp["parent_comp_id"] is None:
                create_component(graf, komps, comp, None, False)
            else:
                x = comp["parent_comp_id"]
                parent_component = komponenta.component_dictionary[x]

                # if x not in parent_component.construction.outgoing:
                #     parent_component.construction.insert_vertex(parent_component)

                create_component(graf, komps, comp, parent_component.construction, True)

    return graf, komps


def create_component(graf, comp_list, comp, comp_graph, has_parent):
    c_id = comp['id']
    c_name = comp['name']
    c_parent_id = comp["parent_comp_id"]
    c_type = comp["comp_type"]
    terminals = []
    for terminal in comp["terminals"]:
        t_id = terminal['id']
        t_name = terminal['name']
        t_direction = terminal['direction']
        new_trm = Terminal.Terminal(t_id, t_name, t_direction)
        terminals.append(new_trm)

    new_comp = komponenta.Component(c_id, c_name, terminals, c_parent_id, c_type, comp_graph)
    if not has_parent:
        graf.insert_vertex(new_comp)
    else:
        comp_graph.insert_vertex(new_comp)
    comp_list.append(new_comp)


def load_edges(doc_data, graf):
    for dev_part in doc_data["dev_partitions"]:
        for node in dev_part["nodes"]:
            terminals = node["terminals"]
            targeted_graph = find_graph(terminals[0], graf)
            connect_nodes(targeted_graph, terminals)


def connect_nodes(graf, terminals):
    while len(terminals) > 1:
        for i in range(1, len(terminals)):
            v = Terminal.terminal_dictionary[terminals[0]]
            u = Terminal.terminal_dictionary[terminals[i]]
            graf.insert_edge(v, u)
        terminals.pop(0)


def find_graph(terminal_id, graf):
    v = Terminal.terminal_dictionary[terminal_id]
    komp = v.comp_parent
    if komp.parent is None:
        return graf
    res = komponenta.component_dictionary[komp.parent]._construction
    return res
