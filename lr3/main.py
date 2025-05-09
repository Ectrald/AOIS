from itertools import product


def implication(p, q):
    return not p or q


def equivalence(p, q):
    return p == q


def generate_truth_values(n):
    return [[bool(int(x)) for x in bin(i)[2:].zfill(n)] for i in range(2 ** n)]


def precedence(op):
    if op == '!': return 3
    if op in ('&', '|'): return 2
    if op in ('->', '~'): return 1
    return 0


def infix_to_postfix(expression):
    output, stack = [], []
    i = 0
    while i < len(expression):
        if expression[i].isalpha():
            output.append(expression[i])
        elif expression[i] in "!&|":
            while stack and precedence(stack[-1]) >= precedence(expression[i]):
                output.append(stack.pop())
            stack.append(expression[i])
        elif expression[i] == '-' and i + 1 < len(expression) and expression[i + 1] == '>':
            while stack and precedence(stack[-1]) >= precedence('->'):
                output.append(stack.pop())
            stack.append("->")
            i += 1
        elif expression[i] == '~':
            while stack and precedence(stack[-1]) >= precedence('~'):
                output.append(stack.pop())
            stack.append("~")
        elif expression[i] == '(':
            stack.append(expression[i])
        elif expression[i] == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        i += 1
    while stack:
        output.append(stack.pop())
    return output


def evaluate_postfix(postfix_tokens, values):
    stack = []
    operators = {"&": lambda a, b: a and b, "|": lambda a, b: a or b,
                 "!": lambda a: not a, "->": implication, "~": equivalence}
    for token in postfix_tokens:
        if token in values:
            stack.append(values[token])
        elif token in operators:
            if token == "!":
                stack.append(operators[token](stack.pop()))
            else:
                b, a = stack.pop(), stack.pop()
                stack.append(operators[token](a, b))
        else:
            raise ValueError(f"Неизвестный токен: {token}")
    return stack.pop()


def generate_sdnf_sknf(truth_table, variables):
    sdnf, sknf, sdnf_indices, sknf_indices = [], [], [], []
    for i, row in enumerate(truth_table):
        values, result = row[:-1], row[-1]
        term = [var if val else f"!{var}" for var, val in zip(variables, values)]
        clause = [f"!{var}" if val else var for var, val in zip(variables, values)]
        if result:
            sdnf.append(f"({' & '.join(term)})")
            sdnf_indices.append(str(i))
        else:
            sknf.append(f"({' | '.join(clause)})")
            sknf_indices.append(str(i))
    return " | ".join(sdnf), " & ".join(sknf), sdnf_indices, sknf_indices


def combine_implicants(implicants, n):
    """
    Объединяет пары импликант, различающиеся ровно в одном разряде.
    Каждая импликанта представлена как кортеж (паттерн, покрытие), где:
      - паттерн – строка длины n с символами '0', '1' или '-'
      - покрытие – множество индексов минтермов, покрываемых данной импликантой.
    """
    new_list = []
    used = [False] * len(implicants)
    for i in range(len(implicants)):
        for j in range(i + 1, len(implicants)):
            p1, cov1 = implicants[i]
            p2, cov2 = implicants[j]
            # Находим позиции, где разные символы
            diffs = [k for k in range(n) if p1[k] != p2[k]]
            if len(diffs) == 1:
                idx = diffs[0]
                new_pattern = p1[:idx] + '-' + p1[idx + 1:]
                new_cov = cov1 | cov2
                candidate = (new_pattern, new_cov)
                if candidate not in new_list:
                    new_list.append(candidate)
                used[i] = True
                used[j] = True
    primes = [implicants[i] for i in range(len(implicants)) if not used[i]]
    return new_list, primes

def generate_prime_implicants(minterm_patterns):
    """
    Из исходного списка минтермов (бинарные строки без дефисов) генерирует все простые импликанты
    с информацией о том, какие минтермы они покрывают.
    """
    n = len(minterm_patterns[0])
    # Исходные импликанты: каждый минтерм превращается в кортеж (паттерн, {индекс})
    implicants = [(p, {i}) for i, p in enumerate(minterm_patterns)]
    all_primes = []
    while True:
        new_implicants, primes = combine_implicants(implicants, n)
        all_primes.extend(primes)
        if not new_implicants:
            break
        implicants = new_implicants
    return all_primes

