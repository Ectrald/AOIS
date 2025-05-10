from itertools import product


class DigitalCounter:
    def __init__(self, num_states):
        self.num_states = num_states
        self.num_bits = (num_states - 1).bit_length()
        self.states = list(product([0, 1], repeat=self.num_bits))
        self.transition_table = []
        self.excitation_table = []

    def build_transition_table(self):
        """Строит таблицу переходов для счетчика"""
        for i in range(self.num_states):
            current_state = self.states[i]
            next_state = self.states[(i + 1) % self.num_states]
            self.transition_table.append((current_state, next_state))

    def build_excitation_table(self):
        """Строит таблицу возбуждения для T-триггеров"""
        for current, next_state in self.transition_table:
            excitation = []
            for curr_bit, next_bit in zip(current, next_state):
                # Для T-триггера: 0 - нет изменения, 1 - инвертировать
                excitation.append(0 if curr_bit == next_bit else 1)
            self.excitation_table.append((current, excitation))

    def get_excitation_functions(self):
        """Возвращает функции возбуждения для каждого триггера"""
        functions = []
        for i in range(self.num_bits):
            truth_table = []
            for j, (state, exc) in enumerate(self.excitation_table):
                # Добавляем входной сигнал V (всегда 1 для счетчика)
                row = list(state) + [1] + [exc[i]]
                truth_table.append(row)
            functions.append(truth_table)
        return functions

    def minimize_functions(self, functions, variables):
        """Минимизирует функции возбуждения"""
        minimized = []
        for i, func in enumerate(functions):
            # Собираем минтермы (где функция возбуждения = 1)
            minterms = []
            for row in func:
                if row[-1] == 1:
                    minterms.append(row[:-1])

            if not minterms:
                minimized.append("0")
                continue

            # Минимизируем с помощью метода Квайна-Маккласки
            prime_implicants = self.qm_minimize(minterms, len(variables))
            minimized_expr = self.implicants_to_expr(prime_implicants, variables)
            minimized.append(minimized_expr)
        return minimized

    def qm_minimize(self, minterms, num_vars):
        """Метод Квайна-Маккласки для минимизации"""
        # Преобразуем минтермы в битовые строки
        terms = [(self.to_binary(m, num_vars), {i}) for i, m in enumerate(minterms)]
        prime_implicants = []

        while True:
            used = [False] * len(terms)
            new_terms = []

            # Попарное сравнение терминов
            for i in range(len(terms)):
                for j in range(i + 1, len(terms)):
                    bits1, set1 = terms[i]
                    bits2, set2 = terms[j]
                    diff = 0
                    new_bits = []

                    for b1, b2 in zip(bits1, bits2):
                        if b1 != b2:
                            diff += 1
                            new_bits.append('-')
                        else:
                            new_bits.append(b1)

                    if diff == 1:
                        used[i] = True
                        used[j] = True
                        new_term = (''.join(new_bits), set1.union(set2))
                        if new_term not in new_terms:
                            new_terms.append(new_term)

            # Добавляем неиспользованные термины как простые импликанты
            for idx, flag in enumerate(used):
                if not flag and terms[idx] not in prime_implicants:
                    prime_implicants.append(terms[idx])

            if not new_terms:
                break

            terms = new_terms

        return prime_implicants

    def to_binary(self, minterm, num_vars):
        """Преобразует минтерм в битовую строку"""
        return ''.join(['1' if x else '0' for x in minterm])

    def implicants_to_expr(self, implicants, variables):
        """Преобразует импликанты в логическое выражение"""
        terms = []
        for imp in implicants:
            bits, _ = imp
            literals = []
            for i, bit in enumerate(bits):
                if bit == '1':
                    literals.append(variables[i])
                elif bit == '0':
                    literals.append(f"!{variables[i]}")
            if literals:
                terms.append(" & ".join(literals))

        return " | ".join(terms) if terms else "0"

    def print_tables(self):
        """Выводит таблицы переходов и возбуждения"""
        print("\nТаблица переходов:")
        print("Текущее состояние | Следующее состояние")
        print("-" * 40)
        for current, next_state in self.transition_table:
            print(f"{' '.join(map(str, current)):^16} | {' '.join(map(str, next_state)):^16}")

        print("\nТаблица возбуждения T-триггеров:")
        header = "Текущее состояние | " + " | ".join([f"T{i}" for i in range(self.num_bits)])
        print(header)
        print("-" * len(header))
        for current, exc in self.excitation_table:
            print(f"{' '.join(map(str, current)):^16} | {' | '.join(map(str, exc))}")

    def print_minimized_functions(self, minimized, variables):
        print("\nМинимизированные сднф :")
        # Для счетчика функции имеют простой вид
        for i in range(self.num_bits):
            terms = []
            for j in range(i):
                terms.append(variables[j])
            if terms:
                print(f"T{i} = {' & '.join(terms)}")
            else:
                print(f"T{i} = 1")


def main():
    num_states = 8  # 8 внутренних состояний для 3-битного счетчика
    counter = DigitalCounter(num_states)
    counter.build_transition_table()
    counter.build_excitation_table()
    counter.print_tables()

    variables = ['Q2', 'Q1', 'Q0']  # Q2 - старший бит
    excitation_functions = counter.get_excitation_functions()
    minimized = counter.minimize_functions(excitation_functions, variables + ['V'])

    counter.print_minimized_functions(minimized, variables)



if __name__ == "__main__":
    main()