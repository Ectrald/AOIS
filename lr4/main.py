def generate_truth_values(n):
    return [[bool(int(x)) for x in bin(i)[2:].zfill(n)] for i in range(2 ** n)]


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
    new_list = []
    used = [False] * len(implicants)
    for i in range(len(implicants)):
        for j in range(i + 1, len(implicants)):
            p1, cov1 = implicants[i]
            p2, cov2 = implicants[j]
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
    n = len(minterm_patterns[0])
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
    return sum(1 for ch in pattern if ch != '-')


def select_minimal_cover(prime_implicants, total_minterms):
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


def minimize_sdnf(sdnf, variables):
    minterm_patterns = [
        ''.join('0' if f"!{var}" in term.strip('()') else '1'
                for var in variables)
        for term in sdnf.split(' | ')
    ]
    if not minterm_patterns or minterm_patterns == ['']:
        return ""

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


def build_karnaugh_map(variables, truth_values):
    n = len(variables)
    if n == 2:
        return [[truth_values[0], truth_values[1]],
                [truth_values[2], truth_values[3]]]
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


class ThreeBitAdder:
    def __init__(self):
        # Логика для выхода S (сумма)
        self.s_logic = lambda a, b, cin: a ^ b ^ cin

        # Логика для выхода Cout (перенос)
        self.cout_logic = lambda a, b, cin: (a & b) | (a & cin) | (b & cin)

    def add(self, a, b, cin=0):
        """Выполняет сложение 3 битов (a, b, cin) и возвращает (sum, carry)"""
        s = self.s_logic(a, b, cin)
        cout = self.cout_logic(a, b, cin)
        return s, cout

    def add_numbers(self, num1, num2):
        """Складывает два 4-битных числа и возвращает 5-битный результат (бит переноса + 4 бита суммы)"""
        if num1 < 0 or num1 > 15 or num2 < 0 or num2 > 15:
            raise ValueError("Числа должны быть в диапазоне 0-15")

        # Преобразуем числа в бинарный формат (4 бита)
        bin1 = [int(x) for x in f"{num1:04b}"]
        bin2 = [int(x) for x in f"{num2:04b}"]

        result = []
        carry = 0

        # Выполняем сложение от младшего бита к старшему
        for i in range(3, -1, -1):
            s, carry = self.add(bin1[i], bin2[i], carry)
            result.insert(0, s)

        # Добавляем бит переноса, если он есть
        result.insert(0, carry)

        return result


class D8421Converter:
    def __init__(self):
        # Логика преобразования для каждого бита (Y3, Y2, Y1, Y0)
        self.logic = [
            lambda d8, d4, d2, d1: d8 ^ (d4 & d2 & d1),  # Y3
            lambda d8, d4, d2, d1: d4 ^ (d2 & d1),  # Y2
            lambda d8, d4, d2, d1: d2 ^ d1,  # Y1
            lambda d8, d4, d2, d1: not d1  # Y0
        ]

    def convert(self, decimal):
        """Преобразует десятичное число (0-9) в D8421+1"""
        if decimal < 0 or decimal > 9:
            raise ValueError("Число должно быть в диапазоне 0-9")

        # Преобразуем число в D8421 (4 бита)
        d8421 = [int(x) for x in f"{decimal:04b}"]
        d8, d4, d2, d1 = d8421

        # Применяем логику преобразования для каждого бита
        result = [
            int(self.logic[0](d8, d4, d2, d1)),
            int(self.logic[1](d8, d4, d2, d1)),
            int(self.logic[2](d8, d4, d2, d1)),
            int(self.logic[3](d8, d4, d2, d1))
        ]

        # Преобразуем результат обратно в десятичное число
        result_decimal = result[0] * 8 + result[1] * 4 + result[2] * 2 + result[3] * 1

        return {
            'input': {
                'decimal': decimal,
                'binary': d8421
            },
            'output': {
                'binary': result,
                'decimal': result_decimal if result_decimal < 10 else None
            }
        }


