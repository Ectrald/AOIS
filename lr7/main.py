import random


class AssociativeProcessorDiagonal:
    def __init__(self, rows=16, cols=16):
        self.rows = rows
        self.cols = cols
        self.matrix = [[0 for _ in range(cols)] for _ in range(rows)]
        # Sj,i (бит i слова j) хранится в matrix[(i+j)%rows][j]

    def initialize_matrix_from_data(self, data_str):
        """
        Инициализирует матрицу из строки с данными, разделенными запятыми,
        где каждая строка входных данных - это строка физической матрицы.
        """
        lines = data_str.strip().split('\n')
        if len(lines) != self.rows:
            raise ValueError(f"Входные данные должны содержать {self.rows} строк.")

        temp_matrix = []
        for r, line in enumerate(lines):
            row_values = [int(x.strip()) for x in line.split(',')]
            if len(row_values) != self.cols:
                raise ValueError(f"Строка {r} должна содержать {self.cols} столбцов.")
            temp_matrix.append(row_values)
        self.matrix = temp_matrix
        print("Матрица инициализирована из предоставленных данных.")

    def generate_random_matrix(self):
        """Заполняет матрицу случайными 0 и 1."""
        self.matrix = [[random.randint(0, 1) for _ in range(self.cols)] for _ in range(self.rows)]
        print("Матрица инициализирована случайными двоичными значениями.")

    def display_matrix(self):
        """Выводит текущее состояние физической матрицы."""
        print("\nТекущее состояние матрицы:")
        for r in range(self.rows):
            print(' '.join(map(str, self.matrix[r])))
        print("-" * (self.cols * 2))

    def display_word_as_string(self, word_list, label=""):
        """Выводит слово (список битов) в виде строки."""
        if label:
            print(f"{label}: {''.join(map(str, word_list))}")
        else:
            print(''.join(map(str, word_list)))

    # --- Операции со словами и столбцами ---
    def read_word(self, word_idx):
        """Считывает слово Sj (word_idx) из матрицы."""
        if not (0 <= word_idx < self.cols):
            raise ValueError(f"Индекс слова {word_idx} вне диапазона (0-{self.cols - 1}).")

        word_data = [0] * self.rows
        for bit_idx_in_word in range(self.rows):
            matrix_row = (bit_idx_in_word + word_idx) % self.rows
            matrix_col = word_idx
            word_data[bit_idx_in_word] = self.matrix[matrix_row][matrix_col]
        return word_data

    def write_word(self, word_idx, word_data_list):
        """Записывает word_data_list в слово Sj (word_idx) в матрице."""
        if not (0 <= word_idx < self.cols):
            raise ValueError(f"Индекс слова {word_idx} вне диапазона (0-{self.cols - 1}).")
        if len(word_data_list) != self.rows:
            raise ValueError(f"Данные слова должны содержать {self.rows} бит.")

        for bit_idx_in_word in range(self.rows):
            matrix_row = (bit_idx_in_word + word_idx) % self.rows
            matrix_col = word_idx
            self.matrix[matrix_row][matrix_col] = word_data_list[bit_idx_in_word]
        print(f"Слово S{word_idx} успешно записано.")

    def read_address_column_diagonal(self, start_row_idx_k):
        """
        Считывает "адресный столбец #k" (диагональный) из матрицы.
        start_row_idx_k - это 'k' из "адресный столбец #k",
        соответствует начальной строке диагонали.
        """
        if not (0 <= start_row_idx_k < self.rows):
            raise ValueError(
                f"Индекс адресного столбца (начальная строка) {start_row_idx_k} вне диапазона (0-{self.rows - 1}).")

        column_data = [0] * self.cols
        for c in range(self.cols):  # итерация по физическим столбцам
            matrix_row = (start_row_idx_k + c) % self.rows
            column_data[c] = self.matrix[matrix_row][c]
        return column_data

    def write_address_column_diagonal(self, start_row_idx_k, column_data_list):
        """
        Записывает column_data_list в "адресный столбец #k" (диагональный).
        start_row_idx_k - это 'k' из "адресный столбец #k".
        """
        if not (0 <= start_row_idx_k < self.rows):
            raise ValueError(
                f"Индекс адресного столбца (начальная строка) {start_row_idx_k} вне диапазона (0-{self.rows - 1}).")
        if len(column_data_list) != self.cols:
            raise ValueError(f"Данные для адресного столбца должны содержать {self.cols} бит.")

        for c in range(self.cols):  # итерация по физическим столбцам
            matrix_row = (start_row_idx_k + c) % self.rows
            self.matrix[matrix_row][c] = column_data_list[c]
        print(f"Адресный столбец #{start_row_idx_k} успешно записан.")

    # --- Логические функции ---
    def _logical_f0(self, b1, b2):
        return 0

    def _logical_f5(self, b1, b2):
        return b2

    def _logical_f10(self, b1, b2):
        return 1 - b2

    def _logical_f15(self, b1, b2):
        return 1

    def apply_logical_func(self, func_name, word1_idx, word2_idx, result_word_idx):
        """
        Применяет побитовую логическую функцию к word1 и word2, сохраняя результат в result_word.
        func_name может быть 'f0', 'f5', 'f10', 'f15'.
        """
        s1 = self.read_word(word1_idx)
        s2 = self.read_word(word2_idx)
        result_word = [0] * self.rows

        log_func = None
        if func_name == 'f0':
            log_func = self._logical_f0
        elif func_name == 'f5':
            log_func = self._logical_f5
        elif func_name == 'f10':
            log_func = self._logical_f10
        elif func_name == 'f15':
            log_func = self._logical_f15
        else:
            raise ValueError(f"Неизвестная логическая функция: {func_name}")

        for i in range(self.rows):
            result_word[i] = log_func(s1[i], s2[i])

        self.write_word(result_word_idx, result_word)
        self.display_word_as_string(result_word,
                                    f"Результат {func_name}(S{word1_idx}, S{word2_idx}) записан в S{result_word_idx}")

    # --- Поиск по соответствию ---
    def search_by_correspondence(self, search_argument_list):
        """
        Находит слова с максимальным количеством совпадающих битов с search_argument_list.
        Возвращает список индексов слов с наилучшими совпадениями.
        """
        if len(search_argument_list) != self.rows:
            raise ValueError(f"Аргумент поиска должен содержать {self.rows} бит.")

        self.display_word_as_string(search_argument_list, "Поиск соответствия с аргументом")

        match_counts = []
        for j in range(self.cols):
            word_sj = self.read_word(j)
            count = 0
            for i in range(self.rows):
                if word_sj[i] == search_argument_list[i]:
                    count += 1
            match_counts.append({'word_index': j, 'count': count})

        if not match_counts:
            print("В памяти нет слов для поиска.")
            return []

        max_count = -1
        for item in match_counts:
            if item['count'] > max_count:
                max_count = item['count']

        best_matches_indices = []
        print(f"\nМаксимальное количество совпадений: {max_count}")
        print("Слова с максимальным соответствием:")
        for item in match_counts:
            if item['count'] == max_count:
                best_matches_indices.append(item['word_index'])
                self.display_word_as_string(self.read_word(item['word_index']), f"S{item['word_index']}")

        if not best_matches_indices:
            print("Совпадений не найдено.")
        return best_matches_indices

    def search_by_correspondence_with_g_l(self, search_argument_list):
        """
        Находит слова, совпадающие с search_argument_list, с использованием g и l переменных.
        Поддерживает маскирование (-1 в аргументе означает 'любой бит').
        Возвращает список индексов слов, полностью совпадающих с аргументом.
        """
        if len(search_argument_list) != self.rows:
            raise ValueError(f"Аргумент поиска должен содержать {self.rows} бит.")

        self.display_word_as_string(search_argument_list, "Поиск соответствия с аргументом")

        n = self.rows  # Длина слова (16)
        matches = []

        # Инициализация g и l для каждого слова
        g = [0] * self.cols  # g_{j,n+1} = 0 (слово не больше аргумента)
        l = [0] * self.cols  # l_{j,n+1} = 0 (слово не меньше аргумента)

        # Поразрядное сравнение, начиная со старшего разряда
        for i in range(n - 1, -1, -1):  # От n-1 до 0
            new_g = [0] * self.cols
            new_l = [0] * self.cols
            for j in range(self.cols):
                word = self.read_word(j)  # Получаем слово с учетом диагональной адресации
                a_i = search_argument_list[i]  # i-й бит аргумента поиска
                s_ji = word[i]  # i-й бит j-го слова

                # Если бит аргумента -1 (маска), пропускаем сравнение
                if a_i == -1:
                    new_g[j] = g[j]
                    new_l[j] = l[j]
                else:
                    # Проверяем совпадение: если s_ji != a_i, слово не совпадает
                    if s_ji != a_i:
                        # Устанавливаем g или l в 1, чтобы исключить слово из совпадений
                        if s_ji > a_i:
                            new_g[j] = 1  # s_ji > a_i, слово больше
                        else:
                            new_l[j] = 1  # s_ji < a_i, слово меньше
                    else:
                        # Биты совпадают, сохраняем предыдущие значения
                        new_g[j] = g[j]
                        new_l[j] = l[j]

            g = new_g
            l = new_l

        # Проверяем, какие слова совпадают (g_{j0} = l_{j0} = 0)
        print("\nСлова, соответствующие аргументу поиска:")
        for j in range(self.cols):
            if g[j] == 0 and l[j] == 0:
                matches.append(j)
                self.display_word_as_string(self.read_word(j), f"S{j}")

        if not matches:
            print("Совпадений не найдено.")

        return matches

    # --- Арифметические операции ---
    def _bin_list_to_int(self, bin_list):
        return int("".join(map(str, bin_list)), 2)

    def _int_to_bin_list(self, num, bits):
        val = bin(num)[2:].zfill(bits)
        if len(val) > bits:  # Обработка переполнения, если число не помещается в bits
            val = val[-bits:]
        return [int(b) for b in val]

    def arithmetic_sum_fields(self, key_v_list):
        """
        Выполняет суммирование полей V(3)A(4)B(4)S(5).
        Складывает A и B, сохраняет в S для слов, где V совпадает с key_V.
        """
        if len(key_v_list) != 3:
            raise ValueError("Ключ V должен состоять из 3 бит.")
        self.display_word_as_string(key_v_list, "Выполнение арифметической суммы для V_ключа")

        modified_words_count = 0
        for j in range(self.cols):
            word_sj = self.read_word(j)

            v_sj = word_sj[0:3]

            if v_sj == key_v_list:
                print(f"\nСлово S{j} совпадает с ключом V: {''.join(map(str, word_sj))}")
                a_sj_list = word_sj[3:7]
                b_sj_list = word_sj[7:11]

                a_val = self._bin_list_to_int(a_sj_list)
                b_val = self._bin_list_to_int(b_sj_list)

                sum_val = a_val + b_val

                sum_s_list = self._int_to_bin_list(sum_val, 5)

                self.display_word_as_string(a_sj_list, f"  Поле A (биты 3-6) = {a_val}")
                self.display_word_as_string(b_sj_list, f"  Поле B (биты 7-10) = {b_val}")
                print(f"  Сумма (A+B) = {sum_val}")
                self.display_word_as_string(sum_s_list, "  Новое Поле S (биты 11-15)")

                new_word_sj = v_sj + a_sj_list + b_sj_list + sum_s_list
                self.write_word(j, new_word_sj)
                self.display_word_as_string(new_word_sj, f"  Обновленное S{j}")
                modified_words_count += 1

        if modified_words_count == 0:
            print(f"Не найдено слов, совпадающих с V_ключом: {''.join(map(str, key_v_list))}")
        else:
            print(f"\nОперация арифметической суммы полей завершена. {modified_words_count} слов(о) изменено.")


