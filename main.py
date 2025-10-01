from createDB import createDB
from knowledgeBase import *
from connections import *

kb = KnowledgeBase()
createDB(kb)

finder = ConnectionFinder(kb)

path = finder.find_path("Лева грива", "Тварина")
print(path)

path2 = finder.find_path("Листок", "Однодольна")
print(path2)

path3 = finder.find_path("Шерсть", "Наземний")
print(path3)

path4 = finder.find_path("Лапа", "Водний")
print(path4)

path5 = finder.find_path("Сад", "Троянда")
print(path5)

# print("Всі додані об’єкти:", kb.get_objects())

# print("Заборонені об'єкти:", kb.get_exceptions("Лапа"))
# print(kb.has_exception("Шерсть", "part_of", "Слон"))

# print("Зв’язки:", kb.get_relations("Шерсть"))

# print("Статистика:", kb.get_statistics())