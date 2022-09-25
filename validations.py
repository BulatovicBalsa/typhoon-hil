import myvalidator.komponenta as komponenta
import myvalidator.Terminal as terminal
import myvalidator.JSON_Parser as JSON_Parser
import myvalidator.Graph as Graph
from typhoon.api.schematic_editor import SchematicAPI as API
import os

TSE_path = ""


def validate_bus_join(model, graph):
    for vertex in graph.outgoing:
        comp = komponenta.get_component_by_id(vertex)
        if not comp.type == "Bus Join":
            continue
        for elem in graph.outgoing[vertex]:
            comp = komponenta.get_component_by_id(elem)
            if comp.type == "Bus Split":
                bus_error(vertex, elem)
                bus_transformation(model, graph, vertex, elem)


def bus_error(id1, id2):
    print("Found un-needed bus pair with following IDs: " + str(id1) + ", " + str(id2))


def bus_transformation(model, graph, id1, id2):
    kmp1 = komponenta.component_dictionary[id1]
    kmp2 = komponenta.component_dictionary[id2]
    node1 = graph.find_node(kmp1)
    node2 = graph.find_node(kmp2)
    new_dict1 = {}
    for elem in graph.outgoing[id1].keys():
        x = terminal.terminal_dictionary[graph.outgoing[id1][elem][0]]
        if "out" in x.name:
            continue
        new_dict1[x.name] = komponenta.component_dictionary[elem]

    new_dict2 = {}
    for elem in graph.outgoing[id2].keys():
        x = terminal.terminal_dictionary[graph.outgoing[id2][elem][0]]
        if "in" in x.name:
            continue
        new_dict2[x.name] = komponenta.component_dictionary[elem]

    print()
    bus_join = model.get_item(kmp1.name, item_type="component")
    bus_split = model.get_item(kmp2.name, item_type="component")
    model.delete_item(bus_split)
    model.delete_item(bus_join)
    komponenta.removed_components.append(id1)
    komponenta.removed_components.append(id2)

    for i in range(len(new_dict1)):
        name1 = "in"
        name2 = "out"
        if not i == 0:
            name1 += str(i)
            name2 += str(i)
        tmp1 = model.get_item(new_dict1[name1].name, item_type="component")
        tmp2 = model.get_item(new_dict2[name2].name, item_type="component")
        term1 = graph.outgoing[new_dict1[name1].id][id1][0]
        term2 = graph.outgoing[new_dict2[name2].id][id2][0]
        term1 = terminal.terminal_dictionary[term1]
        term2 = terminal.terminal_dictionary[term2]
        model.create_connection(model.term(tmp1, term1.name), model.term(tmp2, term2.name))


def validate_calc_value_not_used(model, graph):
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
    calc_value_not_used_transformation(model, eliminated_list)


def val_not_used_error(remove_list):
    print("Found unused sub-graph result. Components with following IDs can be eliminated:")
    print(remove_list)


def calc_value_not_used_transformation(model, remove_list):
    if not remove_list:
        return
    for elem in remove_list:
        cmp = komponenta.component_dictionary[elem]
        item = model.get_item(cmp.name, item_type="component")
        model.delete_item(item)
        komponenta.removed_components.append(elem)


def validate_known_values(model, graph):
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
    known_values_transformation(model, graph, rez_list)


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


def find_next_comp(graph, rez_list):
    found_list = []
    cmp = None
    elem = None
    for elem in rez_list:
        x = komponenta.component_dictionary[elem]
        x = graph.find_node(x)
        for edge in graph.incident_edges(elem):
            cmp = edge.opposite(elem)
            if cmp not in rez_list:
                x = elem
                found_list.append((cmp, elem))

    ret_list = []
    for tup in found_list:
        cmp = tup[0]
        elem = tup[1]
        term = graph.outgoing[cmp][elem][0]
        term = terminal.terminal_dictionary[term]
        cmp = komponenta.component_dictionary[cmp]
        ret_list.append((cmp, term))
    return ret_list


    #term = graph.outgoing[cmp][elem][0]
    #term = terminal.terminal_dictionary[term]
    #cmp = komponenta.component_dictionary[cmp]
    #return cmp, term