def literal_count(pattern):
    """Количество заданных (не дефисных) литералов в паттерне."""
    return sum(1 for ch in pattern if ch != '-')

def select_minimal_cover(prime_implicants, total_minterms):
    """
    Перебором выбирает такое подмножество простых импликант, сумма
    которого покрывает все минтермы и имеет минимальную «стоимость» (сумму количества литералов).
    """
    best_cover = None
    best_cost = float('inf')

    def backtrack(selected, covered, start):
        nonlocal best_cover, best_cost
        if covered == total_minterms:
            cost = sum(literal_count(prime_implicants[i][0]) for i in selected)
            if cost < best_cost:
                best_cost = cost
                best_cover = selected.copy()
            return
        for i in range(start, len(prime_implicants)):
            new_covered = covered | prime_implicants[i][1]
            if new_covered != covered:
                selected.append(i)
                backtrack(selected, new_covered, i + 1)
                selected.pop()
    backtrack([], set(), 0)
    if best_cover is None:
        return []
    return [prime_implicants[i] for i in best_cover]

def minimize_sdnf_by_calculation_method(sdnf, variables):
    """
    Для СДНФ: преобразуем каждое слагаемое вида
        (literal_1 & literal_2 & ... & literal_n)
    в строку из '0' и '1' (где '0' соответствует отрицанию, '1' – положительному вхождению),
    генерируем все простые импликанты и затем с помощью перебора выбираем минимальное покрытие.
    Результат возвращается в виде строки минимизированной СДНФ.
    """
    # Преобразуем каждое слагаемое в бинарную строку (минтерм)
    # Предполагаем, что каждое слагаемое содержит все переменные.
    minterm_patterns = [
        ''.join('0' if f"!{var}" in term.strip('()') else '1'
                for var in variables)
        for term in sdnf.split(' | ')
    ]
    if not minterm_patterns or minterm_patterns == ['']:
        return ""
    n = len(variables)
    prime_implicants = generate_prime_implicants(minterm_patterns)
    total = set(range(len(minterm_patterns)))
    selected = select_minimal_cover(prime_implicants, total)

    def pattern_to_term(pattern):
        lits = []
        for i, ch in enumerate(pattern):
            if ch == '1':
                lits.append(variables[i])
            elif ch == '0':
                lits.append(f"!{variables[i]}")
        return " & ".join(lits) if lits else "1"

    minimized_terms = [f"({pattern_to_term(imp[0])})" for imp in selected]
    return " | ".join(minimized_terms)

def minimize_sknf_by_calculation_method(sknf, variables):
    """
    Для СКНФ: каждое слагаемое (макстерм) вида
        (literal_1 | literal_2 | ... | literal_n)
    преобразуем в бинарную строку, где если литерал записан без отрицания, ставим «0», а если с отрицанием – «1».
    Затем проводится аналогичная генерация простых импликант и выбор минимального покрытия.
    """
    minterm_patterns = [
        ''.join('1' if f"!{var}" in term.strip('()') else '0'
                for var in variables)
        for term in sknf.split(' & ')
    ]
    if not minterm_patterns or minterm_patterns == ['']:
        return ""
    n = len(variables)
    prime_implicants = generate_prime_implicants(minterm_patterns)
    total = set(range(len(minterm_patterns)))
    selected = select_minimal_cover(prime_implicants, total)

    def pattern_to_term(pattern):
        lits = []
        for i, ch in enumerate(pattern):
            if ch == '0':
                lits.append(variables[i])
            elif ch == '1':
                lits.append(f"!{variables[i]}")
        return " | ".join(lits) if lits else "0"

    minimized_terms = [f"({pattern_to_term(imp[0])})" for imp in selected]
    return " & ".join(minimized_terms)


