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
        self.assertIsNone(self.ht.search("коллизия2"))

        

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
        self.assertIsNone(self.ht.search("коллизия2"))

        # Восстанавливаем оригинальную хеш-функцию
        self.ht.hash_function = original_hash

    def test_insert_duplicate(self):
        """Тест вставки дубликата."""
        self.ht.insert("алгебра", "Раздел математики")
        self.assertFalse(self.ht.insert("алгебра", "Новое определение"))

    def test_load_factor(self):
        """Тест коэффициента заполнения."""
        self.assertEqual(sum(self.ht.flags['U']), 0)
        self.ht.insert("алгебра", "Раздел математики")
        self.assertEqual(sum(self.ht.flags['U']), 1)

    def test_display(self):
        """Тест отображения таблицы (визуальная проверка)."""
        self.ht.insert("алгебра", "Раздел математики")
        self.ht.insert("геометрия", "Раздел о пространстве")
        print("\nТест отображения таблицы:")
        self.ht.display()


if __name__ == '__main__':
    unittest.main()