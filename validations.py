import Graph
import komponenta


def validate_bus_join(graph):
    for vertex in graph.outgoing:
        comp = komponenta.get_component_by_id(vertex)
        if not comp.type == "Bus Join":
            continue
        for elem in graph.outgoing[vertex]:
            comp = komponenta.get_component_by_id(elem)
            if comp.type == "Bus Split":
                bus_error(vertex, elem)


def bus_error(id1, id2):
    print("Found un-needed bus pair with following IDs: " + str(id1) + ", " + str(id2))


def validate_calc_value_not_used(graph):
    eliminated_list = []
    valid = False
    for vertex in graph.outgoing:
        elem = komponenta.get_component_by_id(vertex)
        if vertex in eliminated_list:
            continue
        if elem.type == "Constant" or "Input" in elem.type:
            visited_list = Graph.get_components_by_dfs_state(graph, vertex, "VISITED")
            for comp_id in visited_list:
                if "Probe" in komponenta.get_type_by_id(comp_id):
                    valid = True
                    break
            if valid:
                valid = False
            else:
                val_not_used_error(visited_list)
                eliminated_list.extend(visited_list)


def val_not_used_error(remove_list):
    print("Found unused sub-graph result. Components with following IDs can be eliminated:")
    print(remove_list)


def validate_known_values(graph):
    rez_list = []
    input_list = []
    constants_list = komponenta.get_components_by_type("Constant")
    for constant in constants_list:  # id_constant
        input_list.append(constant)
        e = None
        for tmp in graph.incident_edges(constant):
            e = tmp
        w = e.opposite(constant)
        w = komponenta.component_dictionary[w]
        if "Probe" in w.type:
            input_list.remove(constant)
            continue
        find_known_values(graph, w, input_list)
        rez_list.extend(input_list)
        input_list.clear()
    rez_list = list(dict.fromkeys(rez_list))
    known_values_error(rez_list)


def find_known_values(graph, comp, input_list):
    input_list.append(comp.id)
    for trm_id in comp.get_input_terminals():
        next_comp_id = None
        for key in graph.outgoing[comp.id]:
            if trm_id in graph.outgoing[comp.id][key]:
                next_comp_id = key
                break
        if next_comp_id in input_list:
            continue
        next_comp = komponenta.get_component_by_id(next_comp_id)
        if "Input" in next_comp.type:
            input_list.clear()
            return
        input_list.append(next_comp_id)
        if not next_comp.type == "Constant":
            find_known_values(graph, next_comp, input_list)


def known_values_error(rez_list):
    if not rez_list:
        return
    print("Found known calculations, components with following IDs should be replaced:")
    s = str(rez_list).replace("[", "").replace("]", "")
    print(s)


def validate_duplicate_sub_graph(graph):
    all_same_groups = []
    group = []
    sub_graph_list = graph.divide_by_sub_graphs()
    while len(sub_graph_list) > 1:
        a_graph = sub_graph_list[0]
        for i in range(1, len(sub_graph_list)):
            b_graph = sub_graph_list[i]
            same = compare_graphs(a_graph, b_graph)
            if same:
                group.append(a_graph)
                group.append(b_graph)
        sub_graph_list.pop(0)
        group = set(group)
        all_same_groups.append(group)
        group = []
    duplicate_sub_graph_error(all_same_groups)


def compare_graphs(a_graph, b_graph):
    if not len(a_graph.edges) == len(b_graph.edges):
        return False
    if not len(a_graph.outgoing) == len(b_graph.outgoing):
        return False
    a_graph_dict = {}
    b_graph_dict = {}
    for cmp_id in a_graph.outgoing:
        if cmp_id in a_graph_dict:
            continue
        cmp_type = komponenta.get_type_by_id(cmp_id)
        a_graph_dict[cmp_type] = []
        b_graph_dict[cmp_type] = []
        for cmp2_id in a_graph.outgoing:
            if komponenta.get_type_by_id(cmp2_id) == cmp_type:
                a_graph_dict[cmp_type].append(cmp2_id)
        for cmp2_id in b_graph.outgoing:
            if komponenta.get_type_by_id(cmp2_id) == cmp_type:
                b_graph_dict[cmp_type].append(cmp2_id)

        if not len(a_graph_dict[cmp_type]) == len(b_graph_dict[cmp_type]):
            return False

    for e in a_graph.edges:
        c1_type = komponenta.get_type_by_id(e.origin)
        c2_type = komponenta.get_type_by_id(e.destination)
        valid = funkcija(b_graph, c1_type, c2_type)
        if not valid:
            return False
    return True


def funkcija(graph, type1, type2):
    exist = False
    e = None
    for e in graph.edges:
        c1_type = komponenta.get_type_by_id(e.origin)
        c2_type = komponenta.get_type_by_id(e.destination)
        if c1_type == type1 and c2_type == type2:
            exist = True
            break
        elif c1_type == type2 and c2_type == type1:
            exist = True
            break
    if exist:
        graph.edges.remove(e)
        return True
    return False


def duplicate_sub_graph_error(all_groups):
    if not all_groups:
        return
    print("Duplicate sub-graphs found. Following components should be replaced:")
    for lista in all_groups:
        ss = ""
        for elem in lista:
            s1 = str(list(elem.outgoing.keys()))
            ss += s1 + " ; "
        ss = ss[:-3]
        print(ss)