def minimize_sdnf_by_calculation_spreadsheet_method(sdnf, variables):
    """
    Минимизация СДНФ методом расчетно-табличного (табличного) метода.
    Для каждого слагаемого (минтерма) вида (literal1 & literal2 & ...)
    формируется бинарная строка: '1' если переменная присутствует, '0' если с отрицанием.
    Затем происходит этап склеивания с печатью каждого этапа, далее строится таблица покрытия,
    и перебором выбирается минимальное покрытие простых импликант.
    """
    # Преобразуем каждое слагаемое в бинарную строку
    minterm_patterns = [
        ''.join('0' if f"!{var}" in term.strip('()') else '1'
                for var in variables)
        for term in sdnf.split(' | ')
    ]
    if not minterm_patterns or minterm_patterns == ['']:
        return ""

    print("\nЭтапы склеивания СДНФ (расчетно-табличный метод):")
    stage = 1
    current = list(minterm_patterns)
    merged_implicants = set()

    # Функция для сравнения, покрывает ли импликанта минтерм
    def covers(prime, minterm):
        return all(p == '-' or p == m for p, m in zip(prime, minterm))

    while True:
        print(f"\nЭтап {stage}:")
        print("Текущие термы:", current)
        new_current = set()
        used = set()
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                term1 = current[i]
                term2 = current[j]
                diffs = [k for k in range(len(term1)) if term1[k] != term2[k]]
                if len(diffs) == 1:
                    idx = diffs[0]
                    merged = term1[:idx] + '-' + term1[idx + 1:]
                    new_current.add(merged)
                    used.add(term1)
                    used.add(term2)
                    print(f"Склеиваем {term1} и {term2} -> {merged}")
        # Те, которые не склеились, являются простыми импликанантами данного этапа.
        stage_primes = set(x for x in current if x not in used)
        merged_implicants.update(stage_primes)
        if not new_current:
            break
        current = list(new_current)
        stage += 1

    # Собираем информацию по покрытию: для каждого простого шаблона определяем, какие минтермы он покрывает
    prime_list = []
    for prime in merged_implicants:
        covered = set(i for i, minterm in enumerate(minterm_patterns) if covers(prime, minterm))
        prime_list.append((prime, covered))

    total = set(range(len(minterm_patterns)))

    # Выводим таблицу покрытия, используя уже существующую функцию
    print_spreadsheet_table(merged_implicants, minterm_patterns, variables)

    # Алгоритм перебором для выбора минимального покрытия.
    def literal_count(pattern):
        return sum(1 for ch in pattern if ch != '-')

    best_cover = None
    best_cost = float('inf')
    prime_list_sorted = prime_list

    def backtrack(selected, covered, start):
        nonlocal best_cover, best_cost
        if covered == total:
            cost = sum(literal_count(prime_list_sorted[i][0]) for i in selected)
            if cost < best_cost:
                best_cost = cost
                best_cover = selected.copy()
            return
        for i in range(start, len(prime_list_sorted)):
            new_covered = covered | prime_list_sorted[i][1]
            if new_covered != covered:
                selected.append(i)
                backtrack(selected, new_covered, i + 1)
                selected.pop()

    backtrack([], set(), 0)
    if best_cover is None:
        selected_primes = []
    else:
        selected_primes = [prime_list_sorted[i][0] for i in best_cover]

    def pattern_to_term(pattern):
        lits = []
        for i, ch in enumerate(pattern):
            if ch == '1':
                lits.append(variables[i])
            elif ch == '0':
                lits.append("!" + variables[i])
        return " & ".join(lits) if lits else "1"

    minimized_terms = [f"({pattern_to_term(p)})" for p in selected_primes]
    return " | ".join(minimized_terms)


