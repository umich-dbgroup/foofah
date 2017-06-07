def invalid_node(cur_node, goal_node):
    if goal_node.prop_chars & cur_node.prop_chars != goal_node.prop_chars:
        return True
    return False


def count_num_empty_cols(table):
    count = 0

    temp = list(table)
    transpose_table = map(list, zip(*temp))

    for col in transpose_table:
        if "".join(col) == "":
            count += 1

    return count


def add_empty_col(orig_table, new_table):
    if count_num_empty_cols(new_table) > count_num_empty_cols(orig_table):
        return True
    else:
        return False


def contains_empty_col(table, col_id):
    for row in table:
        if "" == row[col_id]:
            return True

    return False


def unlikely_introduce_symbols(cur_node,parent_node,goal_node):
    if not parent_node:
        return False

    if set(cur_node.prop_symbols) - set(goal_node.prop_symbols) > set(parent_node.prop_symbols) - set(goal_node.prop_symbols):
        return True
    return False


def unlikely_unfolds(opname, contents, target):
    if (opname == 'unfold' or opname == 'unfold_header')and len(contents) < len(target):
        return True
    return False


