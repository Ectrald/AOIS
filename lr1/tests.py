import unittest
from functions import *
class TestBinaryOperations(unittest.TestCase):
    def test_convert_number_to_binary_code(self):
        # Проверяем корректное преобразование чисел
        self.assertEqual(convert_number_to_binary_code(5), "00000101")
        self.assertEqual(convert_number_to_binary_code(-5), "10000101")

    def test_get_revers_code(self):
        # Проверяем обратный код
        self.assertEqual(get_revers_code("00000101"), "00000101")  # Положительное число
        self.assertEqual(get_revers_code("10000101"), "11111010")  # Отрицательное число

    def test_get_additional_code(self):
        # Проверяем дополнительный код
        self.assertEqual(get_additional_code("00000101"), "00000101")  # Положительное число
        self.assertEqual(get_additional_code("11111010"), "11111011")  # Обратный код для -5

    def test_binary_to_signed_decimal(self):
        # Проверяем преобразование бинарных строк в десятичные числа
        self.assertEqual(binary_to_signed_decimal("00000101"), 5)
        self.assertEqual(binary_to_signed_decimal("10000101"), -5)

    def test_binary_addition(self):
        # Проверяем сложение
        self.assertEqual(binary_addition(5, 3), 8)

    def test_binary_subtraction(self):
        # Проверяем вычитание
        self.assertEqual(binary_subtraction(10, 3), 7)

    def test_binary_multiplication(self):
        # Проверяем умножение
        self.assertEqual(binary_multiplication(5, 3), "00001111")  # 15
        self.assertEqual(binary_multiplication(-5, 3), "10001111")  # -15

    def test_binary_division(self):
        # Проверяем деление
        self.assertEqual(binary_division(10, 3), "00000011.01010")  # 3.3125
        self.assertEqual(binary_division(-10, 3), "10000011.01010")  # -3.3125

    def test_binary_fixed_point_to_decimal(self):
        # Проверяем преобразование бинарной строки с фиксированной точкой
        self.assertEqual(binary_fixed_point_to_decimal("00000011.01010"), 3.3125)
        self.assertEqual(binary_fixed_point_to_decimal("10000011.01010"), -3.3125)

    def test_float_to_ieee754(self):
        # Проверяем преобразование в IEEE-754 (если функция поддерживает)
        if hasattr(float_to_ieee754, "__call__"):
            self.assertEqual(float_to_ieee754(1.5), [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_ieee754_to_float(self):
        # Проверяем преобразование из IEEE-754 (если функция поддерживает)
        if hasattr(ieee754_to_float, "__call__"):
            self.assertAlmostEqual(ieee754_to_float([0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), 1.5)

    def test_addition_float(self):
        # Проверяем сложение чисел с плавающей точкой (если функция поддерживает)
        if hasattr(addition_float, "__call__"):
            self.assertAlmostEqual(addition_float(1.5, 2.75), 4.25)

if __name__ == "__main__":
    unittest.main()