def minimize_sknf_by_calculation_spreadsheet_method(sknf, variables):
    """
    Минимизация СКНФ методом расчетно-табличного (табличного) метода.
    Для каждого макстерма вида (literal1 | literal2 | ...)
    мы формируем бинарную строку, где для SKНФ используем: '1' если литерал имеет отрицание,
    '0' если литерал отсутствует с отрицанием.
    Затем проводим этап склеивания, печатаем промежуточные этапы, строим таблицу покрытия и
    перебором выбираем минимальное покрытие.
    """
    # Для СКНФ преобразуем каждое слагаемое в бинарную строку:
    minterm_patterns = [
        ''.join('1' if f"!{var}" in term.strip('()') else '0'
                for var in variables)
        for term in sknf.split(' & ')
    ]
    if not minterm_patterns or minterm_patterns == ['']:
        return ""

    print("\nЭтапы склеивания СКНФ (расчетно-табличный метод):")
    stage = 1
    current = list(minterm_patterns)
    merged_implicants = set()

    # Для SKНФ функция covers аналогична, сравниваем символы (учитывая, что здесь '1' соответствует отрицанию)
    def covers(prime, minterm):
        return all(p == '-' or p == m for p, m in zip(prime, minterm))

    while True:
        print(f"\nЭтап {stage}:")
        print("Текущие термы:", current)
        new_current = set()
        used = set()
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                term1 = current[i]
                term2 = current[j]
                diffs = [k for k in range(len(term1)) if term1[k] != term2[k]]
                if len(diffs) == 1:
                    idx = diffs[0]
                    merged = term1[:idx] + '-' + term1[idx + 1:]
                    new_current.add(merged)
                    used.add(term1)
                    used.add(term2)
                    print(f"Склеиваем {term1} и {term2} -> {merged}")
        stage_primes = set(x for x in current if x not in used)
        merged_implicants.update(stage_primes)
        if not new_current:
            break
        current = list(new_current)
        stage += 1

    prime_list = []
    for prime in merged_implicants:
        covered = set(i for i, minterm in enumerate(minterm_patterns) if covers(prime, minterm))
        prime_list.append((prime, covered))

    total = set(range(len(minterm_patterns)))

    print_spreadsheet_table(merged_implicants, minterm_patterns, variables)

    def literal_count(pattern):
        return sum(1 for ch in pattern if ch != '-')

    best_cover = None
    best_cost = float('inf')
    prime_list_sorted = prime_list

    def backtrack(selected, covered, start):
        nonlocal best_cover, best_cost
        if covered == total:
            cost = sum(literal_count(prime_list_sorted[i][0]) for i in selected)
            if cost < best_cost:
                best_cost = cost
                best_cover = selected.copy()
            return
        for i in range(start, len(prime_list_sorted)):
            new_covered = covered | prime_list_sorted[i][1]
            if new_covered != covered:
                selected.append(i)
                backtrack(selected, new_covered, i + 1)
                selected.pop()

    backtrack([], set(), 0)
    if best_cover is None:
        selected_primes = []
    else:
        selected_primes = [prime_list_sorted[i][0] for i in best_cover]

    def pattern_to_term(pattern):
        # Для СКНФ: если символ равен '0' – переменная (без отрицания), если '1' – отрицание переменной.
        lits = []
        for i, ch in enumerate(pattern):
            if ch == '0':
                lits.append(variables[i])
            elif ch == '1':
                lits.append("!" + variables[i])
        return " | ".join(lits) if lits else "0"

    minimized_terms = [f"({pattern_to_term(p)})" for p in selected_primes]
    return " & ".join(minimized_terms)


def print_spreadsheet_table(implicants, constituents, variables):
    print("\n\nТаблица покрытия расчетно-табличным методом:")
    print(" " * 25, end="")
    for const in constituents:
        const_str = "(" + "".join(f"{'¬' if c == '0' else ''}{var}" for var, c in zip(variables, const)) + ")"
        print(f"{const_str:^15}", end="")
    print("\n" + "-" * (25 + 15 * len(constituents)))
    for i, imp in enumerate(implicants, 1):
        imp_str = ["¬" + var if val == '0' else var for idx, (var, val) in enumerate(zip(variables, imp)) if val != '-']
        row_label = f"{i}. {' & '.join(imp_str)}"
        print(f"{row_label:<25}", end="")
        for const in constituents:
            print(f"{'X':^15}" if covers(imp, const) else f"{'':^15}", end="")
        print()


def covers(implicant, term):
    return all(implicant[i] == '-' or implicant[i] == term[i] for i in range(len(implicant)))


