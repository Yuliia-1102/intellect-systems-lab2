from createDB import createDB
from knowledgeBase import *
from connections import *

kb = KnowledgeBase()

createDB(kb)

finder = ConnectionFinder(kb)

path = finder.find_path("Хвіст", "Тигр")
print(path)

path2 = finder.find_path("Сад", "Корінь")
print(path2)

# Отримуємо список об’єктів
# print("Об’єкти:", kb.get_objects())
#
# # Отримуємо зв’язки певного об’єкта
# print("Зв’язки Dog:", kb.get_relations("Dog"))
#
# # Отримуємо всі зв’язки
# print("Всі зв’язки:", kb.get_relations())
#
# # Статистика
# print("Статистика:", kb.get_statistics())

