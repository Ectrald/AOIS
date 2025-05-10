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
        # Преобразуем ключ в числовое значение по первым двум буквам (русский алфавит)
        alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        first_char = key[0].lower()
        second_char = key[1].lower() if len(key) > 1 else 'а'

        try:
            v1 = alphabet.index(first_char)
            v2 = alphabet.index(second_char)
        except ValueError:
            # Если символы не найдены в алфавите (например, цифры или латинские буквы)
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
        last_index = None

        for i in range(self.size):
            index = self.quadratic_probing(h, i)

            if self.flags['U'][index] == 0 or self.flags['D'][index] == 1:
                # Нашли свободное место или удаленную ячейку
                break

            if not collision_occurred and i > 0:
                collision_occurred = True
                self.flags['C'][h] = 1  # Устанавливаем флажок коллизии для исходного адреса

            last_index = index

        # Если не нашли свободного места
        if self.flags['U'][index] == 1 and self.flags['D'][index] == 0:
            print("Хеш-таблица заполнена")
            return False

        # Заполняем ячейку
        self.keys[index] = key
        self.data[index] = data
        self.flags['U'][index] = 1
        self.flags['D'][index] = 0

        # Обновляем флажки и указатели
        if collision_occurred:
            # Если была коллизия, обновляем указатель P0 предыдущей ячейки
            self.P0[last_index] = index
            self.flags['T'][last_index] = 0  # Предыдущая ячейка больше не терминальная
            self.flags['T'][index] = 1  # Новая ячейка становится терминальной
        else:
            # Нет коллизии - это одиночная запись
            self.flags['T'][index] = 1
            self.P0[index] = index  # Указывает на себя

        print(f"Добавлено: '{key}' -> '{data}' по индексу {index}")
        return True

    def search(self, key):
        """Поиск записи по ключу"""
        V, h = self.hash_function(key)
        index = h

        for i in range(self.size):
            index = self.quadratic_probing(h, i)

            # Если ячейка свободна и не была удалена
            if self.flags['U'][index] == 0 and self.flags['D'][index] == 0:
                return None

            # Если ячейка занята и не удалена, и ключ совпадает
            if (self.flags['U'][index] == 1 and self.flags['D'][index] == 0 and
                    self.keys[index] == key):
                return {
                    'index': index,
                    'key': self.keys[index],
                    'data': self.data[index],
                    'flags': {k: self.flags[k][index] for k in self.flags},
                    'P0': self.P0[index]
                }

            # Если дошли до терминальной ячейки в цепочке
            if self.flags['T'][index] == 1:
                break

        return None

    def delete(self, key):
        """Удаление записи по ключу"""
        # Сначала находим запись
        found = self.search(key)
        if found is None:
            print(f"Ключ '{key}' не найден")
            return False

        index = found['index']
        h = self.hash_function(key)[1]

        # Устанавливаем флажок вычеркивания
        self.flags['D'][index] = 1

        # Анализируем тип записи
        if found['flags']['T'] == 1 and self.P0[index] == index:
            # Одиночная запись - просто освобождаем
            self.flags['U'][index] = 0
            print(f"Удалена одиночная запись '{key}' по индексу {index}")
        elif found['flags']['T'] == 1 and self.P0[index] != index:
            # Последняя в цепочке - находим предыдущую
            prev_index = None
            for i in range(self.size):
                current = self.quadratic_probing(h, i)
                if self.P0[current] == index:
                    prev_index = current
                    break

            if prev_index is not None:
                # Освобождаем текущую
                self.flags['U'][index] = 0
                # Делаем предыдущую терминальной
                self.flags['T'][prev_index] = 1
                self.P0[prev_index] = prev_index
                print(f"Удалена последняя запись в цепочке '{key}' по индексу {index}")
        elif found['flags']['T'] == 0 and self.P0[index] != index:
            # Промежуточная в цепочке - заменяем следующей
            next_index = self.P0[index]
            next_entry = {
                'key': self.keys[next_index],
                'data': self.data[next_index],
                'flags': {k: self.flags[k][next_index] for k in self.flags},
                'P0': self.P0[next_index]
            }

            # Копируем следующую запись на место текущей
            self.keys[index] = next_entry['key']
            self.data[index] = next_entry['data']
            for k in self.flags:
                self.flags[k][index] = next_entry['flags'][k]
            self.P0[index] = next_entry['P0']

            # Освобождаем следующую запись
            self.flags['U'][next_index] = 0
            print(f"Удалена промежуточная запись в цепочке '{key}', заменена записью из индекса {next_index}")
        elif found['flags']['T'] == 0 and found['flags']['C'] == 1:
            # Первая в цепочке с коллизией - заменяем следующей
            next_index = self.P0[index]
            next_entry = {
                'key': self.keys[next_index],
                'data': self.data[next_index],
                'flags': {k: self.flags[k][next_index] for k in self.flags},
                'P0': self.P0[next_index]
            }

            # Копируем следующую запись на место текущей
            self.keys[index] = next_entry['key']
            self.data[index] = next_entry['data']
            for k in self.flags:
                self.flags[k][index] = next_entry['flags'][k]
            self.P0[index] = next_entry['P0']

            # Освобождаем следующую запись
            self.flags['U'][next_index] = 0
            self.flags['C'][index] = 1  # Сохраняем флажок коллизии
            print(f"Удалена первая запись в цепочке с коллизией '{key}', заменена записью из индекса {next_index}")

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

        # Расчет коэффициента заполнения
        filled = sum(1 for u in self.flags['U'] if u == 1)
        load_factor = filled / self.size
        print(f"\nКоэффициент заполнения: {load_factor:.2f}")


