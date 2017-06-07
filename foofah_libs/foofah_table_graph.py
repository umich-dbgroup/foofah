import re
import string
import math
from operator import itemgetter
from itertools import groupby

import itertools
import operator

import foofah_utils

COST_DELETE_EXISTING_CELL = 1
COST_DELETE_CELL = 1
COST_DELETE_EMPTY = 1
COST_ADD_EMPTY = 1
COST_MOVE_EMPTY = 1
COST_MOVE_CELL = 1
COST_SPLIT = 1
COST_MERGE = 1
COST_COPY = 1
COST_MOVE_CELL_HORIZONTAL_1 = 1

cost_data_transform_cpp = False
cost_move_cpp = False
cost_edit_op_cpp = False

debug_print = False

COST_IMPOSSIBLE = 100000


class TableNode:
    def __init__(self, data, row=None, col=None):
        self.data = data
        self.id = id(self)
        self.row = row
        self.col = col

    def __str__(self):
        return "'%s' (%d,%d)" % (self.data, self.row, self.col)


class TableGraph:
    def __init__(self, table):

        self.cells = []
        self.data_set = set()

        for rid, row in enumerate(table):
            for cid, cell in enumerate(row):
                cell_node = TableNode(cell, rid, cid)
                self.cells.append(cell_node)

        self.cell_set = set(self.cells)
        self.cells = tuple(self.cells)

        self.row_num = len(table)
        self.col_num = len(table[0])

    def __str__(self):
        return str(list(self.graph.edges()))

    def nodes(self):
        return self.cells

    def nodes_set(self):
        return self.cell_set

    def graph_edit_distance(self, other):
        return graph_edit_distance(self, other)

    def graph_edit_distance_greedy(self, other, batch=False):
        if batch:
            return clustered_maps(graph_edit_distance_greedy(self, other)[0], self, other)
        return graph_edit_distance_greedy(self, other)

    def batch_graph_edit_distance_greedy(self, other):
        return clustered_maps(graph_edit_distance_greedy(self, other)[0], self, other)

    # Edit distance
    def __sub__(self, other):
        return self.graph_edit_distance(other)

    # Edit distance
    def __rshift__(self, other):
        return self.graph_edit_distance_greedy(other)

# Print a path
def print_map(edge):
    if edge[0] and edge[1]:
        print edge[0].data, "(%d,%d)" % (edge[0].row, edge[0].col), "->", edge[1].data, "(%d,%d)" % (
        edge[1].row, edge[1].col)
    elif edge[0]:
        print edge[0].data, "(%d,%d)" % (edge[0].row, edge[0].col), "->", "empty"

    else:
        print "empty", "->", edge[1].data, "(%d,%d)" % (edge[1].row, edge[1].col)


# Print a path
def print_path(path):
    if path:
        for edge in path:
            if edge[0] and edge[1]:
                print str(edge[0]), "->", str(edge[1]), "%", edge[2]
            elif edge[0]:
                print str(edge[0]), "->", "empty", "%", edge[2]

            else:
                print "empty", "->", str(edge[1]), "%", edge[2]

        print "Actual Cost:", cost_edit_path(path)

    else:
        print "No Transformation Available"


PATTERN_R_2_C = "PATTERN_R_2_C"
PATTERN_R_2_R = "PATTERN_R_2_R"
PATTERN_R_2_T = "PATTERN_R_2_T"

PATTERN_C_2_C = "PATTERN_C_2_C"
PATTERN_C_2_R = "PATTERN_C_2_R"
PATTERN_C_2_T = "PATTERN_C_2_T"

PATTERN_T_2_C = "PATTERN_T_2_C"
PATTERN_T_2_R = "PATTERN_T_2_R"
PATTERN_T_2_T = "PATTERN_T_2_T"


def divide_if_identical_col(path, id=0):
    groups = []

    path.sort(key=lambda x: x[id].col)
    for k, g in groupby(enumerate(path), lambda (i, x): x[id].col):
        groups.append(map(itemgetter(1), g))

    return groups


