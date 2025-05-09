import unittest
from io import StringIO
from contextlib import redirect_stdout
import sys


from main12 import *


class TestLogicMinimization(unittest.TestCase):

    def test_implication(self):
        self.assertTrue(implication(False, True))
        self.assertTrue(implication(False, False))
        self.assertTrue(implication(True, True))
        self.assertFalse(implication(True, False))

    def test_equivalence(self):
        self.assertTrue(equivalence(True, True))
        self.assertTrue(equivalence(False, False))
        self.assertFalse(equivalence(True, False))
        self.assertFalse(equivalence(False, True))

    def test_generate_truth_values(self):
        # Для 2 переменных
        expected = [[False, False], [False, True], [True, False], [True, True]]
        self.assertEqual(generate_truth_values(2), expected)
        # Для 1 переменной
        self.assertEqual(generate_truth_values(1), [[False], [True]])

    def test_precedence(self):
        self.assertEqual(precedence("!"), 3)
        self.assertEqual(precedence("&"), 2)
        self.assertEqual(precedence("|"), 2)
        self.assertEqual(precedence("->"), 1)
        self.assertEqual(precedence("~"), 1)
        self.assertEqual(precedence("random"), 0)

    def test_infix_to_postfix(self):
        expr = "a&b"
        tokens = infix_to_postfix(expr)
        self.assertEqual(tokens, ['a', 'b', '&'])

        expr = "a->b"
        tokens = infix_to_postfix(expr)
        self.assertEqual(tokens, ['a', 'b', '->'])

        expr = "a~b"
        tokens = infix_to_postfix(expr)
        self.assertEqual(tokens, ['a', 'b', '~'])

        # Проверка с вложенными скобками
        expr = "!(a|b)"
        tokens = infix_to_postfix(expr)
        self.assertIn('!', tokens)
        self.assertIn('a', tokens)
        self.assertIn('b', tokens)

    def test_evaluate_postfix(self):
        tokens = ['a', 'b', '&']
        values = {"a": True, "b": False}
        self.assertFalse(evaluate_postfix(tokens, values))

        tokens = ['a', 'b', '|']
        values = {"a": False, "b": False}
        self.assertFalse(evaluate_postfix(tokens, values))

    def test_generate_sdnf_sknf(self):
        # Используем небольшую таблицу истинности для 2 переменных
        truth_table_data = [
            [0, 0, 0],
            [0, 1, 0],
            [1, 0, 1],
            [1, 1, 1]
        ]
        variables = ['a', 'b']
        sdnf, sknf, sdnf_indices, sknf_indices = generate_sdnf_sknf(truth_table_data, variables)
        # В таблице истина только для строк 2 и 3
        self.assertIn("(a & !b)", sdnf)
        self.assertIn("(a & b)", sdnf)
        self.assertEqual(sdnf_indices, ['2', '3'])
        # Для макстермов (результат 0) — строки 0 и 1
        self.assertIn("(a | b)", sknf)
        self.assertIn("(a | !b)", sknf)
        self.assertEqual(sknf_indices, ['0', '1'])

    def test_minimize_sdnf_by_calculation_method(self):
        # Тест минимизации СДНФ. Если взять (a & !b) | (a & b) должно свестись к a
        sdnf = "(a & !b) | (a & b)"
        variables = ['a', 'b']
        minimized = minimize_sdnf_by_calculation_method(sdnf, variables)
        self.assertIn("a", minimized)
        # Если получится просто (a) или (a & ...), то проверяем отсутствие лишних литералов
        self.assertNotIn("!b", minimized)

    def test_minimize_sknf_by_calculation_method(self):
        # Аналогичный тест для СКНФ – (a | !b) & (a | b) должно свестись к a
        sknf = "(a | !b) & (a | b)"
        variables = ['a', 'b']
        minimized = minimize_sknf_by_calculation_method(sknf, variables)
        self.assertIn("a", minimized)

    def test_minimize_sdnf_by_calculation_spreadsheet_method(self):
        # Тест расчетно-табличного метода для СДНФ
        sdnf = "(a & !b) | (a & b)"
        variables = ['a', 'b']
        with StringIO() as buf, redirect_stdout(buf):
            minimized = minimize_sdnf_by_calculation_spreadsheet_method(sdnf, variables)
            output = buf.getvalue()
        self.assertIn("Этап", output)  # проверяем вывод этапов
        self.assertIn("a", minimized)
        self.assertNotIn("!b", minimized)

    def test_minimize_sknf_by_calculation_spreadsheet_method(self):
        # Тест расчетно-табличного метода для СКНФ
        sknf = "(a | !b) & (a | b)"
        variables = ['a', 'b']
        with StringIO() as buf, redirect_stdout(buf):
            minimized = minimize_sknf_by_calculation_spreadsheet_method(sknf, variables)
            output = buf.getvalue()
        self.assertIn("Этап", output)
        self.assertIn("a", minimized)

    def test_qm_minimize(self):
        # Создаем таблицу истинности для функции, где истина при a=1 (для 2 переменных)
        truth_table_data = [
            [0, 0, 0],
            [0, 1, 0],
            [1, 0, 1],
            [1, 1, 1]
        ]
        variables = ['a', 'b']
        minimized = qm_minimize(truth_table_data, variables, is_sdnf=True)
        self.assertIn("a", minimized)

    def test_build_karnaugh_map(self):
        # Для 2 переменных
        truth_values = [1, 0, 0, 1]
        variables = ['a', 'b']
        kmap = build_karnaugh_map(variables, truth_values)
        self.assertEqual(len(kmap), 2)
        self.assertEqual(len(kmap[0]), 2)

    def test_print_karnaugh_map(self):
        truth_values = [1, 0, 0, 1]
        variables = ['a', 'b']
        kmap = build_karnaugh_map(variables, truth_values)
        with StringIO() as buf, redirect_stdout(buf):
            print_karnaugh_map(kmap, variables)
            out = buf.getvalue()
        self.assertIn("Карта Карно", out)

    def test_build_var_map(self):
        vm2 = build_var_map(2)
        self.assertEqual(len(vm2), 2)
        self.assertEqual(len(vm2[0]), 2)
        vm3 = build_var_map(3)
        self.assertEqual(len(vm3), 2)  # функция для 3 переменных возвращает 2 строки

    def test_find_all_groups_2d(self):
        # Простой пример для 2х2 карты
        kmap = [
            [True, True],
            [False, True]
        ]
        groups = find_all_groups_2d(kmap, True)
        # Ожидаем хотя бы одну группу, содержащую более одного элемента
        self.assertTrue(any(len(g) > 1 for g in groups))

    def test_group_to_term(self):
        var_map = [['00', '01'], ['10', '11']]
        variables = ['a', 'b']
        group = {(0, 0), (0, 1)}
        term = group_to_term(group, var_map, variables)
        # В группе первая строка, для переменной a всегда 0 → ожидаем отрицание a
        self.assertIn("!a", term)

    def test_build_prime_chart(self):
        groups = [{(0, 0), (0, 1)}, {(1, 0)}]
        minterm_coords = [(0, 0), (0, 1), (1, 0)]
        chart = build_prime_chart(groups, minterm_coords)
        self.assertEqual(len(chart), 3)
        for indices in chart.values():
            self.assertIsInstance(indices, set)

    def test_select_essential_groups(self):
        # Пример: пусть для минтермов 0 и 1 есть группы 0 и 1, где:
        # - минтерм 1 покрывается только группой 1
        chart = {0: {0, 1}, 1: {1}}
        groups = [{(0, 0)}, {(0, 0), (0, 1)}]
        essentials = select_essential_groups(chart, groups)
        self.assertTrue(len(essentials) > 0)

    def test_minimize_with_karnaugh(self):
        truth_table_data = [
            [0, 0, 1],
            [0, 1, 1],
            [1, 0, 0],
            [1, 1, 0]
        ]
        variables = ['a', 'b']
        minimized = minimize_with_karnaugh(truth_table_data, variables, True)
        self.assertIn("(", minimized)
        self.assertGreater(len(minimized), 0)

    def test_initialize_5var_kmap(self):
        # Создание таблицы истинности для 5 переменных (32 строки)
        truth_table_data = []
        for i in range(32):
            bits = [int(x) for x in bin(i)[2:].zfill(5)]
            # Произвольная функция: 1 для нечетных чисел, 0 для четных
            truth_table_data.append(bits + [i % 2])
        variables = ['a', 'b', 'c', 'd', 'e']
        kmap = initialize_5var_kmap(truth_table_data, variables)
        self.assertEqual(len(kmap), 8)
        self.assertEqual(len(kmap[0]), 4)

    def test_print_5var_kmap(self):
        truth_table_data = []
        for i in range(32):
            bits = [int(x) for x in bin(i)[2:].zfill(5)]
            truth_table_data.append(bits + [i % 2])
        variables = ['a', 'b', 'c', 'd', 'e']
        with StringIO() as buf, redirect_stdout(buf):
            print_5var_kmap(truth_table_data, variables)
            output = buf.getvalue()
        self.assertIn("Карта Карно для 5 переменных", output)

    def test_qm_prime_implicants(self):
        minterms = [1, 3, 7]
        primes = qm_prime_implicants(minterms, 3)
        self.assertTrue(len(primes) > 0)
        # Проверяем, что каждая импликанта имеет битовую строку нужной длины
        for imp in primes:
            self.assertEqual(len(imp[0]), 3)

    def test_prime_implicant_chart(self):
        prime_imp = qm_prime_implicants([1, 3], 3)
        chart = prime_implicant_chart(prime_imp, [1, 3])
        self.assertTrue(all(isinstance(val, list) for val in chart.values()))

    def test_select_essential_primes_and_choose_cover(self):
        # Используем простую задачу: пусть у нас есть такие примеры.
        prime_implicants = [
            ("10", {0}),
            ("0-", {1}),
            ("1-", {0, 1})
        ]
        chart = {0: [0, 2], 1: [1, 2]}
        essentials = select_essential_primes(chart)
        additional = choose_cover(chart, prime_implicants, essentials)
        # В данном случае индекс 2 должен покрывать все минтермы
        self.assertIn(2, essentials.union(additional))

    def test_implicant_to_term(self):
        # Для СДНФ: '1-0' должно дать (a & !c) для переменных ['a','b','c']
        variables = ['a', 'b', 'c']
        term = implicant_to_term(("1-0", {0, 1}), variables, True)
        self.assertEqual(term, "(a & !c)")
        # Для СКНФ: '1-0' должно дать (¬a | c) (но в нашем коде используется ! вместо ¬)
        term2 = implicant_to_term(("1-0", {0, 1}), variables, False)
        self.assertEqual(term2, "(!a | c)")

    def test_minimize_5var_karnaugh(self):
        # Для 5 переменных создадим таблицу истинности с фиксированными значениями.
        truth_table_data = []
        for i in range(32):
            bits = [int(x) for x in bin(i)[2:].zfill(5)]
            # Функция: истина, если сумма битов > 2
            truth_table_data.append(bits + [1 if sum(bits) > 2 else 0])
        variables = ['a', 'b', 'c', 'd', 'e']
        minimized_sdnf = minimize_5var_karnaugh(truth_table_data, variables, True)
        minimized_sknf = minimize_5var_karnaugh(truth_table_data, variables, False)
        self.assertIsInstance(minimized_sdnf, str)
        self.assertIsInstance(minimized_sknf, str)
        self.assertGreater(len(minimized_sdnf), 0)
        self.assertGreater(len(minimized_sknf), 0)

    def test_truth_table(self):
        # Для функции: (a->b) & (!a|b) эквивалентно (a->b)
        test_input = "(a->b)"
        # Симулируем ввод: используем patch на input() через redirect_stdout, подменяя sys.stdin
        original_stdin = sys.stdin
        try:
            sys.stdin = StringIO(test_input + "\n")
            with StringIO() as buf, redirect_stdout(buf):
                index_form = truth_table(test_input, ['a', 'b'])
                output = buf.getvalue()
            # Проверяем, что прошла печать таблицы истинности и минимизированные формы
            self.assertIn("a | b | Result", output)
            self.assertIn("СДНФ:", output)
            self.assertIn("СКНФ:", output)
            self.assertIn("Индексная форма функции:", output)
            # Также возвращенное значение должно содержать индекс функции
            self.assertIn("-", index_form)
        finally:
            sys.stdin = original_stdin


if __name__ == '__main__':
    unittest.main()
# coverage run -m unittest test3.py
# coverage report -m