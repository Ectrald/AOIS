class DiagonalMatrix:
    def __init__(self, size=16):
        self.size = size
        # Инициализируем матрицу нулями
        self.matrix = [[0 for _ in range(size)] for _ in range(size)]

    def set_matrix(self, matrix_data):
        """Загружает матрицу из предоставленных данных"""
        for i in range(self.size):
            for j in range(self.size):
                self.matrix[i][j] = matrix_data[i][j]

    def get_word(self, word_index):
        """Возвращает слово по индексу (диагональная адресация)"""
        word = []
        for i in range(self.size):
            # Вычисляем правильный столбец с учетом диагонального расположения
            col = (word_index + i) % self.size
            word.append(self.matrix[i][col])
        return word

    def set_word(self, word_index, word_data):
        """Устанавливает слово по индексу (диагональная адресация)"""
        for i in range(self.size):
            col = (word_index + i) % self.size
            self.matrix[i][col] = word_data[i]

    def get_address_column(self, column_index):
        """Возвращает адресный столбец по индексу"""
        return [row[column_index] for row in self.matrix]

    def set_address_column(self, column_index, column_data):
        """Устанавливает адресный столбец по индексу"""
        for i in range(self.size):
            self.matrix[i][column_index] = column_data[i]

    def apply_logical_function(self, func_num, word1_idx, word2_idx, result_word_idx):
        """Применяет логическую функцию к двум словам и сохраняет результат"""
        word1 = self.get_word(word1_idx)
        word2 = self.get_word(word2_idx)

        result = []
        for b1, b2 in zip(word1, word2):
            if func_num == 5:  # f5: И-НЕ (NAND)
                result.append(0 if (b1 and b2) else 1)
            elif func_num == 10:  # f10: Исключающее ИЛИ (XOR)
                result.append(b1 ^ b2)
            elif func_num == 0:  # f0: Константа 0
                result.append(0)
            elif func_num == 15:  # f15: Константа 1
                result.append(1)
            else:
                raise ValueError(f"Unsupported function number: {func_num}")

        self.set_word(result_word_idx, result)

    def add_fields_for_matching_v(self, v_key):
        """Сложение полей Aj и Bj в словах, где Vj совпадает с заданным V"""
        for word_idx in range(self.size):
            word = self.get_word(word_idx)
            # Проверяем первые 3 бита слова
            if word[:3] == v_key:
                # Разбиваем слово на части: V(3), A(4), B(4), S(5)
                v_part = word[:3]
                a_part = word[3:7]
                b_part = word[7:11]
                s_part = word[11:16]

                # Преобразуем A и B в целые числа
                a_int = int(''.join(map(str, a_part)), 2)
                b_int = int(''.join(map(str, b_part)), 2)

                # Выполняем сложение и обрезаем до 5 бит
                sum_result = a_int + b_int
                sum_bits = [int(b) for b in format(sum_result, '05b')[-5:]]

                # Собираем новое слово
                new_word = v_part + a_part + b_part + sum_bits
                self.set_word(word_idx, new_word)

    def search_by_pattern(self, pattern):
        """Поиск по соответствию (Вариант 4)"""
        matches = []
        for word_idx in range(self.size):
            word = self.get_word(word_idx)
            if all(b == -1 or b == word[i] for i, b in enumerate(pattern)):
                matches.append(word_idx)
        return matches

    def display_matrix(self):
        """Выводит матрицу в удобочитаемом формате"""
        for row in self.matrix:
            print(' '.join(map(str, row)))

    def display_word(self, word_idx):
        """Выводит слово по индексу"""
        word = self.get_word(word_idx)
        print(f"Слово {word_idx}: {''.join(map(str, word))}")


# Пример использования
if __name__ == "__main__":
    # Создаем матрицу и заполняем данными из примера
    matrix_data = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    dm = DiagonalMatrix()
    dm.set_matrix(matrix_data)

    print("Исходная матрица:")
    dm.display_matrix()

    # Пример 1: Чтение слова #2
    print("\nПример 1: Чтение слова #2")
    dm.display_word(2)

    # Пример 2: Чтение адресного столбца #3
    print("\nПример 2: Чтение адресного столбца #3")
    col3 = dm.get_address_column(3)
    print(f"Столбец 3: {''.join(map(str, col3))}")

    # Пример 3: Применение логической функции f5 (И-НЕ) к словам 2 и 3, результат в слово 15
    print("\nПример 3: Применение логической функции f5 (И-НЕ)")
    dm.apply_logical_function(5, 2, 3, 15)
    dm.display_word(15)

    # Пример 4: Сложение полей Aj и Bj в словах, где Vj = [1,1,1]
    print("\nПример 4: Сложение полей Aj и Bj для слов с Vj=111")
    dm.add_fields_for_matching_v([1, 1, 1])
    dm.display_word(0)  # В примере только слово 0 имеет Vj=111

    # Пример 5: Поиск по соответствию (Вариант 4)
    print("\nПример 5: Поиск по соответствию")
    # Ищем слова, где первые 3 бита = 111 (остальные могут быть любыми)
    pattern = [1, 1, 1] + [-1] * 13  # -1 означает "любое значение"
    matches = dm.search_by_pattern(pattern)
    print(f"Найдены слова с Vj=111: {matches}")