def divide_if_identical_row(path, id=0):
    groups = []
    path.sort(key=lambda x: x[id].row)
    for k, g in groupby(enumerate(path), lambda (i, x): x[id].row):
        groups.append(map(itemgetter(1), g))

    return groups


def divide_if_discontinuous_col(path, id=0):
    groups = []
    if id == 0:
        path.sort(key=lambda x: x[id].col)
    for k, g in groupby(enumerate(path), lambda (i, x): i - x[id].col):
        groups.append(map(itemgetter(1), g))

    return groups


def divide_if_discontinuous_row(path, c_id=0):
    groups = []
    if c_id == 0:
        path.sort(key=lambda x: x[c_id].row)
    for k, g in groupby(enumerate(path), lambda (i, x): i - x[c_id].row):
        groups.append(map(itemgetter(1), g))

    return groups


def func_1(table_graph):
    if table_graph:
        return table_graph.col
    else:
        return -1


def func_2(table_graph):
    if table_graph:
        return table_graph.row
    else:
        return -1


def cluster_by_columns(path, i=0, continuous=False, identical_row=False):
    cluster_c = {}

    for tran in path:
        if tran[i]:

            if tran[i].col not in cluster_c.keys():
                cluster_c[tran[i].col] = [tran]
            else:
                cluster_c[tran[i].col].append(tran)

    ret_cluster = []

    if continuous:
        for group in cluster_c.values():
            ret_cluster += divide_if_discontinuous_row(group, i)

        return ret_cluster

    elif identical_row:
        for group in cluster_c.values():
            ret_cluster += divide_if_identical_row(group, i)

        return ret_cluster

    else:
        return cluster_c.values()


def cluster_by_rows(path, i=0, continuous=False, identical_row=False):
    cluster_r = {}

    for tran in path:
        if tran[i]:
            if tran[i].row not in cluster_r.keys():
                cluster_r[tran[i].row] = [tran]
            else:
                cluster_r[tran[i].row].append(tran)

    ret_cluster = []

    if continuous:
        for group in cluster_r.values():
            ret_cluster += divide_if_discontinuous_col(group, i)

        return ret_cluster

    elif identical_row:
        for group in cluster_r.values():
            ret_cluster += divide_if_identical_col(group, i)

        return ret_cluster

    else:
        return cluster_r.values()


def cluster_by_types(path):
    path = sorted(path, key=lambda tup: tup[2])

    cluster = []

    for key, group in groupby(path, lambda x: x[2]):
        cluster.append(list(group))

    return cluster