# Пример использования
if __name__ == "__main__":
    # Создаем хеш-таблицу для математических терминов
    ht = HashTable()

    # Добавляем записи
    terms = [
        ("алгебра", "Раздел математики, изучающий операции и отношения"),
        ("геометрия", "Раздел математики, изучающий пространственные структуры"),
        ("анализ", "Раздел математики, изучающий функции и их свойства"),
        ("топология", "Раздел математики, изучающий свойства пространств"),
        ("логика", "Раздел математики, изучающий формальные системы"),
        ("комбинаторика", "Раздел математики, изучающий дискретные структуры"),
        ("теория чисел", "Раздел математики, изучающий свойства чисел"),
        ("дифференциал", "Основное понятие дифференциального исчисления"),
        ("интеграл", "Основное понятие интегрального исчисления"),
        ("матрица", "Прямоугольная таблица чисел"),
        ("вектор", "Элемент векторного пространства"),
        ("граф", "Совокупность вершин и ребер"),
        ("изоморфизм", "Взаимно однозначное соответствие"),
        ("гомоморфизм", "Отображение, сохраняющее структуру"),
        ("аксиома", "Исходное положение теории"),
        ("теорема", "Утверждение, требующее доказательства"),
        ("лемма", "Вспомогательное утверждение"),
        ("следствие", "Утверждение, выводимое из теоремы"),
        ("доказательство", "Логическое обоснование истинности"),
        ("контрпример", "Пример, опровергающий утверждение")
    ]

    # Вставляем только 15 записей из 20, чтобы были коллизии
    for i in range(15):
        ht.insert(*terms[i])

    # Выводим таблицу
    ht.display()

    # Поиск записи
    print("\nПоиск 'алгебра':")
    result = ht.search("алгебра")
    print(result)

    # Удаление записи
    print("\nУдаление 'геометрия':")
    ht.delete("геометрия")
    ht.display()

    # Попытка вставки существующего ключа
    print("\nПопытка вставить существующий ключ:")
    ht.insert("алгебра", "Новое определение")

    # Поиск удаленной записи
    print("\nПоиск удаленной 'геометрия':")
    print(ht.search("геометрия"))