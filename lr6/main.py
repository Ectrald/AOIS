class HashTable:
    def __init__(self, size=20):
        """Инициализация хеш-таблицы"""
        self.size = size
        self.table = [None] * size
        self.flags = {
            'C': [0] * size,  # Флажок коллизий
            'U': [0] * size,  # Флажок "занято"
            'T': [0] * size,  # Терминальный флажок
            'L': [0] * size,  # Флажок связи
            'D': [0] * size  # Флажок вычеркивания
        }
        self.P0 = [None] * size  # Указатель области переполнения
        self.keys = [None] * size  # Ключевые слова (ID)
        self.data = [None] * size  # Данные (Pi)

    def hash_function(self, key):
        """Вычисление числового значения ключа и хеш-адреса"""
        alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        first_char = key[0].lower()
        second_char = key[1].lower() if len(key) > 1 else 'а'

        try:
            v1 = alphabet.index(first_char)
            v2 = alphabet.index(second_char)
        except ValueError:
            v1 = ord(first_char) % 33
            v2 = ord(second_char) % 33

        V = v1 * 33 + v2
        h = V % self.size
        return V, h

    def quadratic_probing(self, h, i):
        """Квадратичный поиск для разрешения коллизий"""
        return (h + i ** 2) % self.size

    def insert(self, key, data):
        """Вставка новой записи в хеш-таблицу"""
        V, h = self.hash_function(key)

        # Проверка, есть ли уже такой ключ в таблице
        existing = self.search(key)
        if existing is not None:
            print(f"Ключ '{key}' уже существует в таблице")
            return False

        # Поиск свободного места с помощью квадратичного пробинга
        index = h
        collision_occurred = False
        prev_index = None
        visited = set()
        i = 0

        while i < self.size:
            index = self.quadratic_probing(h, i)
            if index in visited:
                break
            visited.add(index)

            # Если ячейка свободна или удалена, используем её
            if self.flags['U'][index] == 0 or self.flags['D'][index] == 1:
                break

            collision_occurred = True
            prev_index = index
            i += 1

        # Если не нашли свободного места
        if i >= self.size and self.flags['U'][index] == 1 and self.flags['D'][index] == 0:
            # Проверяем, есть ли удаленные ячейки в таблице
            for j in range(self.size):
                if self.flags['D'][j] == 1 or self.flags['U'][j] == 0:
                    index = j
                    break
            else:
                print("Хеш-таблица заполнена")
                return False

        # Заполняем ячейку
        self.keys[index] = key
        self.data[index] = data
        self.flags['U'][index] = 1
        self.flags['D'][index] = 0
        self.flags['T'][index] = 1  # Новая ячейка всегда терминальная

        # Обновляем флажки и указатели
        if collision_occurred and prev_index is not None:
            self.flags['C'][h] = 1  # Устанавливаем флажок коллизии
            self.P0[prev_index] = index  # Связываем с предыдущей ячейкой
            self.flags['T'][prev_index] = 0  # Предыдущая ячейка не терминальная
        self.P0[index] = index  # Новая ячейка указывает на себя

        print(f"Добавлено: '{key}' -> '{data}' по индексу {index}")
        return True

    def search(self, key):
        """Поиск записи по ключу"""
        V, h = self.hash_function(key)
        index = h
        visited = set()

        for i in range(self.size):
            index = self.quadratic_probing(h, i)
            if index in visited:
                break
            visited.add(index)

            # Если ячейка свободна и не была удалена
            if self.flags['U'][index] == 0 and self.flags['D'][index] == 0:
                return None

            # Если ячейка занята, не удалена и ключ совпадает
            if (self.flags['U'][index] == 1 and self.flags['D'][index] == 0 and
                    self.keys[index] == key):
                return {
                    'index': index,
                    'key': self.keys[index],
                    'data': self.data[index],
                    'flags': {k: self.flags[k][index] for k in self.flags},
                    'P0': self.P0[index]
                }

        # Если есть коллизия, продолжаем поиск по цепочке P0
        if self.flags['C'][h] == 1:
            index = h
            visited = set()
            while index is not None and index not in visited:
                visited.add(index)
                if (self.flags['U'][index] == 1 and self.flags['D'][index] == 0 and
                        self.keys[index] == key):
                    return {
                        'index': index,
                        'key': self.keys[index],
                        'data': self.data[index],
                        'flags': {k: self.flags[k][index] for k in self.flags},
                        'P0': self.P0[index]
                    }
                index = self.P0[index] if self.P0[index] is not None else None

        return None

    def delete(self, key):
        """Удаление записи по ключу"""
        found = self.search(key)
        if found is None:
            print(f"Ключ '{key}' не найден")
            return False

        index = found['index']
        h = self.hash_function(key)[1]

        # Устанавливаем флажок вычеркивания
        self.flags['D'][index] = 1
        self.flags['U'][index] = 0

        # Если это одиночная запись
        if found['flags']['T'] == 1 and self.P0[index] == index:
            print(f"Удалена одиночная запись '{key}' по индексу {index}")
            return True

        # Если есть коллизия, обновляем цепочку
        if self.flags['C'][h] == 1:
            prev_index = None
            curr_index = h
            visited = set()

            # Находим предыдущую запись в цепочке
            while curr_index is not None and curr_index not in visited:
                if self.P0[curr_index] == index:
                    prev_index = curr_index
                    break
                visited.add(curr_index)
                curr_index = self.P0[curr_index]

            next_index = self.P0[index]

            if prev_index is not None:
                # Связываем предыдущую запись с следующей
                self.P0[prev_index] = next_index
                if next_index is None or next_index == index:
                    self.flags['T'][prev_index] = 1
                print(f"Удалена запись '{key}' по индексу {index}, обновлена цепочка")
            else:
                # Это первая запись в цепочке
                if next_index is not None and next_index != index:
                    # Копируем следующую запись на место текущей
                    self.keys[index] = self.keys[next_index]
                    self.data[index] = self.data[next_index]
                    for k in self.flags:
                        self.flags[k][index] = self.flags[k][next_index]
                    self.P0[index] = self.P0[next_index]
                    self.flags['U'][index] = 1
                    self.flags['D'][index] = 0

                    # Освобождаем следующую ячейку
                    self.flags['U'][next_index] = 0
                    self.flags['D'][next_index] = 1
                    print(f"Удалена первая запись в цепочке '{key}', заменена записью из индекса {next_index}")
                else:
                    self.flags['C'][h] = 0  # Нет больше коллизий
                    print(f"Удалена последняя запись в цепочке '{key}' по индексу {index}")

        return True

    def display(self):
        """Отображение содержимого хеш-таблицы"""
        print("\nХеш-таблица:")
        print("Индекс\tКлюч\t\tДанные\t\tU\tC\tT\tL\tD\tP0")
        for i in range(self.size):
            key = self.keys[i] if self.keys[i] is not None else "None"
            data = self.data[i] if self.data[i] is not None else "None"
            p0 = self.P0[i] if self.P0[i] is not None else "None"

            print(f"{i}\t{key[:10]:<10}\t{data[:10]:<10}\t"
                  f"{self.flags['U'][i]}\t{self.flags['C'][i]}\t"
                  f"{self.flags['T'][i]}\t{self.flags['L'][i]}\t"
                  f"{self.flags['D'][i]}\t{p0}")

        filled = sum(1 for u in self.flags['U'] if u == 1)
        load_factor = filled / self.size
        print(f"\nКоэффициент заполнения: {load_factor:.2f}")