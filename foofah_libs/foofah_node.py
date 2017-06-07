import editdistance
from timeit import default_timer as timer
from operators import add_extract
from prune_rules import invalid_node, unlikely_introduce_symbols
from collections import defaultdict
import Levenshtein
from collections import Counter
import numpy as np
import string
import itertools

from foofah_table_graph import TableGraph

import foofah_utils

MAX_TABLE_OPS = 3
MAX_SYNTAX = 4

CPP = True

NODE_COUNTER = {'nodes': 0}

alphanumeric_set = set(string.ascii_letters) | set(string.digits)

symbol_set = set(string.punctuation) | set(string.whitespace)


def median(lst):
    sorted_list = sorted(lst)
    list_len = len(lst)
    index = (list_len - 1) // 2

    if list_len % 2:
        return sorted_list[index]
    else:
        return (sorted_list[index] + sorted_list[index + 1]) / 2.0


def is_messy_subset(target, contents):
    content_str = chr(0).join(contents)
    return_val = True

    for t in target:
        if t not in content_str:
            return_val = False
            break
    return return_val


def count_matches(target, contents):
    content_str = chr(0).join(contents)
    target_str = chr(0).join(target)
    count = 0
    for c in contents:
        if c == '' or c not in target_str:
            target_in_here = False
            for t in target:
                if t in c:
                    target_in_here = True
                    break
            if not target_in_here:
                count += 1  # this is a drop

    for t in target:
        if t in content_str and t not in contents:
            count += 2  # this is a split + at least one drop

    return count