def qm_minimize(truth_table, variables, is_sdnf=True):
    """
    Универсальная функция минимизации методом Квайна-Маккласки для 2-4 переменных
    """
    num_vars = len(variables)
    minterms = []

    # Собираем минтермы (для СДНФ) или макстермы (для СКНФ)
    for idx, row in enumerate(truth_table):
        if (is_sdnf and row[-1]) or (not is_sdnf and not row[-1]):
            minterms.append(idx)

    if not minterms:
        return "0" if is_sdnf else "1"

    # Получаем простые импликанты методом QM
    prime_implicants = qm_prime_implicants(minterms, num_vars)

    # Строим таблицу покрытия
    chart = prime_implicant_chart(prime_implicants, minterms)

    # Выбираем обязательные импликанты
    essential = select_essential_primes(chart)

    # Покрываем оставшиеся минтермы
    additional = choose_cover(chart, prime_implicants, essential)
    final_indices = essential | additional

    # Преобразуем выбранные импликанты в термы
    terms = [implicant_to_term(prime_implicants[idx], variables, is_sdnf)
             for idx in final_indices]

    if is_sdnf:
        minimized = " | ".join(sorted(terms, key=lambda t: t.count("!")))
    else:
        minimized = " & ".join(sorted(terms, key=lambda t: t.count("!")))

    return minimized

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


def build_prime_chart(groups, minterm_coords):
    return {i: {gi for gi, group in enumerate(groups) if minterm in group}
            for i, minterm in enumerate(minterm_coords)}


def select_essential_groups(chart, groups):
    selected, uncovered = set(), set(chart.keys())
    while uncovered:
        best_group, best_coverage = max(
            ((g_idx, {i for i in uncovered if g_idx in chart[i]})
             for g_idx in set(g for s in chart.values() for g in s)),
            key=lambda x: len(x[1]), default=(None, set())
        )
        if not best_group:
            break
        selected.add(best_group)
        uncovered -= best_coverage
    return [groups[i] for i in selected]


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
    else:
        result = ["(" + " | ".join(part[1:] if part.startswith("!") else f"!{part}"
                                   for part in t.split(" & ")) + ")"
                  for t in minimized_terms if t]
        return " & ".join(result)


def initialize_5var_kmap(truth_table, variables):
    gray_code_3bit = [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1), (1, 0, 0)]
    gray_code_2bit = {(0, 0): 0, (0, 1): 1, (1, 1): 2, (1, 0): 3}
    kmap = [[{'vars': [], 'result': None, 'processed': False} for _ in range(4)] for _ in range(8)]
    for row in truth_table:
        a, b, c, d, e = row[:5]
        row_index = gray_code_3bit.index((a, b, c)) if (a, b, c) in gray_code_3bit else None
        if row_index is None:
            continue
        col_index = gray_code_2bit.get((d, e), 0)
        kmap[row_index][col_index]['vars'] = [(variables[i], row[i]) for i in range(5)]
        kmap[row_index][col_index]['result'] = int(row[5])
    return kmap


def print_5var_kmap(truth_table, variables):
    kmap = initialize_5var_kmap(truth_table, variables)
    print("\nКарта Карно для 5 переменных:")
    print("Плоскость " + variables[4] + "=0:")
    print("   " + variables[2] + variables[3] + " 00 01 11 10")
    for i in range(4):
        print(f"{variables[0]}{variables[1]}{format(i, '02b')}   ", end="")
        print(" ".join(str(kmap[i][j]['result']) for j in range(4)))
    print("\nПлоскость " + variables[4] + "=1:")
    print("   " + variables[2] + variables[3] + " 00 01 11 10")
    for i in range(4, 8):
        print(f"{variables[0]}{variables[1]}{format(i - 4, '02b')}   ", end="")
        print(" ".join(str(kmap[i][j]['result']) for j in range(4)))


def qm_prime_implicants(minterms, num_vars):
    """
    Реализует основной этап Квайна–Маккласки.
    Принимает список минтермов (числовое представление) и число переменных.
    Возвращает список простых импликант в виде кортежей (битовая строка, множество минтермов),
    где в битовой строке символ '-' означает «не важно».
    """
    # Начальное представление: каждый минтерм превращается в битовую строку длины num_vars
    terms = [(format(m, f"0{num_vars}b"), {m}) for m in sorted(minterms)]
    prime_implicants = []
    while True:
        used = [False] * len(terms)
        new_terms = []
        # Сравниваем все пары терминов
        for i in range(len(terms)):
            for j in range(i + 1, len(terms)):
                bits1, mts1 = terms[i]
                bits2, mts2 = terms[j]
                diff_count = 0
                new_bits = []
                for b1, b2 in zip(bits1, bits2):
                    if b1 != b2:
                        # Если оба бита явно заданы и различны
                        if b1 != '-' and b2 != '-':
                            diff_count += 1
                            new_bits.append('-')
                        else:
                            diff_count = 999
                            break
                    else:
                        new_bits.append(b1)
                if diff_count == 1:
                    used[i] = True
                    used[j] = True
                    candidate = ("".join(new_bits), mts1 | mts2)
                    if candidate not in new_terms:
                        new_terms.append(candidate)
        # Все термы, которые не были объединены, являются простыми импликанантами
        for idx, flag in enumerate(used):
            if not flag and terms[idx] not in prime_implicants:
                prime_implicants.append(terms[idx])
        if not new_terms:
            break
        terms = new_terms
    return prime_implicants


