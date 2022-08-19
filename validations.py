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
                if komponenta.get_type_by_id(comp_id) == "Probe":
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