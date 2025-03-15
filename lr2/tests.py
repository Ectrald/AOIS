import unittest
from main import implication, equivalence, infix_to_postfix, evaluate_postfix, generate_truth_values, \
    generate_sdnf_sknf, truth_table


class TestTruthTableFunctions(unittest.TestCase):
    def test_implication(self):
        self.assertTrue(implication(False, False))
        self.assertTrue(implication(False, True))
        self.assertFalse(implication(True, False))
        self.assertTrue(implication(True, True))

    def test_equivalence(self):
        self.assertTrue(equivalence(True, True))
        self.assertTrue(equivalence(False, False))
        self.assertFalse(equivalence(True, False))
        self.assertFalse(equivalence(False, True))

    def test_infix_to_postfix(self):
        self.assertEqual(infix_to_postfix("a & b"), ["a", "b", "&"])
        self.assertEqual(infix_to_postfix("a | b"), ["a", "b", "|"])
        self.assertEqual(infix_to_postfix("!a & b"), ["a", "!", "b", "&"])
        self.assertEqual(infix_to_postfix("a -> b"), ["a", "b", "->"])

    def test_evaluate_postfix(self):
        values = {"a": True, "b": False}
        self.assertTrue(evaluate_postfix(["a", "b", "|"], values))
        self.assertFalse(evaluate_postfix(["a", "b", "&"], values))
        self.assertTrue(evaluate_postfix(["a", "!"], {"a": False}))
        self.assertFalse(evaluate_postfix(["a", "b", "->"], {"a": True, "b": False}))

    def test_generate_truth_values(self):
        self.assertEqual(generate_truth_values(2),
                         [[False, False], [False, True], [True, False], [True, True]])

    def test_generate_sdnf_sknf(self):
        truth_table = [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1]]  # Пример
        variables = ["a", "b"]
        sdnf, sknf, sdnf_indices, sknf_indices = generate_sdnf_sknf(truth_table, variables)
        self.assertEqual(sdnf, "(!a & b) | (a & !b) | (a & b)")
        self.assertEqual(sknf, "(a | b)")
        self.assertEqual(sdnf_indices, ["1", "2", "3"])
        self.assertEqual(sknf_indices, ["0"])

    def test_truth_table(self):
        table = truth_table("!a", sorted(set(filter(str.isalpha, "!a"))))
        self.assertEqual("1 - 01", table)
if __name__ == "__main__":
    unittest.main()