def part1_3bit_adder():
    print("\n" + "=" * 50 + " Часть 1: Одноразрядный двоичный сумматор на 3 входа (ОДС-3) " + "=" * 50)

    # Определяем таблицу истинности для одноразрядного сумматора (A, B, Cin -> S, Cout)
    truth_table = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 0, 1],
        [1, 0, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [1, 1, 0, 0, 1],
        [1, 1, 1, 1, 1]
    ]

    variables = ['A', 'B', 'Cin']

    # Для выхода S (сумма)
    s_values = [row[3] for row in truth_table]
    s_table = [[row[0], row[1], row[2], row[3]] for row in truth_table]

    # Для выхода Cout (перенос)
    cout_values = [row[4] for row in truth_table]
    cout_table = [[row[0], row[1], row[2], row[4]] for row in truth_table]

    print("\nТаблица истинности для одноразрядного сумматора:")
    print("A | B | Cin | S | Cout")
    print("-" * 23)
    for row in truth_table:
        print(f"{row[0]} | {row[1]} | {row[2]}  | {row[3]} | {row[4]}")

    # Анализ для выхода S
    print("\n" + "-" * 30 + " Анализ для выхода S (сумма) " + "-" * 30)
    s_sdnf, s_sknf, s_sdnf_indices, s_sknf_indices = generate_sdnf_sknf(s_table, variables)
    print("\nСДНФ для S:", s_sdnf)
    print("Числовая форма СДНФ для S:", ", ".join(s_sdnf_indices))
    minimized_s_sdnf = minimize_sdnf(s_sdnf, variables)
    print("Минимизированная СДНФ для S:", minimized_s_sdnf)

    # Карта Карно для S
    s_kmap = build_karnaugh_map(variables, s_values)
    print_karnaugh_map(s_kmap, variables)

    # Анализ для выхода Cout
    print("\n" + "-" * 30 + " Анализ для выхода Cout (перенос) " + "-" * 30)
    cout_sdnf, cout_sknf, cout_sdnf_indices, cout_sknf_indices = generate_sdnf_sknf(cout_table, variables)
    print("\nСДНФ для Cout:", cout_sdnf)
    print("Числовая форма СДНФ для Cout:", ", ".join(cout_sdnf_indices))
    minimized_cout_sdnf = minimize_sdnf(cout_sdnf, variables)
    print("Минимизированная СДНФ для Cout:", minimized_cout_sdnf)

    # Карта Карно для Cout
    cout_kmap = build_karnaugh_map(variables, cout_values)
    print_karnaugh_map(cout_kmap, variables)

    # Демонстрация работы сумматора на числах 6 и 8
    print("\n" + "=" * 30 + " Демонстрация работы сумматора " + "=" * 30)
    adder = ThreeBitAdder()

    num1 = 6
    num2 = 8

    print(f"\nСложение чисел {num1} и {num2}:")
    print(f"{num1} в двоичном: {[int(x) for x in f'{num1:04b}']}")
    print(f"{num2} в двоичном: {[int(x) for x in f'{num2:04b}']}")

    result = adder.add_numbers(num1, num2)
    print("\nРезультат сложения:")
    print(f"Бит переноса: {result[0]}")
    print(f"Сумма: {result[1:]}")
    print(f"Десятичное представление: {result[0] * 16 + result[1] * 8 + result[2] * 4 + result[3] * 2 + result[4] * 1}")