def clustered_maps(path, orig_table, target_table):
    patterns = []

    mv_dict = {}
    for pair in path:
        if pair[0] and pair[1]:
            mv_dict[(pair[0].row, pair[0].col, pair[1].row, pair[1].col)] = pair
        elif pair[0]:
            mv_dict[(pair[0].row, pair[0].col, None, None)] = pair

        elif pair[1]:
            mv_dict[(None, None, pair[1].row, pair[1].col)] = pair

    # Separate by types
    for group in cluster_by_types(path):

        input_output_set = []

        for pair in group:
            if pair[0] and pair[1]:
                input_output_set.append((pair[0].row, pair[0].col, pair[1].row, pair[1].col))
            elif pair[0]:
                input_output_set.append((pair[0].row, pair[0].col, None, None))

            elif pair[1]:
                input_output_set.append((None, None, pair[1].row, pair[1].col))

        if group[0][2] == MAP_TYPE_MV or group[0][2] == MAP_TYPE_MER or group[0][2] == MAP_TYPE_SPL or group[0][
            2] == MAP_TYPE_UNKNOWN:

            # Row major input table

            i_row_o_row = sorted(input_output_set, key=lambda x: (x[0], x[1], x[2], x[3]))
            temp_path = [mv_dict[i_row_o_row[0]]]
            base = i_row_o_row[0]

            i = 1

            while i < len(i_row_o_row):

                # H to H
                if i_row_o_row[i] == (base[0], base[1] + len(temp_path), base[2], base[3] + len(temp_path)):
                    temp_path.append(mv_dict[(base[0], base[1] + len(temp_path), base[2], base[3] + len(temp_path))])

                else:
                    if len(temp_path) > 1:
                        patterns.append(list(temp_path))

                    base = i_row_o_row[i]
                    temp_path = [mv_dict[i_row_o_row[i]]]

                i += 1
            if len(temp_path) > 1:
                patterns.append(list(temp_path))

            if group[0][2] != MAP_TYPE_MER and group[0][2] != MAP_TYPE_SPL:

                temp_path = [mv_dict[i_row_o_row[0]]]
                base = i_row_o_row[0]

                i = 1
                while i < len(i_row_o_row):
                    # One to H
                    if i_row_o_row[i] == (base[0], base[1], base[2], base[3] + len(temp_path)):
                        temp_path.append(mv_dict[(base[0], base[1], base[2], base[3] + len(temp_path))])

                    else:
                        if len(temp_path) > 1:
                            patterns.append(list(temp_path))
                        base = i_row_o_row[i]
                        temp_path = [mv_dict[i_row_o_row[i]]]

                    i += 1
                if len(temp_path) > 1:
                    patterns.append(list(temp_path))

            i_row_o_col = sorted(input_output_set, key=lambda x: (x[0], x[1], x[3], x[2]))

            temp_path = [mv_dict[i_row_o_col[0]]]
            base = i_row_o_col[0]

            i = 1

            while i < len(i_row_o_col):
                # H to V
                if i_row_o_col[i] == (base[0], base[1] + len(temp_path), base[2] + len(temp_path), base[3]):
                    temp_path.append(mv_dict[(base[0], base[1] + len(temp_path), base[2] + len(temp_path), base[3])])

                else:
                    if len(temp_path) > 1:
                        patterns.append(list(temp_path))
                    base = i_row_o_col[i]
                    temp_path = [mv_dict[i_row_o_col[i]]]

                i += 1
            if len(temp_path) > 1:
                patterns.append(list(temp_path))

            # Sort column major of input table
            i_col_o_col = sorted(input_output_set, key=lambda x: (x[1], x[0], x[3], x[2]))
            temp_path = [mv_dict[i_col_o_col[0]]]
            base = i_col_o_col[0]

            i = 1

            while i < len(i_col_o_col):
                # V to V
                if i_col_o_col[i] == (base[0] + len(temp_path), base[1], base[2] + len(temp_path), base[3]):

                    temp_path.append(mv_dict[(base[0] + len(temp_path), base[1], base[2] + len(temp_path), base[3])])


                else:
                    if len(temp_path) > 1:
                        patterns.append(list(temp_path))
                    base = i_col_o_col[i]
                    temp_path = [mv_dict[i_col_o_col[i]]]

                i += 1

            if len(temp_path) > 1:
                patterns.append(list(temp_path))

            # Sort column major of output table

            i_col_o_col = sorted(input_output_set, key=lambda x: (x[3], x[2], x[1], x[0]))
            temp_path = [mv_dict[i_col_o_col[0]]]
            base = i_col_o_col[0]

            i = 1

            while i < len(i_col_o_col):
                # V to V
                if i_col_o_col[i] == (base[0] + len(temp_path), base[1], base[2] + len(temp_path), base[3]):

                    temp_path.append(mv_dict[(base[0] + len(temp_path), base[1], base[2] + len(temp_path), base[3])])


                else:
                    if len(temp_path) > 1:
                        patterns.append(list(temp_path))
                    base = i_col_o_col[i]
                    temp_path = [mv_dict[i_col_o_col[i]]]

                i += 1

            if len(temp_path) > 1:
                patterns.append(list(temp_path))

            if group[0][2] != MAP_TYPE_MER and group[0][2] != MAP_TYPE_SPL:

                temp_path = [mv_dict[i_col_o_col[0]]]
                base = i_col_o_col[0]

                i = 1
                while i < len(i_col_o_col):

                    # One to V
                    if i_col_o_col[i] == (base[0], base[1], base[2] + len(temp_path), base[3]):

                        temp_path.append(mv_dict[(base[0], base[1], base[2] + len(temp_path), base[3])])

                    else:
                        if len(temp_path) > 1:
                            patterns.append(list(temp_path))
                        base = i_col_o_col[i]
                        temp_path = [mv_dict[i_col_o_col[i]]]

                    i += 1

                if len(temp_path) > 1:
                    patterns.append(list(temp_path))

            i_col_o_row = sorted(input_output_set, key=lambda x: (x[1], x[0], x[2], x[3]))

            temp_path = [mv_dict[i_col_o_row[0]]]
            base = i_col_o_row[0]

            i = 1

            while i < len(i_col_o_row):
                # V to H
                if i_col_o_row[i] == (base[0] + len(temp_path), base[1], base[2], base[3] + len(temp_path)):
                    temp_path.append(mv_dict[(base[0] + len(temp_path), base[1], base[2], base[3] + len(temp_path))])

                else:
                    if len(temp_path) > 1:
                        patterns.append(list(temp_path))
                    base = i_col_o_row[i]
                    temp_path = [mv_dict[i_col_o_row[i]]]

                i += 1
            if len(temp_path) > 1:
                patterns.append(list(temp_path))

            i_col_o_row = sorted(input_output_set, key=lambda x: (x[2], x[3], x[1], x[0]))

            temp_path = [mv_dict[i_col_o_row[0]]]
            base = i_col_o_row[0]

            i = 1

            while i < len(i_col_o_row):
                # V to H
                if i_col_o_row[i] == (base[0] + len(temp_path), base[1], base[2], base[3] + len(temp_path)):
                    temp_path.append(mv_dict[(base[0] + len(temp_path), base[1], base[2], base[3] + len(temp_path))])

                else:
                    if len(temp_path) > 1:
                        patterns.append(list(temp_path))
                    base = i_col_o_row[i]
                    temp_path = [mv_dict[i_col_o_row[i]]]

                i += 1
            if len(temp_path) > 1:
                patterns.append(list(temp_path))

        if group[0][2] == MAP_TYPE_RM:

            temp = sorted(input_output_set, key=operator.itemgetter(1))

            # Group Removes by Column
            for key, g in itertools.groupby(temp, operator.itemgetter(1)):

                temp_path = []
                for t in list(g):
                    temp_path.append(mv_dict[t])

                if len(temp_path) > 1:
                    patterns.append(list(temp_path))

    # Determine the final groups
    patterns.sort(key=lambda t: len(t), reverse=True)
    final_group = []

    cost = 0

    overlaps = set()

    for group in patterns:
        if not (set(group) & overlaps):
            overlaps = overlaps.union(set(group))
            final_group.append(group)
            cost += sum([mapping[3] for mapping in group]) / float(len(group))

            if debug_print:
                print "*" * 20
                print_path(group)
                print

    if debug_print and set(path) - overlaps:
        print "*" * 20, "Remains"
        print print_path(set(path) - overlaps)

    cost += sum([mapping[3] for mapping in (set(path) - overlaps)])

    return path, cost


