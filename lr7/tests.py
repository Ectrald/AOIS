import unittest
from copy import deepcopy

from main import AssociativeProcessorDiagonal, example_matrix_data_str

class TestAssociativeProcessorDiagonal(unittest.TestCase):
    def setUp(self):
        self.ap = AssociativeProcessorDiagonal()
        self.ap.initialize_matrix_from_data(example_matrix_data_str)

    def test_initialize_matrix_from_data(self):
        # Проверяем размерность и содержимое первой строки
        self.assertEqual(len(self.ap.matrix), 16)
        self.assertEqual(len(self.ap.matrix[0]), 16)
        self.assertEqual(self.ap.matrix[0], [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

    def test_generate_random_matrix(self):
        self.ap.generate_random_matrix()
        for row in self.ap.matrix:
            for item in row:
                self.assertIn(item, (0, 1))

    def test_read_write_word(self):
        test_word = [1]*16
        self.ap.write_word(5, test_word)
        result = self.ap.read_word(5)
        self.assertEqual(result, test_word)

        with self.assertRaises(ValueError):
            self.ap.write_word(16, test_word)  # индекс вне диапазона

    def test_read_write_address_column_diagonal(self):
        col_data = [((i + 3) % 2) for i in range(16)]
        self.ap.write_address_column_diagonal(2, col_data)
        read_col = self.ap.read_address_column_diagonal(2)
        self.assertEqual(read_col, col_data)

        with self.assertRaises(ValueError):
            self.ap.write_address_column_diagonal(17, col_data)

    def test_apply_logical_func(self):
        # Проверка f0 (всегда 0)
        self.ap.write_word(0, [1]*16)
        self.ap.write_word(1, [0]*16)
        self.ap.apply_logical_func('f0', 0, 1, 2)
        self.assertEqual(self.ap.read_word(2), [0]*16)

        # Проверка f5 (результат = второй операнд)
        self.ap.write_word(3, [1,0]*8)
        self.ap.write_word(4, [0,1]*8)
        self.ap.apply_logical_func('f5', 3, 4, 5)
        self.assertEqual(self.ap.read_word(5), [0,1]*8)

        # Проверка f10 (инверсия второго операнда)
        self.ap.apply_logical_func('f10', 3, 4, 6)
        self.assertEqual(self.ap.read_word(6), [1,0]*8)

        # Проверка f15 (всегда 1)
        self.ap.apply_logical_func('f15', 3, 4, 7)
        self.assertEqual(self.ap.read_word(7), [1]*16)

        with self.assertRaises(ValueError):
            self.ap.apply_logical_func('unknown', 0, 1, 2)

    def test_search_by_correspondence(self):
        # В тестовой матрице есть слово, совпадающее с аргументом
        arg = self.ap.read_word(0)
        matches = self.ap.search_by_correspondence(arg)
        self.assertIn(0, matches)

        # Аргумент, не совпадающий ни с одним словом
        arg = [1 - b for b in self.ap.read_word(0)]
        matches = self.ap.search_by_correspondence(arg)
        self.assertTrue(isinstance(matches, list))

    def test_search_by_correspondence_with_g_l(self):
        arg = self.ap.read_word(1)
        matches = self.ap.search_by_correspondence_with_g_l(arg)
        self.assertIn(1, matches)

        # С маской (должно вернуть все слова, если все -1)
        arg_mask = [-1]*16
        matches = self.ap.search_by_correspondence_with_g_l(arg_mask)
        self.assertEqual(set(matches), set(range(16)))

    def test_arithmetic_sum_fields(self):
        # Для теста упростим: запишем в S0 слово, где V=101, A=0001, B=0011 (1+3=4)
        word = [1,0,1] + [0,0,0,1] + [0,0,1,1] + [0]*5  # V=101, A=1, B=3, S=00000
        self.ap.write_word(0, word)
        self.ap.arithmetic_sum_fields([1,0,1])
        updated = self.ap.read_word(0)

        # Проверяем, что поле S стало равно 00100 (4)
        self.assertEqual(updated[11:16], [0,0,1,0,0])

        # Если ключ не совпадает, изменений не должно быть
        before = deepcopy(self.ap.matrix)
        self.ap.arithmetic_sum_fields([0,0,0])  # Нет такого V


    def test_errors(self):
        # Некорректная длина данных
        with self.assertRaises(ValueError):
            self.ap.initialize_matrix_from_data("1,0,0,0\n1,0,0,0")  # мало строк

        with self.assertRaises(ValueError):
            self.ap.write_word(0, [1,0,1])  # мало бит

        with self.assertRaises(ValueError):
            self.ap.write_address_column_diagonal(0, [1,1,1])  # мало бит

        with self.assertRaises(ValueError):
            self.ap.arithmetic_sum_fields([1,1,1,1])  # слишком много бит

if __name__ == "__main__":
    unittest.main()