# --- Пример данных из документа ---
example_matrix_data_str = """
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0
1,1,0,1,1,0,0,0,1,1,1,1,0,0,0,0
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
1,1,1,0,1,0,0,0,0,0,0,1,0,0,0,0
0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0
0,0,1,0,1,1,0,0,0,0,0,1,1,0,0,0
0,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0
0,0,0,0,0,1,1,0,1,0,1,0,1,0,0,0
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1
0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0
0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0
0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,1
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
"""

# --- Основное выполнение программы и меню ---
if __name__ == "__main__":
    ap = AssociativeProcessorDiagonal()

    while True:
        print("\nСимуляция ассоциативного процессора (Вариант 4)")
        print("-------------------------------------------")
        print("1. Инициализировать матрицу из примера")
        print("2. Инициализировать матрицу случайными данными")
        print("3. Показать матрицу")
        print("4. Считать слово Sj")
        print("5. Записать слово Sj")
        print("6. Считать адресный столбец #k (диагональный)")
        print("7. Записать адресный столбец #k (диагональный)")
        print("8. Применить логическую функцию (f0, f5, f10, f15)")
        print("9. Поиск по соответствию")
        print("10. Арифметическая сумма полей (VABS)")
        print("0. Выход")

        choice = input("Введите ваш выбор: ")

        try:
            if choice == '1':
                ap.initialize_matrix_from_data(example_matrix_data_str)
            elif choice == '2':
                ap.generate_random_matrix()
            elif choice == '3':
                ap.display_matrix()
            elif choice == '4':
                idx = int(input("Введите индекс слова Sj (0-15): "))
                word = ap.read_word(idx)
                ap.display_word_as_string(word, f"S{idx}")
            elif choice == '5':
                idx = int(input("Введите индекс слова Sj (0-15) для записи: "))
                data_str = input(f"Введите 16 бит для S{idx} (например, 1010...): ")
                data_list = [int(b) for b in data_str]
                if len(data_list) != 16: raise ValueError("Должно быть 16 бит.")
                ap.write_word(idx, data_list)
            elif choice == '6':
                # k здесь - это индекс начальной строки для диагонального считывания
                k_idx = int(input("Введите индекс адресного столбца #k (0-15) для считывания: "))
                col = ap.read_address_column_diagonal(k_idx)
                ap.display_word_as_string(col, f"Адресный столбец #{k_idx}")
            elif choice == '7':
                k_idx = int(input("Введите индекс адресного столбца #k (0-15) для записи: "))
                data_str = input(f"Введите 16 бит для адресного столбца #{k_idx} (например, 1010...): ")
                data_list = [int(b) for b in data_str]
                if len(data_list) != 16: raise ValueError("Должно быть 16 бит.")
                ap.write_address_column_diagonal(k_idx, data_list)
            elif choice == '8':
                func = input("Введите функцию (f0, f5, f10, f15): ").lower()
                w1_idx = int(input("Введите индекс первого слова S_операнд1 (0-15): "))
                w2_idx = int(input("Введите индекс второго слова S_операнд2 (0-15): "))
                res_idx = int(input("Введите индекс слова для результата S_результат (0-15): "))
                ap.apply_logical_func(func, w1_idx, w2_idx, res_idx)
            elif choice == '9':
                arg_str = input(
                    "Введите 16-битный аргумент поиска (16 символов: 0, 1 или -, например, 111-------------): ")
                if len(arg_str) != 16:
                    raise ValueError("Должно быть 16 символов (0, 1 или -).")
                arg_list = [int(b) if b in ['0', '1'] else -1 for b in arg_str]
                print(f"arg_list: {arg_list}")
                if len(arg_list) != 16:
                    raise ValueError("Должно быть 16 бит.")
                ap.search_by_correspondence_with_g_l(arg_list)
            elif choice == '10':
                key_str = input("Введите 3-битный V_ключ (например, 101): ")
                key_list = [int(b) for b in key_str]
                if len(key_list) != 3: raise ValueError("Должно быть 3 бита.")
                ap.arithmetic_sum_fields(key_list)
            elif choice == '0':
                print("Выход.")
                break
            else:
                print("Неверный выбор. Пожалуйста, попробуйте снова.")

        except ValueError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")