def tokenize(a, first=False):
    if not a:
        return [""]
    if first:
        return re.split('[' + string.punctuation + string.whitespace + ']*', a, 1)
    else:
        return re.split('[' + string.punctuation + string.whitespace + ']*', a)


MAP_TYPE_MV = 1
MAP_TYPE_MER = 2
MAP_TYPE_SPL = 3
MAP_TYPE_UNKNOWN = 4
MAP_TYPE_RM = 5
MAP_TYPE_ADD = 6


# Cost of substitution
def cost_data_transform(str1, str2, use_cpp=cost_data_transform_cpp):
    if use_cpp:
        return foofah_utils.cost_data_transform(str1, str2)

    if str1 == str2:
        return 0, MAP_TYPE_MV
    elif not str1 or not str2:
        return COST_IMPOSSIBLE, MAP_TYPE_UNKNOWN

    elif str1 in str2:
        return COST_MERGE, MAP_TYPE_MER
    elif str2 in str1:
        return COST_SPLIT, MAP_TYPE_SPL

    else:
        token_1 = tokenize(str1)
        token_2 = tokenize(str2)

        not_found_1 = False
        if_all_empty = True
        for token in token_1:
            if token:
                if_all_empty = False
                if token not in str2:
                    not_found_1 = True
                    break

        if if_all_empty:
            not_found_1 = True

        not_found_2 = False
        if_all_empty = True

        for token in token_2:
            if token:
                if_all_empty = False
                if token not in str1:
                    not_found_2 = True
                    break

        if if_all_empty:
            not_found_2 = True

        if not not_found_1 or not not_found_2:
            return COST_MERGE + COST_SPLIT, MAP_TYPE_UNKNOWN
        return COST_IMPOSSIBLE, MAP_TYPE_UNKNOWN