def known_values_transformation(model, graph, rez_list):
    rez_list = list(dict.fromkeys(rez_list))
    del_list = []
    if not rez_list:
        return
    for elem in rez_list:
        if elem in komponenta.removed_components:
            continue

        cmp = komponenta.component_dictionary[elem]
        item = model.get_item(cmp.name, item_type="component")
        del_list.append((item, cmp.id))
        # model.delete_item(item)

    lista = find_next_comp(graph, rez_list)

    safe_list = []
    for tup in lista:
        cmp = tup[0]
        term = tup[1]
        if cmp.name == "Bus Join1":
            continue
        near_cmp = Graph.get_near_constant(graph, cmp.id, rez_list)

        item1 = model.get_item(cmp.name, item_type="component")
        item2 = model.get_item(near_cmp.name, item_type="component")
        model.create_connection(model.term(item1, term.name), model.term(item2, near_cmp._terminals[0].name))

        safe_list.append(item2)

    for tup in del_list:
        item = tup[0]
        c_id = tup[1]
        if item not in safe_list:
            model.delete_item(item)
            komponenta.removed_components.append(c_id)


def validate_duplicate_sub_graph(model, graph):
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
        if not group:
            continue
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


def run_validations(model, graph):
    validate_bus_join(model, graph)
    model, graph = reload_graph(model)
    validate_calc_value_not_used(model, graph)
    model, graph = reload_graph(model)
    validate_duplicate_sub_graph(model, graph)
    model, graph = reload_graph(model)
    validate_known_values(model, graph)


def find_path(file_path):
    fp = os.path.normpath(file_path)
    arr1 = fp.split('\\')
    filename = arr1[len(arr1) - 1]
    return file_path.replace(filename, "")


def validate(json_path, tse_path, validator_name):
    global TSE_path
    TSE_path = find_path(tse_path)
    data = JSON_Parser.load_json(json_path)
    graf, komps = JSON_Parser.load_components(data)
    JSON_Parser.load_edges(data, graf)

    # run_validations(graf)
    model = API()
    model.load(tse_path)
    validator = validators[validator_name]
    validator.function(model, graf)
    model.save_as(TSE_path + "proba.tse")
    model.close_model()


def reload_graph(model):
    komponenta.component_dictionary = {}
    terminal.terminal_dictionary = {}
    komponenta.removed_components = []
    print(TSE_path)
    model.save_as(TSE_path + "proba.tse")
    # model.load("E:\\balsa\\typhoon project\myproject\proba.tse")
    model.load(TSE_path + "proba.tse")
    # model.export_model_to_json(".")
    model.export_model_to_json(TSE_path)
    # data = JSON_Parser.load_json("E:\\balsa\\typhoon project\myproject\proba.json")
    data = JSON_Parser.load_json(TSE_path + "proba.json")
    graf, komps = JSON_Parser.load_components(data)
    JSON_Parser.load_edges(data, graf)
    return model, graf


class ValidatorDescription:
    def __init__(self, name, fnc, desc):
        self.name = name
        self.function = fnc
        self.desc = desc


validacije = [
            'default = myvalidator.validations.validate',
            'bus_join = myvalidator.validations:validate_bus_join',
            'known_values = myvalidator.validations:validate_known_values',
            'duplicated_sub_graph = myvalidator.validations:validate_duplicate_sub_graph',
            'value_not_used = myvalidator.validations:validate_calc_value_not_used'
        ]


vd1 = ValidatorDescription('default', run_validations, "run all validations")
vd2 = ValidatorDescription('bus_join', validate_bus_join, "check if two bus joins are directly connected")
vd3 = ValidatorDescription('known_values', validate_known_values, "check if componnents have all known values at "
                                                                     "inputs")
vd4 = ValidatorDescription('duplicated_sub_graph', validate_duplicate_sub_graph, "check if some parts of graphs "
                                                                                    "are similar")
vd5 = ValidatorDescription('value_not_used', validate_calc_value_not_used, "check if graph contains calculations "
                                                                              "that are not used")

validators = {vd1.name: vd1, vd2.name: vd2, vd3.name: vd3, vd4.name: vd4, vd5.name: vd5}


def get_validation_desc(val_name):
    return validators[val_name]