class FoofahNode:
    pred_model = None

    f_score = 0
    g_score = 0

    f_hash = None

    # Carry-on Properties: can be used directly by other functions, which helps reducing the amount of work when
    # evaluating multiple pruning rules.
    prop_num_rows = 0
    prop_num_cols = 0

    prop_col_char = None

    prop_if_col_contains_empty_cells = None

    def __init__(self, contents, op, parent, times={}, node_counter=NODE_COUNTER, h_debug=False):
        self.node_id = node_counter['nodes']
        self.contents = contents
        self.parent = parent
        self.operation = op
        self.h_debug = h_debug

        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

        self.f_score = 0
        self.g_score = 0

        self.f_hash = hash(str(self.contents))

        self.prop_chars = alphanumeric_set & set(str(self.contents))

        self.prop_symbols = symbol_set & set(str(''.join(y for x in self.contents for y in x)))

        # Set of cell data in current table
        self.prop_data = set(itertools.chain(*self.contents))
        if "" in self.prop_data:
            self.prop_data.remove("")

        self.prop_cols, self.prop_col_data = get_cols_from_table(self.contents)

        self.col_hash = sorted(self.prop_cols)

        self.num_rows = len(self.contents)
        self.num_cols = len(self.contents[0])

        if len(times) == 0:
            times['children'] = []
            times['scores'] = []
            times['ops'] = {}
            times['prune'] = []
            times['prune2'] = []
            times['child_obj'] = []
            times['loop'] = []
        self.times = times

        self.h_score = -1

        node_counter['nodes'] += 1

        if self.parent is not None and self.parent.operation[0]['name'] == 'split1 ]' and op[0]['name'] == 'append ]':
            print self.parent.operation[0]['name'], op[0]['name']

        self.confidence = 1.0

    # @profile
    def make_children(self, ops, debug=False, bound=float("inf"), p1=True, p2=True, p3=True):
        start = timer()
        num_cols = len(self.contents[0])

        children = []

        if self.depth == bound:
            return children

        temp_ops = list(ops)

        ops = temp_ops

        # Checking if all cell data from output table exist in current table.
        # If they are, remove all operators for syntax transformation
        if not table_values_is_subset(FoofahNode.goal_node, self):
            # A brief estimate of whether extract should be added
            ops += add_extract(self.contents, FoofahNode.goal_node.contents, cur_node=self, goal_node=FoofahNode.goal_node)

        # Each operation takes in a column index, so we need to apply
        # each op to every possible column in the current state
        for op in ops:

            # For those table level operations that do not need a column parameter
            if not op['if_col']:
                params = op['params']
                op_obj = (op, None, dict(params))
                result = op['fxn'](self.contents)
                child = self.make_child_node(result, self, op_obj, p1, p2, p3)

                if child:
                    children.append(child)

            else:
                # Try different columns for other operations
                for i in range(num_cols):

                    result = op['fxn'](self.contents, i)
                    params = op['params']
                    params[1] = str(i)
                    op_obj = (op, i, dict(params))
                    child = self.make_child_node(result, self, op_obj, p1, p2, p3)

                    if child:
                        children.append(child)

        self.times['children'].append(timer() - start)

        return children

    def make_child_node(self, table, parent_node, op_obj, p1=True, p2=True, p3=True):
        if table is None or len(table) == 0:
            return None

        child = FoofahNode(table, op_obj, parent_node, parent_node.times)

        if p1 and unlikely_introduce_symbols(child, self, FoofahNode.goal_node) or (p2 and invalid_node(child, FoofahNode.goal_node)) or (p3 and child.identical(parent_node)):
            return None

        return child

    def get_h_score(self, batch=True):
        return self.get_any_dist(self, FoofahNode.goal_node, batch)

    def get_any_dist(self, node_a, node_b, batch=True):
        if CPP:
            a = foofah_utils.TableGraph(node_a.num_rows, node_a.num_cols)
            for i, row in enumerate(node_a.contents):
                for j, cell in enumerate(row):
                    a.addCell(cell, i, j)

            b = foofah_utils.TableGraph(node_b.num_rows, node_b.num_cols)
            for i, row in enumerate(node_b.contents):
                for j, cell in enumerate(row):
                    b.addCell(cell, i, j)

            if batch:
                return foofah_utils.get_ged_batch(a, b, False)
            return foofah_utils.get_ged(a, b)

        a = TableGraph(node_a.contents)
        b = TableGraph(node_b.contents)

        return a.graph_edit_distance_greedy(b, batch)[1]

    def get_h_score_intuitive(self, debug=False):
        # STEP 0
        # There are some scenarios where we know for sure how to solve
        # 
        # Table is exactly the same
        if self == FoofahNode.goal_node:
            self.confidence = float('inf')
            return 0

        syntax = 0
        layout = 0
        clean = 0

        # Usually 1 syntax transformation work on a column
        for col_data in self.prop_col_data:
            for data in col_data:
                if data not in FoofahNode.goal_node.prop_data:
                    syntax += 1
                    continue

        if self.num_rows != FoofahNode.goal_node.num_rows:
            layout += 1

        return syntax + layout + clean

    def get_h_score_rule(self, debug=False, heuristic_no=2):

        if heuristic_no == 1:
            return 1
        elif heuristic_no == 2:
            # If the current table is already the target table, nothing needs to be done
            if self == FoofahNode.goal_node:
                return 0

            # number of rows are the same in the target table, current table and parent table
            if self.num_rows == FoofahNode.goal_node.num_rows:
                # return 1
                h_vals = []
                for i in xrange(self.num_rows):
                    h = self.get_row_h_score(i, debug)
                    h_vals.append(h)

                if len(h_vals) > 1:

                    return median(h_vals)

                else:
                    return h_vals[0]

            else:
                # We are almost sure that it is one of fold, unfold, transpose, fold_header and unfold_header,
                # remove_empty or row concatenation if the table values are the same even though the table shapes
                # are different
                cost = 0
                if self.prop_data != FoofahNode.goal_node.prop_data:
                    cost = 1

                # Tranpose is needed
                if self.num_rows == FoofahNode.goal_node.num_cols and self.num_cols == FoofahNode.goal_node.num_rows:
                    return cost + 1

                # unfold, fold, row concatenation
                elif self.num_rows % FoofahNode.goal_node.num_rows == 0 or self.num_rows % (
                    FoofahNode.goal_node.num_rows - 1) == 0:
                    return cost + 1

                # fold or fold_header or row concate is needed
                elif FoofahNode.goal_node.num_rows % self.num_rows == 0 or FoofahNode.goal_node.num_rows % (
                    self.num_rows - 1) == 0:
                    return cost + 1

                # Could be remove_empty_rows
                elif self.num_cols == FoofahNode.goal_node.num_cols:
                    return cost + 1

                # Otherwise, 2 operations might be used
                else:

                    return cost + 2

        else:
            h_vals = []

            # number of rows are the same in the target table, current table and parent table
            if (self.parent is None or len(self.contents) == len(self.parent.contents)) and len(
                    self.contents) == FoofahNode.goal_node.num_rows:
                # If the current table is already the target table, nothing needs to be done
                if self == FoofahNode.goal_node:
                    return 0

                for i in xrange(len(self.contents)):
                    h = self.get_row_h_score(i, debug)
                    h_vals.append(h)

                if len(h_vals) > 1:
                    h_vals.sort()
                    return np.max(h_vals)  # h_vals[-1] #np.percentile(h_vals, 80)

                else:
                    return h_vals[0]

            else:
                # If the current table is already the target table, nothing needs to be done
                if self == FoofahNode.goal_node:
                    return 0

                # We are almost sure that it is one of fold, unfold, transpose, fold_header and unfold_header, or remove_empty if the table values are the same even though the table shapes are different
                elif table_of_same_values(self, FoofahNode.goal_node):
                    return 1

                # Tranpose is needed
                elif len(self.contents) == FoofahNode.goal_node.num_cols and self.num_cols == FoofahNode.goal_node.num_rows:
                    return 1 + self.get_row_h_score(0)
                # unfold or unfold_header is needed
                elif len(self.contents) % FoofahNode.goal_node.num_rows == 0 or len(self.contents) % (
                    FoofahNode.goal_node.num_rows - 1) == 0:
                    return 1 + self.get_row_h_score(0)

                # fold or fold_header is needed
                elif FoofahNode.goal_node.num_rows % len(self.contents) == 0 or FoofahNode.goal_node.num_rows % (
                    len(self.contents) - 1) == 0:
                    return 1 + self.get_row_h_score(0)

                # We don't know what operations might be used
                else:
                    return 2 + self.get_row_h_score(0)

    def get_row_h_score(self, row_num=0, debug=False, heuristic_no=2):
        H_DEBUG = self.h_debug

        start = timer()

        h_score_source = -1

        if len(self.contents) == 0:
            self.h_score = float("inf")
            h_score_source = 0

            if debug:
                return self.h_score, h_score_source
            else:
                return self.h_score

        row = self.contents[row_num]
        targ_row = FoofahNode.goal_node.contents[row_num]

        if heuristic_no == 2:
            cur_row_count = Counter(row)
            tar_row_count = Counter(targ_row)

            h_score = 0

            if cur_row_count == tar_row_count:

                row_temp = list(row)
                targ_row_temp = list(targ_row)

                p = 0
                while p < len(targ_row_temp) - 1:
                    if row_temp.index(targ_row_temp[p]) < row_temp.index(targ_row_temp[p + 1]):
                        row_temp.remove(targ_row_temp[p])
                        p += 1
                    else:
                        break

                h_score = len(targ_row_temp) - p - 1

            # We are in a more complex situation where more fine grained analysis is needed.
            else:

                # Find intersection of two cell data
                cur_row_temp = list(row)
                tar_row_temp = list(targ_row)

                same_cell_data = set(cur_row_temp) & set(tar_row_temp)

                # Remove null
                if "" in same_cell_data:
                    same_cell_data.remove("")

                # Figure out how many drops or copies are needed. We don't consider if move operations are needed at
                #  this moment. We will posepone considering fill and divide.
                for item in same_cell_data:
                    h_score += abs(cur_row_count[item] - tar_row_count[item])

                # Remove the cells that have already been considered
                cur_row_temp = [x for x in cur_row_temp if x not in same_cell_data]
                tar_row_temp = [x for x in tar_row_temp if x not in same_cell_data]

                # merge and join
                temp_str = chr(1).join(tar_row_temp)
                merge_candidate = []
                for cell_data in cur_row_temp:
                    if cell_data in temp_str:
                        merge_candidate.append(cell_data)

                if "" in merge_candidate: merge_candidate.remove("")

                merge_candidate_2 = set(merge_candidate)
                for a in merge_candidate:
                    for b in merge_candidate:
                        if a != b:
                            if a + b in temp_str:
                                h_score += 1
                                if a in merge_candidate_2: merge_candidate_2.remove(a)
                                if b in merge_candidate_2: merge_candidate_2.remove(b)
                            else:
                                if temp_str.index(a) + len(a) + 1 == temp_str.index(b):
                                    h_score += 1
                                    if a in merge_candidate_2: merge_candidate_2.remove(a)
                                    if b in merge_candidate_2: merge_candidate_2.remove(b)

                cur_row_temp = [x for x in cur_row_temp if x not in merge_candidate_2]
                tar_row_temp = [x for x in tar_row_temp if x not in merge_candidate_2]

                # split
                cur_remove = set()
                tar_remove = set()
                for cur_data in cur_row_temp:
                    if_split = False
                    for tar_data in tar_row_temp:
                        if tar_data in cur_data:
                            if_split = True
                            tar_remove.add(tar_data)

                    tar_row_temp = [x for x in tar_row_temp if x not in tar_remove]

                    if if_split:
                        cur_remove.add(cur_data)
                        h_score += 1

                cur_row_temp = [x for x in cur_row_temp if x not in cur_remove]

                # For fill operation, it delete an empty cell, and add a new cell of random data
                # For divide, it simply add a new empty cell
                # fill & divide

                if cur_row_temp != tar_row_temp:
                    h_score += 1

            self.h_score = h_score
            return h_score

        elif heuristic_no == 1:
            # Simple first try, see how many splits or joins it might take
            if self.h_score:
                self.h_score = 0
                # This is the root node. TODO: this is sort of hacky
                if parent_row is None:
                    self.h_score = float('inf')

                    self.h_score = 1.0

                    h_score_source = 1

                # # Calculate fold and unfold
                # elif len(self.contents) != FooNode.goal_node.num_rows:
                #     self.h_score = 1
                #     target_1d = np.array(self.target)
                #     target_1d = target_1d.ravel()

                #     for item in targ_row:
                #         if item not in target_1d:
                #             self.h_score += 0.5

                # Calculate how many moves needed. This is calculated only when moves are the only operations left to be done.
                elif Counter(row) == Counter(targ_row):
                    row_temp = list(row)
                    targ_row_temp = list(targ_row)

                    p = 0
                    while p < len(targ_row_temp) - 1:
                        if row_temp.index(targ_row_temp[p]) < row_temp.index(targ_row_temp[p + 1]):
                            row_temp.remove(targ_row_temp[p])
                            p += 1
                        else:
                            break

                    self.h_score = (len(targ_row_temp) - p - 1) / 2
                    h_score_source = 2

                # Calculate how many copies and drops are needed. This is calculated only when copies and drops are the only operations to be done.
                elif (set(row) < set(targ_row) or set(targ_row) < set(row)) and Counter(row) != Counter(targ_row):
                    cr = Counter(row)
                    ct = Counter(targ_row)
                    for item in set(row):
                        self.h_score += abs(cr[item] - ct[item]) / 2

                    h_score_source = 3

                # If it's probably a dropped column, use the difference in
                # the number of columns.
                elif (len(row) > len(targ_row) and
                          is_subset(targ_row, row)):
                    self.h_score = abs(len(row) - len(targ_row))
                    h_score_source = 4

                # If we need to do some splits to get the target out...
                elif is_messy_subset(targ_row, row):
                    self.h_score = count_matches(targ_row, row)
                    h_score_source = 5

                else:

                    content_str = chr(1).join(row)
                    target_str = chr(1).join(targ_row)
                    count = 0
                    join_targs = defaultdict(list)
                    in_join_targs = defaultdict(list)
                    drop_cands = []
                    dupes = set([])
                    for c in row:
                        if c == '':
                            count += 1
                        else:
                            for t in targ_row:
                                # if this part of the current state is in the
                                # we may have a join.
                                if c != t and c in t:
                                    num_in_targ = t.count(c)
                                    num_seen = chr(1).join(join_targs[t]).count(c)
                                    # if we have more in the target that we've seen
                                    # yet, add this one. We need to do this in case
                                    # rows have duplicates.
                                    if num_in_targ > num_seen:
                                        join_targs[t].append(c)
                                        in_join_targs[c].append(t)

                            # This is an attempt to handle the case where there
                            # are duplicate columns in the input
                            contents_cnt = content_str.count(c)
                            targ_cnt = target_str.count(c)
                            if targ_cnt > 0 and contents_cnt - targ_cnt > 0:
                                if c not in dupes:
                                    if H_DEBUG: print "Dupe drop:", c, 1
                                    count += 1
                                    dupes.add(c)

                            if c not in target_str and c not in targ_row:
                                drop_cands.append(c)

                    # use this to keep track of what pieces we've already used for
                    # joins, so they don't get double counted later.
                    used_joins = set([])

                    # This counts join ops. If 2 or more items are joins, there
                    # are actually 1 fewer ops than items being joined
                    for k, v in join_targs.iteritems():
                        if len(v) > 1:
                            joined = chr(1).join(v)

                            if H_DEBUG: print "Joins:", k, v, editdistance.eval(joined, k)
                            count += editdistance.eval(joined, k)
                            used_joins.add(k)
                        elif len(in_join_targs[v[0]]) == 1:  # no duplicate matches
                            e_dist = editdistance.eval(k, v[0])
                            count += e_dist  # TODO: this is not right

                            used_joins.add(k)

                            if H_DEBUG: print "Add chars:", k, v, count

                    no_drops = set([])
                    also_no_drops = set([])  # this is for CASE4
                    min_edists = defaultdict(int)
                    for t in targ_row:
                        if t in row:
                            continue

                        for d in drop_cands:
                            e_dist = 0
                            for eo in Levenshtein.editops(t, d):
                                if eo[0] == 'replace':
                                    e_dist += 2
                                else:
                                    e_dist += 1

                            if H_DEBUG: print "START:", t, "|", d, e_dist
                            if d not in no_drops and t in d:
                                if H_DEBUG: print "* CASE1:", t, d, e_dist, 1, count
                                count += 2
                                no_drops.add(d)
                            elif d not in no_drops and d in t and e_dist < len(t) and e_dist >= len(d):
                                if H_DEBUG: print "* CASE2:", t, "|", d, e_dist, 2, count
                                count += 2  # split and drop (or similar)
                                no_drops.add(d)
                            elif d not in no_drops and d in t and e_dist < len(t) and e_dist < len(d):
                                if H_DEBUG: print "* CASE3:", t, d, e_dist, e_dist, count
                                count += e_dist  # char. operations
                                no_drops.add(d)
                            elif e_dist >= len(t) and e_dist < len(d):
                                if H_DEBUG: print "* CASE4:", t, d, e_dist
                                count += 3  # include a split in here

                                also_no_drops.add(d)
                            elif e_dist < len(t) and e_dist < len(d):
                                if H_DEBUG: print "* CASE5:", t, d, e_dist
                                if min_edists[t] == 0 or min_edists[t] > e_dist:
                                    min_edists[t] = e_dist
                                no_drops.add(d)

                    for k, v in min_edists.iteritems():
                        # don't double count ones we've already used in joins
                        if k not in used_joins:
                            count += v

                    no_drops.update(also_no_drops)
                    # drops for all the candidates we didn't just account for
                    drops_count = 0
                    for d in drop_cands:
                        if d not in no_drops and d not in dupes:
                            should_count = True
                            for dupe in dupes:
                                if dupe in d:
                                    should_count = False
                                    break
                            if should_count:
                                drops_count += 1

                    count += drops_count
                    if H_DEBUG:
                        print "drops:", drops_count

                    self.h_score = count

                    h_score_source = 7

            if H_DEBUG:
                print "h_score_source:", h_score_source
            self.times['scores'].append(timer() - start)
            if debug:
                return self.h_score, h_score_source
            else:
                return self.h_score

    def __hash__(self):
        return self.f_hash

    def __eq__(self, other):
        if self.f_hash == other.f_hash:
            return True

        if other.col_hash == self.col_hash:
            return True

        return False

    def identical(self, other):
        if self.f_hash == other.f_hash:
            return True
        return False

    def __ne__(self, other):
        if not other and self:
            return True

        if self.f_hash == other.f_hash:
            return False

        if other.col_hash == self.col_hash:
            return False

        return True

    def __str__(self):

        if 'num_params' in self.operation[0].keys():
            if self.operation[0]['num_params'] == 1:
                return self.operation[0]['name']
            elif self.operation[0]['num_params'] == 2:
                return self.operation[0]['name'] + " on column " + str(self.operation[1])
            else:
                return self.operation[0]['name']
        else:
            return self.operation[0]['name']

    def __cmp__(self, other):
        score = (self.f_score > other.f_score) - (self.f_score < other.f_score)

        if score != 0:
            return score

        return (other.node_id > self.node_id) - (other.node_id < self.node_id)


# class method
def get_cols_from_table(table):
    cols = []

    col_data = []

    new_table = map(list, zip(*table))

    for col in new_table:

        cols.append(tuple(col))
        col_set = set(col)
        if "" in col_set:
            col_set.remove("")

        col_data.append(tuple(col_set))

    return cols, col_data


def table_of_same_values(node_a, node_b):
    a = set(node_a.prop_data)
    a.add("")

    b = set(node_b.prop_data)
    b.add("")

    if a == b:
        return True
    else:
        return False


def table_values_is_subset(node_a, node_b):
    a = set(node_a.prop_data)
    a.add("")

    b = set(node_b.prop_data)
    b.add("")

    if a <= b:
        return True
    else:
        return False