# Cost of substitution
def cost_move(node_1, node_2, use_cpp=cost_move_cpp):
    if use_cpp:
        return foofah_utils.cost_move(node_1.row, node_1.col, node_2.row, node_2.col, node_1.data)

    cost = 0
    # Moving empty space shouldn't count
    if node_1.data:

        if math.fabs(node_1.col - node_2.col) == 1 and node_1.row == node_2.row:
            cost += COST_MOVE_CELL_HORIZONTAL_1

        elif node_1.row != node_2.row or node_1.col != node_2.col:
            cost += COST_MOVE_CELL


    else:
        if node_1.row != node_2.row or node_1.col != node_2.col:
            cost += COST_MOVE_EMPTY

    return cost


# Calculate the cost of path
def cost_edit_op(operation, target=None, use_cpp=cost_edit_op_cpp):
    cost = 0
    if use_cpp:
        if operation[0] and operation[1]:
            return foofah_utils.cost_edit_op(operation[0].row, operation[0].col, operation[0].data, operation[1].row,
                                             operation[1].col, operation[1].data)

        elif operation[0]:
            return foofah_utils.cost_edit_op(operation[0].row, operation[0].col, operation[0].data, -1, -1, "")

        elif operation[1]:
            return foofah_utils.cost_edit_op(-1, -1, "", operation[1].row, operation[1].col, operation[1].data)

        else:

            return foofah_utils.cost_edit_op(-1, -1, "", -1, -1, "")

    if operation[0] and operation[1]:
        new_cost, map_type = cost_data_transform(operation[0].data, operation[1].data)

        cost += new_cost

        if cost >= COST_IMPOSSIBLE:
            return cost, map_type

        cost += cost_move(operation[0], operation[1])

    elif operation[0] and operation[0].data:
        cost += COST_DELETE_CELL

        map_type = MAP_TYPE_RM

    elif operation[0] and not operation[0].data:
        cost += COST_DELETE_EMPTY
        map_type = MAP_TYPE_RM

    elif operation[1] and operation[1].data:
        cost += COST_IMPOSSIBLE
        map_type = MAP_TYPE_ADD

    else:
        cost += COST_ADD_EMPTY
        map_type = MAP_TYPE_ADD

    return cost, map_type


# Calculate the cost of path
def cost_edit_path(edit_path, target=None):
    cost = 0

    for operation in edit_path:
        if operation[0] and operation[1]:
            new_cost, sub_type = cost_data_transform(operation[0].data, operation[1].data)

            cost += new_cost

            if cost >= COST_IMPOSSIBLE:
                return cost

            cost += cost_move(operation[0], operation[1])

        elif operation[0] and operation[0].data:
            cost += COST_DELETE_CELL

        elif operation[0] and not operation[0].data:
            cost += COST_DELETE_EMPTY
        elif operation[1] and operation[1].data:

            cost += COST_IMPOSSIBLE

        else:
            cost += COST_ADD_EMPTY

    return cost


# Check unprocessed nodes in graph u and v
def check_unprocessed(u, v, path):
    processed_u = []
    processed_v = []

    for operation in path:
        if operation[0]:
            processed_u.append(operation[0])

        if operation[1]:
            processed_v.append(operation[1])

    unprocessed_u = u.nodes_set() - set(processed_u)
    unprocessed_v = v.nodes_set() - set(processed_v)

    return list(unprocessed_u), list(unprocessed_v)


