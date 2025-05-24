import unittest
from copy import deepcopy
from io import StringIO
from contextlib import redirect_stdout
import sys
from main import AssociativeProcessorDiagonal, example_matrix_data_str


class TestAssociativeProcessorDiagonal(unittest.TestCase):
    def setUp(self):
        self.ap = AssociativeProcessorDiagonal()
        self.ap.initialize_matrix_from_data(example_matrix_data_str)

    def test_initialize_matrix_from_data(self):
        self.assertEqual(len(self.ap.matrix), 16)
        self.assertEqual(len(self.ap.matrix[0]), 16)
        self.assertEqual(self.ap.matrix[0], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(self.ap.matrix[11], [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    def test_generate_random_matrix(self):
        self.ap.generate_random_matrix()
        for row in self.ap.matrix:
            for item in row:
                self.assertIn(item, (0, 1))
        self.assertEqual(len(self.ap.matrix), 16)
        self.assertEqual(len(self.ap.matrix[0]), 16)

    def test_read_write_word(self):
        test_word = [1] * 16
        self.ap.write_word(5, test_word)
        result = self.ap.read_word(5)
        self.assertEqual(result, test_word)

        self.ap.write_word(0, [0] * 16)
        self.assertEqual(self.ap.read_word(0), [0] * 16)
        self.ap.write_word(15, [1] * 16)
        self.assertEqual(self.ap.read_word(15), [1] * 16)

        with self.assertRaises(ValueError):
            self.ap.write_word(16, test_word)
        with self.assertRaises(ValueError):
            self.ap.read_word(-1)

    def test_read_write_address_column_diagonal(self):
        col_data = [((i + 3) % 2) for i in range(16)]
        self.ap.write_address_column_diagonal(2, col_data)
        read_col = self.ap.read_address_column_diagonal(2)
        self.assertEqual(read_col, col_data)

        self.ap.write_address_column_diagonal(0, [0] * 16)
        self.assertEqual(self.ap.read_address_column_diagonal(0), [0] * 16)
        self.ap.write_address_column_diagonal(15, [1] * 16)
        self.assertEqual(self.ap.read_address_column_diagonal(15), [1] * 16)

        with self.assertRaises(ValueError):
            self.ap.write_address_column_diagonal(17, col_data)
        with self.assertRaises(ValueError):
            self.ap.read_address_column_diagonal(-1)

    def test_apply_logical_func(self):
        self.ap.write_word(0, [1] * 16)
        self.ap.write_word(1, [0] * 16)
        self.ap.apply_logical_func('f0', 0, 1, 2)
        self.assertEqual(self.ap.read_word(2), [0] * 16)

        self.ap.write_word(3, [1, 0] * 8)
        self.ap.write_word(4, [0, 1] * 8)
        self.ap.apply_logical_func('f5', 3, 4, 5)
        self.assertEqual(self.ap.read_word(5), [0, 1] * 8)

        self.ap.apply_logical_func('f10', 3, 4, 6)
        self.assertEqual(self.ap.read_word(6), [1, 0] * 8)

        self.ap.apply_logical_func('f15', 3, 4, 7)
        self.assertEqual(self.ap.read_word(7), [1] * 16)

        with self.assertRaises(ValueError):
            self.ap.apply_logical_func('unknown', 0, 1, 2)
        with self.assertRaises(ValueError):
            self.ap.apply_logical_func('f0', -1, 1, 2)
        with self.assertRaises(ValueError):
            self.ap.apply_logical_func('f0', 0, 16, 2)

    def test_search_by_correspondence(self):
        arg = self.ap.read_word(0)
        matches = self.ap.search_by_correspondence(arg)
        self.assertIn(0, matches)

        arg = [1 - b for b in self.ap.read_word(0)]
        matches = self.ap.search_by_correspondence(arg)
        self.assertTrue(isinstance(matches, list))

        self.ap.write_word(1, arg)
        self.ap.write_word(2, arg)
        matches = self.ap.search_by_correspondence(arg)
        self.assertIn(1, matches)
        self.assertIn(2, matches)

    def test_search_by_correspondence_with_g_l(self):
        arg = self.ap.read_word(1)
        matches = self.ap.search_by_correspondence_with_g_l(arg)
        self.assertIn(1, matches)

        arg_mask = [-1] * 16
        matches = self.ap.search_by_correspondence_with_g_l(arg_mask)
        self.assertEqual(set(matches), set(range(16)))

        arg = [1, 0] + [-1] * 14
        matches = self.ap.search_by_correspondence_with_g_l(arg)
        self.assertTrue(len(matches) > 0)

        arg = [1] * 16
        self.ap.write_word(0, [0] * 16)
        matches = self.ap.search_by_correspondence_with_g_l(arg)
        self.assertEqual(matches, [])

    def test_arithmetic_sum_fields(self):
        # Test case 1: V=101, A=0001, B=0011 (1+3=4)
        word = [1, 0, 1] + [0, 0, 0, 1] + [0, 0, 1, 1] + [0] * 5
        self.ap.write_word(0, word)
        self.ap.arithmetic_sum_fields([1, 0, 1])
        updated = self.ap.read_word(0)
        self.assertEqual(updated[11:16], [0, 0, 1, 0, 0])

        # Test case 2: Overflow (A=1111, B=1111, sum=30, 5 bits=11110)
        word = [1, 0, 1] + [1, 1, 1, 1] + [1, 1, 1, 1] + [0] * 5
        self.ap.write_word(1, word)
        self.ap.arithmetic_sum_fields([1, 0, 1])
        updated = self.ap.read_word(1)
        self.assertEqual(updated[11:16], [1, 1, 1, 1, 0])

        # Test case 3: Non-matching key
        before = deepcopy(self.ap.matrix)
        self.ap.write_word(2, [0, 0, 0] + [1, 0, 0, 0] + [0, 0, 0, 1] + [0] * 5)
        self.ap.arithmetic_sum_fields([1, 1, 1])  # No matches
        self.assertEqual(self.ap.read_word(2), [0, 0, 0] + [1, 0, 0, 0] + [0, 0, 0, 1] + [0] * 5)
        self.assertEqual(self.ap.read_word(0), [1, 0, 1] + [0, 0, 0, 1] + [0, 0, 1, 1] + [0, 0, 1, 0, 0])

    def test_display_matrix(self):
        with StringIO() as captured_output:
            with redirect_stdout(captured_output):
                self.ap.display_matrix()
            output = captured_output.getvalue()
        self.assertIn("Текущее состояние матрицы:", output)
        self.assertEqual(len(output.split('\n')), 20)  # 16 rows + header + separator

    def test_display_word_as_string(self):
        with StringIO() as captured_output:
            with redirect_stdout(captured_output):
                self.ap.display_word_as_string([1, 0] * 8, "TestWord")
            output = captured_output.getvalue()
        self.assertIn("TestWord: 1010101010101010", output)

    def test_bin_list_to_int(self):
        self.assertEqual(self.ap._bin_list_to_int([1, 0, 1]), 5)
        self.assertEqual(self.ap._bin_list_to_int([0, 0, 0]), 0)
        self.assertEqual(self.ap._bin_list_to_int([1, 1, 1, 1]), 15)

    def test_int_to_bin_list(self):
        self.assertEqual(self.ap._int_to_bin_list(4, 5), [0, 0, 1, 0, 0])
        self.assertEqual(self.ap._int_to_bin_list(30, 5), [1, 1, 1, 1, 0])
        self.assertEqual(self.ap._int_to_bin_list(0, 5), [0, 0, 0, 0, 0])

    def test_errors(self):
        with self.assertRaises(ValueError):
            self.ap.initialize_matrix_from_data("1,0,0,0\n1,0,0,0")
        with self.assertRaises(ValueError):
            self.ap.write_word(0, [1, 0, 1])
        with self.assertRaises(ValueError):
            self.ap.write_address_column_diagonal(0, [1, 1, 1])
        with self.assertRaises(ValueError):
            self.ap.arithmetic_sum_fields([1, 1, 1, 1])




if __name__ == "__main__":
    unittest.main()