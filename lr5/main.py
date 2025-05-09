from itertools import product

def generate_sdnf_sknf(truth_table, variables):
    sdnf, sknf, sdnf_indices, sknf_indices = [], [], [], []
    for i, row in enumerate(truth_table):
        values, result = row[:-1], row[-1]
        term = [var if val else f"!{var}" for var, val in zip(variables, values)]
        if result:
            sdnf.append(f"({' & '.join(term)})")
            sdnf_indices.append(str(i))
    return " | ".join(sdnf), sdnf_indices
def build_karnaugh_map(variables, truth_values):
    n = len(variables)
    if n == 2:
        return [[truth_values[0], truth_values[1]], [truth_values[2], truth_values[3]]]
    elif n == 3:
        return [[truth_values[0], truth_values[1], truth_values[3], truth_values[2]],
                [truth_values[4], truth_values[5], truth_values[7], truth_values[6]]]
    elif n == 4:
        return [[truth_values[0], truth_values[1], truth_values[3], truth_values[2]],
                [truth_values[4], truth_values[5], truth_values[7], truth_values[6]],
                [truth_values[12], truth_values[13], truth_values[15], truth_values[14]],
                [truth_values[8], truth_values[9], truth_values[11], truth_values[10]]]
    return None


def print_karnaugh_map(kmap, variables):
    n = len(variables)
    print("\nКарта Карно:")
    if n == 2:
        print("   " + variables[1] + "0 " + variables[1] + "1")
        print(variables[0] + "0 " + " ".join(map(str, kmap[0])))
        print(variables[0] + "1 " + " ".join(map(str, kmap[1])))
    elif n == 3:
        print("   " + variables[1] + variables[2] + " 00 01 11 10")
        print(variables[0] + "0    " + " ".join(map(str, kmap[0])))
        print(variables[0] + "1    " + " ".join(map(str, kmap[1])))
    elif n == 4:
        print("   " + variables[2] + variables[3] + " 00 01 11 10")
        print(variables[0] + variables[1] + "00   " + " ".join(map(str, kmap[0])))
        print(variables[0] + variables[1] + "01   " + " ".join(map(str, kmap[1])))
        print(variables[0] + variables[1] + "11   " + " ".join(map(str, kmap[2])))
        print(variables[0] + variables[1] + "10   " + " ".join(map(str, kmap[3])))

def build_var_map(n):
    raw = list(product("01", repeat=n))
    binary_list = ["".join(p) for p in raw]
    if n == 2:
        return [[binary_list[0], binary_list[1]], [binary_list[2], binary_list[3]]]
    elif n == 3:
        return [[binary_list[0], binary_list[1], binary_list[3], binary_list[2]],
                [binary_list[4], binary_list[5], binary_list[7], binary_list[6]]]
    elif n == 4:
        return [[binary_list[0], binary_list[1], binary_list[3], binary_list[2]],
                [binary_list[4], binary_list[5], binary_list[7], binary_list[6]],
                [binary_list[12], binary_list[13], binary_list[15], binary_list[14]],
                [binary_list[8], binary_list[9], binary_list[11], binary_list[10]]]
    else:
        raise ValueError("build_var_map поддерживает 2–4 переменных")


def find_all_groups_2d(kmap, is_sdnf):
    rows = len(kmap)
    cols = len(kmap[0])
    groups = []
    for height in [1, 2, 4]:
        for width in [1, 2, 4]:
            if height > rows or width > cols:
                continue
            for i in range(rows):
                for j in range(cols):
                    valid = True
                    group = set()
                    for di in range(height):
                        for dj in range(width):
                            ni = (i + di) % rows
                            nj = (j + dj) % cols
                            if kmap[ni][nj] != is_sdnf:
                                valid = False
                                break
                            group.add((ni, nj))
                        if not valid:
                            break
                    if valid and group:
                        if not any(group.issubset(existing) for existing in groups):
                            groups.append(group)
    return groups


def group_to_term(group, var_map, variables):
    bits = [var_map[i][j] for i, j in group]
    term = [var if vals.pop() == '1' else f"!{var}" for idx, var in enumerate(variables)
            if len(vals := set(b[idx] for b in bits)) == 1]
    return " & ".join(term)

def minimize_with_karnaugh(truth_table, variables, is_sdnf=True):
    values = [row[-1] for row in truth_table]
    kmap = build_karnaugh_map(variables, values)
    if kmap:
        print_karnaugh_map(kmap, variables)
    n = len(variables)
    var_map = build_var_map(n)
    groups = find_all_groups_2d(kmap, is_sdnf) if kmap else []
    terms_coords = [(i, j) for i in range(len(kmap)) for j in range(len(kmap[0])) if kmap[i][j] == is_sdnf]
    simplified_groups = [group for group in groups if
                         not any(group != other and group.issubset(other) for other in groups)]
    coverage = {term_idx: [group_idx for group_idx, group in enumerate(simplified_groups) if term_coord in group]
                for term_idx, term_coord in enumerate(terms_coords)}
    selected_groups = set()
    remaining_terms = set(coverage.keys())
    essential_groups = {covers[0] for term, covers in coverage.items() if len(covers) == 1}
    selected_groups.update(essential_groups)
    remaining_terms -= {term for term in coverage if any(g in essential_groups for g in coverage[term])}
    while remaining_terms:
        best_group, best_coverage = max(
            ((group_idx, {term for term in remaining_terms if group_idx in coverage[term]})
             for group_idx in set(g for cov in coverage.values() for g in cov) if group_idx not in selected_groups),
            key=lambda x: len(x[1]), default=(None, set())
        )
        if best_group is None:
            break
        selected_groups.add(best_group)
        remaining_terms -= best_coverage
    minimized_terms = [group_to_term(simplified_groups[group_idx], var_map, variables)
                       for group_idx in selected_groups if
                       group_to_term(simplified_groups[group_idx], var_map, variables)]
    if is_sdnf:
        minimized_terms.sort(key=lambda x: '!' in x)
        return " | ".join(f"({t})" for t in minimized_terms if t)

table_t1 = [[0, 0, 0, 0],
 [0, 0, 1, 1],
 [0, 1, 0, 0],
 [0, 1, 1, 1],
 [1, 0, 0, 1],
 [1, 0, 1, 0],
 [1, 1, 0, 1],
 [1, 1, 1, 1]]