def prime_implicant_chart(prime_implicants, minterms):
    """
    Строит таблицу покрытия: для каждого минтерма возвращает список индексов
    простых импликант, которые его покрывают.
    """
    chart = {}
    for m in minterms:
        chart[m] = []
        for idx, (bits, mt_set) in enumerate(prime_implicants):
            if m in mt_set:
                chart[m].append(idx)
    return chart


def select_essential_primes(chart):
    """
    Выделение обязательных простых импликант:
    если какой-либо минтерм покрывается только одной импликантой, она обязательна.
    """
    essential = set()
    for m, indices in chart.items():
        if len(indices) == 1:
            essential.add(indices[0])
    return essential


def choose_cover(chart, prime_implicants, essential):
    """
    Для оставшихся (не покрытых обязательными) минтермов с помощью перебора
    выбирается такое минимальное покрытие, чтобы суммарное число литералов было минимальным.
    """
    covered = set()
    for e in essential:
        covered |= prime_implicants[e][1]
    remaining = set(chart.keys()) - covered
    non_essential = set(range(len(prime_implicants))) - essential
    best = None
    best_cost = float('inf')
    non_essential_list = list(non_essential)
    n = len(non_essential_list)
    from itertools import combinations
    for r in range(1, n + 1):
        for combo in combinations(non_essential_list, r):
            cover = set()
            for idx in combo:
                cover |= prime_implicants[idx][1]
            if remaining.issubset(cover):
                # Вычисляем «стоимость» набора как сумму количества установленных битов (не '-')
                cost = sum(sum(1 for ch in prime_implicants[idx][0] if ch != '-') for idx in combo)
                if cost < best_cost:
                    best_cost = cost
                    best = set(combo)
        if best is not None:
            break
    return best if best is not None else set()


def implicant_to_term(implicant, variables, is_sdnf=True):
    """
    Преобразует импликанту (битовая строка) в строковое представление терма.
    Для СДНФ: если символ равен '1' – переменная, если '0' – отрицание переменной.
    Для СКНФ: при '0' – переменная, при '1' – отрицание переменной.
    Символ '-' пропускается.
    """
    bits = implicant[0]
    if is_sdnf:
        literals = []
        for i, ch in enumerate(bits):
            if ch == '1':
                literals.append(variables[i])
            elif ch == '0':
                literals.append(f"!{variables[i]}")
        if literals:
            return "(" + " & ".join(literals) + ")"
        else:
            return "1"
    else:
        literals = []
        for i, ch in enumerate(bits):
            if ch == '0':
                literals.append(variables[i])
            elif ch == '1':
                literals.append(f"!{variables[i]}")
        if literals:
            return "(" + " | ".join(literals) + ")"
        else:
            return "0"