# More greedy edit distance graph
def graph_edit_distance_greedy(u, v):
    chosen_path = []
    chosen_path_cost = 0

    # For each node w in u, insert the substitution {w -> v1} into OPEN

    v1 = v.nodes()[0]

    possible_path = []
    possible_path_cost = []

    for w in u.nodes():
        edit_op = (w, v1)

        new_cost, map_type = cost_edit_op(edit_op, v)

        if map_type == MAP_TYPE_MV:
            if_exact_match_found = True

        new_path = (w, v1, map_type, new_cost)

        possible_path.append(new_path)
        possible_path_cost.append(new_cost)

    # Comes out of nowhere
    edit_op = (None, v1)
    new_cost, map_type = cost_edit_op(edit_op, v)
    edit_path = (None, v1, map_type, new_cost)

    possible_path.append(edit_path)
    possible_path_cost.append(new_cost)

    path_idx = possible_path_cost.index(min(possible_path_cost))

    # The cheapest operation is not a move when exact match exists, we keep finding the second cheapest until we find
    #  the move

    chosen_path.append(possible_path[path_idx])
    chosen_path_cost += possible_path_cost[path_idx]

    unprocessed_u = list(u.nodes())
    unprocessed_v = list(v.nodes())


    if possible_path[path_idx][0] in unprocessed_u:
        unprocessed_u.remove(possible_path[path_idx][0])

    unprocessed_v.pop(0)

    while unprocessed_v and unprocessed_u:

        v_next = unprocessed_v.pop(0)

        possible_path = []
        possible_path_cost = []

        if_exact_match_found = False

        for u_next in unprocessed_u:

            edit_op = (u_next, v_next)
            new_cost, map_type = cost_edit_op(edit_op, v)
            if map_type == MAP_TYPE_MV:
                if_exact_match_found = True

            new_path = (u_next, v_next, map_type, new_cost)

            possible_path.append(new_path)
            possible_path_cost.append(new_cost)

            if new_cost <= 0:
                break

        edit_op = (None, v_next)
        new_cost, map_type = cost_edit_op(edit_op, v)

        new_path = (None, v_next, map_type, new_cost)

        possible_path.append(new_path)
        possible_path_cost.append(new_cost)

        path_idx = possible_path_cost.index(min(possible_path_cost))

        # The cheapest operation is not a move when exact match exists, we keep finding the second cheapest until we
        #  find the move
        while if_exact_match_found and possible_path[path_idx][2] != MAP_TYPE_MV:
            if len(possible_path_cost) > 1:
                possible_path_cost.pop(path_idx)
                possible_path.pop(path_idx)
                path_idx = possible_path_cost.index(min(possible_path_cost))
            else:
                break

        # We already don't have a good choice in unprocessed v, let's pick one from the old choice
        if possible_path[path_idx][2] == MAP_TYPE_UNKNOWN or possible_path[path_idx][2] == MAP_TYPE_SPL or \
                        possible_path[path_idx][2] == MAP_TYPE_MER:

            possible_path_new = []
            possible_path_cost_new = []

            for u_next in u.nodes():
                edit_op = (u_next, v_next)
                new_cost, map_type = cost_edit_op(edit_op, v)

                new_path = (u_next, v_next, map_type, new_cost)

                possible_path_new.append(new_path)
                possible_path_cost_new.append(new_cost)

                if new_cost <= 0:
                    break

            path_idx_new = possible_path_cost_new.index(min(possible_path_cost_new))

            if possible_path_cost_new[path_idx_new] < possible_path_cost[path_idx]:
                chosen_path.append(possible_path_new[path_idx_new])
                chosen_path_cost += possible_path_cost_new[path_idx_new]
                if possible_path_new[path_idx_new][0] in unprocessed_u:
                    unprocessed_u.remove(possible_path_new[path_idx_new][0])
            else:
                chosen_path.append(possible_path[path_idx])
                chosen_path_cost += possible_path_cost[path_idx]

                if possible_path[path_idx][0] in unprocessed_u:
                    unprocessed_u.remove(possible_path[path_idx][0])

        else:
            chosen_path.append(possible_path[path_idx])
            chosen_path_cost += possible_path_cost[path_idx]

            if possible_path[path_idx][0] in unprocessed_u:
                unprocessed_u.remove(possible_path[path_idx][0])

    # If unprocessed_u is empty, but unprocessed_v is not, we transform some of the old u nodes
    if not unprocessed_u and unprocessed_v:
        for v_next in unprocessed_v:
            possible_path = []
            possible_path_cost = []
            for u_old in u.nodes():
                edit_op = (u_old, v_next)
                new_cost, map_type = cost_edit_op(edit_op, v)

                new_path = (u_old, v_next, map_type, new_cost)

                possible_path.append(new_path)
                possible_path_cost.append(new_cost)

            edit_op = (None, v_next)
            new_cost, map_type = cost_edit_op(edit_op, v)

            new_path = (None, v_next, map_type, new_cost)

            possible_path.append(new_path)
            possible_path_cost.append(new_cost)

            path_idx = possible_path_cost.index(min(possible_path_cost))

            chosen_path.append(possible_path[path_idx])
            chosen_path_cost += possible_path_cost[path_idx]

    # If unprocessed_v is empty, but unprocessed_u is not, we kick the rest of unprocessed u out
    if unprocessed_u and not unprocessed_v:

        for u_next in unprocessed_u:
            edit_op = (u_next, None)
            new_cost, map_type = cost_edit_op(edit_op, v)

            new_path = (u_next, None, map_type, new_cost)

            chosen_path.append(new_path)
            chosen_path_cost += new_cost

    if debug_print:
        print_path(chosen_path)

    return chosen_path, chosen_path_cost


