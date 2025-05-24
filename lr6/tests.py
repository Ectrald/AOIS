import unittest
from main import HashTable


class TestHashTable(unittest.TestCase):
    def setUp(self):
        self.ht = HashTable(size=20)

    def test_insert_and_search(self):
        """Тест вставки и поиска без коллизий."""
        self.ht.insert("алгебра", "Раздел математики")
        result = self.ht.search("алгебра")
        self.assertIsNotNone(result)
        self.assertEqual(result['key'], "алгебра")
        self.assertEqual(result['data'], "Раздел математики")

    def test_collision_handling(self):
        """Тест обработки коллизий."""
        # Создаем искусственную коллизию
        original_hash = self.ht.hash_function

        def forced_collision_hash(key):
            if key in ["коллизия1", "коллизия2"]:
                return (123, 5)  # Одинаковые V и h для обоих ключей
            return original_hash(key)

        self.ht.hash_function = forced_collision_hash

        # Вставляем два ключа с одинаковым хешем
        self.ht.insert("коллизия1", "Данные 1")
        self.ht.insert("коллизия2", "Данные 2")

        # Проверяем, что оба ключа добавлены
        self.assertIsNotNone(self.ht.search("коллизия1"))
        result = self.ht.search("коллизия2")
        self.assertIsNotNone(result)
        self.assertEqual(result['key'], "коллизия2")

        # Проверяем флаги коллизии
        self.assertEqual(self.ht.flags['C'][5], 1)

        # Восстанавливаем оригинальную хеш-функцию
        self.ht.hash_function = original_hash

    def test_delete(self):
        """Тест удаления записи."""
        self.ht.insert("алгебра", "Раздел математики")
        self.assertTrue(self.ht.delete("алгебра"))
        self.assertIsNone(self.ht.search("алгебра"))
        # Проверяем, что ячейка помечена как удаленная
        V, h = self.ht.hash_function("алгебра")
        self.assertEqual(self.ht.flags['D'][h], 1)

    def test_delete_with_collision(self):
        """Тест удаления записи с коллизией."""
        # Создаем искусственную коллизию
        original_hash = self.ht.hash_function

        def forced_collision_hash(key):
            if key in ["коллизия1", "коллизия2"]:
                return (123, 5)
            return original_hash(key)

        self.ht.hash_function = forced_collision_hash

        # Вставляем два ключа с коллизией
        self.ht.insert("коллизия1", "Данные 1")
        self.ht.insert("коллизия2", "Данные 2")

        # Удаляем первый ключ
        self.assertTrue(self.ht.delete("коллизия1"))
        self.assertIsNone(self.ht.search("коллизия1"))

        # Проверяем, что второй ключ остался
        result = self.ht.search("коллизия2")
        self.assertIsNotNone(result)
        self.assertEqual(result['key'], "коллизия2")

        # Восстанавливаем оригинальную хеш-функцию
        self.ht.hash_function = original_hash

    def test_insert_duplicate(self):
        """Тест вставки дубликата."""
        self.ht.insert("алгебра", "Раздел математики")
        self.assertFalse(self.ht.insert("алгебра", "Новое определение"))
        # Проверяем, что данные не изменились
        result = self.ht.search("алгебра")
        self.assertEqual(result['data'], "Раздел математики")

    def test_load_factor(self):
        """Тест коэффициента заполнения."""
        self.assertEqual(sum(self.ht.flags['U']), 0)
        self.ht.insert("алгебра", "Раздел математики")
        self.assertEqual(sum(self.ht.flags['U']), 1)
        # Проверяем после удаления
        self.ht.delete("алгебра")
        self.assertEqual(sum(self.ht.flags['U']), 0)

    def test_display(self):
        """Тест отображения таблицы."""
        self.ht.insert("алгебра", "Раздел математики")
        self.ht.insert("геометрия", "Раздел о пространстве")
        # Просто проверяем, что метод выполняется без ошибок
        try:
            self.ht.display()
        except Exception as e:
            self.fail(f"display() raised {type(e).__name__} unexpectedly!")

    def test_empty_table_operations(self):
        """Тест операций с пустой таблицей."""
        self.assertIsNone(self.ht.search("несуществующий"))
        self.assertFalse(self.ht.delete("несуществующий"))

    def test_hash_function(self):
        """Тест хеш-функции с разными типами ключей."""
        # Русские слова
        V, h = self.ht.hash_function("тест")
        self.assertIsInstance(V, int)
        self.assertIsInstance(h, int)

        # Короткие ключи
        V, h = self.ht.hash_function("я")
        self.assertIsInstance(V, int)

        # Английские буквы
        V, h = self.ht.hash_function("test")
        self.assertIsInstance(V, int)

        # Цифры
        V, h = self.ht.hash_function("123")
        self.assertIsInstance(V, int)

    def test_full_table(self):
        """Тест заполнения таблицы до предела."""
        # Уменьшаем размер таблицы для теста
        small_ht = HashTable(size=3)
        self.assertTrue(small_ht.insert("ключ0", "значение0"))
        self.assertTrue(small_ht.insert("ключ1", "значение1"))
        self.assertTrue(small_ht.insert("ключ2", "значение2"))

        # Попытка вставить в заполненную таблицу
        self.assertTrue(small_ht.insert("лишний", "не поместится"))

    def test_quadratic_probing(self):
        """Тест квадратичного пробинга."""
        # Для теста используем таблицу большего размера
        indices = set()
        for i in range(5):  # Проверяем первые 5 проб
            index = self.ht.quadratic_probing(0, i)
            indices.add(index)

        # Проверяем, что все индексы уникальны
        self.assertEqual(len(indices), 5)

    def test_flag_operations(self):
        """Тест работы с флагами."""
        self.ht.insert("флаг", "тест")
        V, h = self.ht.hash_function("флаг")

        # Проверяем установку флагов
        self.assertEqual(self.ht.flags['U'][h], 1)
        self.assertEqual(self.ht.flags['T'][h], 1)
        self.assertEqual(self.ht.flags['D'][h], 0)

        # Проверяем сброс флагов при удалении
        self.ht.delete("флаг")
        self.assertEqual(self.ht.flags['U'][h], 0)
        self.assertEqual(self.ht.flags['D'][h], 1)

    def test_pointer_operations(self):
        """Тест работы с указателями P0."""
        # Создаем искусственную коллизию
        original_hash = self.ht.hash_function

        def forced_collision_hash(key):
            if key in ["указ1", "указ2"]:
                return (123, 5)
            return original_hash(key)

        self.ht.hash_function = forced_collision_hash

        self.ht.insert("указ1", "данные1")
        self.ht.insert("указ2", "данные2")

        # Находим фактические индексы
        idx1 = None
        idx2 = None
        for i in range(self.ht.size):
            if self.ht.keys[i] == "указ1":
                idx1 = i
            elif self.ht.keys[i] == "указ2":
                idx2 = i

        self.assertIsNotNone(idx1)
        self.assertIsNotNone(idx2)

        # Проверяем указатели
        self.assertEqual(self.ht.P0[idx1], idx2)
        self.assertEqual(self.ht.P0[idx2], idx2)  # Терминальная

        self.ht.hash_function = original_hash

    def test_complex_collision_scenario(self):
        """Тест сложного сценария с несколькими коллизиями."""
        # Создаем искусственные коллизии
        original_hash = self.ht.hash_function

        def forced_collision_hash(key):
            if key.startswith("колл"):
                return (123, 5)
            return original_hash(key)

        self.ht.hash_function = forced_collision_hash

        # Вставляем 3 ключа с коллизией
        self.ht.insert("колл1", "данные1")
        self.ht.insert("колл2", "данные2")
        self.ht.insert("колл3", "данные3")

        # Находим фактические индексы
        idx1 = None
        idx2 = None
        idx3 = None
        for i in range(self.ht.size):
            if self.ht.keys[i] == "колл1":
                idx1 = i
            elif self.ht.keys[i] == "колл2":
                idx2 = i
            elif self.ht.keys[i] == "колл3":
                idx3 = i

        self.assertIsNotNone(idx1)
        self.assertIsNotNone(idx2)
        self.assertIsNotNone(idx3)

        # Проверяем цепочку
        self.assertEqual(self.ht.P0[idx1], idx2)
        self.assertEqual(self.ht.P0[idx2], idx3)
        self.assertEqual(self.ht.P0[idx3], idx3)  # Терминальная

        # Удаляем средний элемент
        self.assertTrue(self.ht.delete("колл2"))

        # Проверяем обновленную цепочку
        self.assertEqual(self.ht.P0[idx1], idx3)

        self.ht.hash_function = original_hash


if __name__ == '__main__':
    unittest.main()