def part2_D8421_to_D8421_plus_1():
    print("\n" + "=" * 50 + " Часть 2: Преобразователь кода Д8421 в код Д8421+1 " + "=" * 50)

    # Таблица истинности для преобразователя Д8421 в Д8421+1
    # Входы: D8, D4, D2, D1 (D8 - старший бит)
    # Выходы: Y3, Y2, Y1, Y0 (Y3 - старший бит)
    # Неопределенные состояния (для чисел 10-15) обозначены как None

    truth_table = [
        [0, 0, 0, 0, 0, 0, 0, 1],  # 0 -> 1
        [0, 0, 0, 1, 0, 0, 1, 0],  # 1 -> 2
        [0, 0, 1, 0, 0, 0, 1, 1],  # 2 -> 3
        [0, 0, 1, 1, 0, 1, 0, 0],  # 3 -> 4
        [0, 1, 0, 0, 0, 1, 0, 1],  # 4 -> 5
        [0, 1, 0, 1, 0, 1, 1, 0],  # 5 -> 6
        [0, 1, 1, 0, 0, 1, 1, 1],  # 6 -> 7
        [0, 1, 1, 1, 1, 0, 0, 0],  # 7 -> 8
        [1, 0, 0, 0, 1, 0, 0, 1],  # 8 -> 9
        [1, 0, 0, 1, 1, 0, 1, 0],  # 9 -> 10 (в Д8421 это недопустимо, но для полноты)
        [1, 0, 1, 0, None, None, None, None],  # 10 -> не определено
        [1, 0, 1, 1, None, None, None, None],  # 11 -> не определено
        [1, 1, 0, 0, None, None, None, None],  # 12 -> не определено
        [1, 1, 0, 1, None, None, None, None],  # 13 -> не определено
        [1, 1, 1, 0, None, None, None, None],  # 14 -> не определено
        [1, 1, 1, 1, None, None, None, None]  # 15 -> не определено
    ]

    input_vars = ['D8', 'D4', 'D2', 'D1']
    output_vars = ['Y3', 'Y2', 'Y1', 'Y0']

    print("\nТаблица истинности преобразователя Д8421 в Д8421+1:")
    print("D8 | D4 | D2 | D1 | Y3 | Y2 | Y1 | Y0")
    print("-" * 35)
    for row in truth_table:
        print(f"{row[0]}  | {row[1]}  | {row[2]}  | {row[3]}  | " +
              f"{row[4] if row[4] is not None else 'X'}  | " +
              f"{row[5] if row[5] is not None else 'X'}  | " +
              f"{row[6] if row[6] is not None else 'X'}  | " +
              f"{row[7] if row[7] is not None else 'X'}")

    # Анализ для каждого выхода
    for i, output_var in enumerate(output_vars, 4):
        print("\n" + "-" * 30 + f" Анализ для выхода {output_var} " + "-" * 30)

        # Создаем таблицу истинности только для этого выхода
        output_table = []
        for row in truth_table:
            if row[i] is not None:
                output_table.append(row[:4] + [row[i]])

        # Генерируем СДНФ и минимизируем
        sdnf, sknf, sdnf_indices, sknf_indices = generate_sdnf_sknf(output_table, input_vars)
        print("\nСДНФ:", sdnf)
        print("Числовая форма СДНФ:", ", ".join(sdnf_indices))

        # Минимизация с учетом неопределенных состояний
        minimized_sdnf = minimize_sdnf(sdnf, input_vars)
        print("Минимизированная СДНФ:", minimized_sdnf)

        # Карта Карно
        values = []
        for row in truth_table:
            values.append(row[i] if row[i] is not None else None)

        kmap = build_karnaugh_map(input_vars, values)
        print_karnaugh_map(kmap, input_vars)

    # Демонстрация работы преобразователя
    print("\n" + "=" * 30 + " Демонстрация работы преобразователя " + "=" * 30)
    converter = D8421Converter()

    while True:
        try:
            decimal = int(input("\nВведите число от 0 до 9 (или -1 для выхода): "))
            if decimal == -1:
                break
            if decimal < 0 or decimal > 9:
                print("Число должно быть от 0 до 9")
                continue

            result = converter.convert(decimal)

            print("\nРезультат преобразования:")
            print(f"Входное число: {result['input']['decimal']}")
            print(f"Двоичный вход (D8421): {result['input']['binary']}")
            print(f"Двоичный выход (D8421+1): {result['output']['binary']}")
            print(f"Десятичный выход: {result['output']['decimal']}")
        except ValueError:
            print("Пожалуйста, введите целое число от 0 до 9")


if __name__ == "__main__":
    part1_3bit_adder()
    part2_D8421_to_D8421_plus_1()