def graph_edit_distance(u, v):
    # Partial edit path
    open_set = []
    cost_open_set = []

    # For each node w in V2, insert the substitution {u1 -> w} into OPEN

    u1 = u.nodes()[0]

    for w in v.nodes():
        edit_path = set()
        edit_path.add((u1, w))

        new_cost = cost_edit_path(edit_path)

        if new_cost < COST_IMPOSSIBLE:
            open_set.append(edit_path)
            cost_open_set.append(new_cost)

    # Insert the deletion {u1 -> none} into OPEN
    edit_path = set()
    edit_path.add((u1, None))

    new_cost = cost_edit_path(edit_path)

    if new_cost < COST_IMPOSSIBLE:
        open_set.append(edit_path)
        cost_open_set.append(new_cost)

    while cost_open_set:
        # Retrieve minimum-cost partial edit path pmin from OPEN
        path_idx = cost_open_set.index(min(cost_open_set))
        min_path = open_set.pop(path_idx)
        cost = cost_open_set.pop(path_idx)

        # check p_min is a complete edit path
        unprocessed_u, unprocessed_v = check_unprocessed(u, v, min_path)

        if not unprocessed_u and not unprocessed_v:
            # print len(cost_open_set)
            return min_path, cost
        else:
            if unprocessed_u:
                u_next = unprocessed_u.pop()

                for v_next in unprocessed_v:
                    new_path = set(min_path)
                    new_path.add((u_next, v_next))
                    new_cost = cost_edit_path(new_path)

                    if new_cost < COST_IMPOSSIBLE:
                        open_set.append(new_path)
                        cost_open_set.append(new_cost)

                new_path = set(min_path)
                new_path.add((u_next, None))

                new_cost = cost_edit_path(new_path)

                if new_cost < COST_IMPOSSIBLE:
                    open_set.append(new_path)
                    cost_open_set.append(new_cost)

            else:
                # All nodes in u have been processed, but there are nodes in v not been processed
                # They are either copied, splited or merged from u

                for v_next in unprocessed_v:
                    for u_old in u.nodes():
                        new_path = set(min_path)
                        new_path.add((u_old, v_next))

                        new_cost = cost_edit_path(new_path)

                        if new_cost < COST_IMPOSSIBLE:
                            open_set.append(new_path)
                            cost_open_set.append(new_cost)
    return None, None