def minimize_5var_karnaugh(truth_table, variables, is_sdnf=True):
    """
    Минимизация логической функции с 5 переменными по алгоритму Квайна–Маккласки.
    Для is_sdnf=True используются минтермы (значение 1) и получается минимизированная СДНФ,
    для is_sdnf=False – используются макстермы (значение 0) и получается минимизированная СКНФ.

    Функция:
      1. Из truth_table собирает индексы строк, где результат равен целевому значению.
      2. Вычисляет простейшие импликанты по методу Квайна–Маккласки.
      3. Строит таблицу покрытия и выделяет обязательные импликанты.
      4. Для непокрытых минтермов перебором выбирается дополнительное покрытие.
      5. Преобразует выбранные импликанты в строковое представление итоговой минимизированной формулы.
    """
    num_vars = 5
    minterms = []
    for idx, row in enumerate(truth_table):
        if is_sdnf:
            if row[-1] == 1:
                minterms.append(idx)
        else:
            if row[-1] == 0:
                minterms.append(idx)
    if not minterms:
        return "0" if is_sdnf else "1"

    prime_implicants = qm_prime_implicants(minterms, num_vars)
    chart = prime_implicant_chart(prime_implicants, minterms)
    essential = select_essential_primes(chart)
    additional = choose_cover(chart, prime_implicants, essential)
    final_indices = essential | additional

    terms = [implicant_to_term(prime_implicants[idx], variables, is_sdnf) for idx in final_indices]
    if is_sdnf:
        minimized = " | ".join(sorted(terms, key=lambda t: t.count("!")))
    else:
        minimized = " & ".join(sorted(terms, key=lambda t: t.count("!")))
    return minimized


def truth_table(expression, variables):
    postfix_tokens = infix_to_postfix(expression)
    table = []
    print(" | ".join(variables) + " | Result")
    print("-" * (len(variables) * 4 + 10))
    for values in generate_truth_values(len(variables)):
        values_dict = dict(zip(variables, values))
        result = evaluate_postfix(postfix_tokens, values_dict)
        row = [int(values_dict[var]) for var in variables] + [int(result)]
        table.append(row)
        print(" | ".join(map(str, row)))
    sdnf, sknf, sdnf_indices, sknf_indices = generate_sdnf_sknf(table, variables)
    index_bits = [str(row[-1]) for row in table]
    index_binary = ''.join(index_bits)
    index_decimal = int(index_binary, 2)
    index_form = f"{index_decimal} - {index_binary}"
    print("\nСДНФ:", sdnf)
    print("Числовая форма СДНФ:", ", ".join(sdnf_indices))
    print("СКНФ:", sknf)
    print("Числовая форма СКНФ:", ", ".join(sknf_indices))
    print("Индексная форма функции:", index_form)
    minimized_sdnf = minimize_sdnf_by_calculation_method(sdnf, variables)
    minimized_sknf = minimize_sknf_by_calculation_method(sknf, variables)
    print("\nМинимизированная СДНФ (расчетный метод):", minimized_sdnf)
    print("Минимизированная СКНФ (расчетный метод):", minimized_sknf)
    minimized_sdnf_spreadsheet = minimize_sdnf_by_calculation_spreadsheet_method(sdnf, variables)
    minimized_sknf_spreadsheet = minimize_sknf_by_calculation_spreadsheet_method(sknf, variables)
    print("\nМинимизированная СДНФ (расчетно-табличный метод):", minimized_sdnf_spreadsheet)
    print("Минимизированная СКНФ (расчетно-табличный метод):", minimized_sknf_spreadsheet)
    if len(variables) <= 4:
        print("\n" + "=" * 50 + " Табличный метод " + "=" * 50)
        minimized_sdnf_karnaugh = minimize_with_karnaugh(table, variables, True)
        print("\nМинимизированная СДНФ (табличный метод):", minimized_sdnf_karnaugh)
        minimized_sknf_karnaugh = minimize_with_karnaugh(table, variables, False)
        print("\nМинимизированная СКНФ (табличный метод):", minimized_sknf_karnaugh)
    elif len(variables) == 5:
        print("\n" + "=" * 50 + " Табличный метод для 5 переменных " + "=" * 50)
        print_5var_kmap(table, variables)
        minimized_sdnf_karnaugh = minimize_5var_karnaugh(table, variables, True)
        print("\nМинимизированная СДНФ (табличный метод для 5 переменных):", minimized_sdnf_karnaugh)
        minimized_sknf_karnaugh = minimize_5var_karnaugh(table, variables, False)
        print("\nМинимизированная СКНФ (табличный метод для 5 переменных):", minimized_sknf_karnaugh)
    return index_form


if __name__ == "__main__":
    expression = input("Введите логическое выражение (a, b, c, d, e, &, |, !, ->, ~): ")
    variables = sorted(set(filter(str.isalpha, expression)))
    truth_table(expression, variables)

# (((a->b)~(c->d))->e)
# (((a->b)->(c->d))->e)
# (a~b)->(c&d)|(c&a)~b