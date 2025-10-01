class KnowledgeBase:
    def __init__(self):
        # Список організмів
        self.objects = set()
        # Зв’язки у форматі: {об’єкт: [(тип_зв’язку, інший_об’єкт), ...]}
        self.relations = {}

    def add_object(self, obj_name: str):
        """Додати новий об’єкт (організм)"""
        self.objects.add(obj_name)
        if obj_name not in self.relations:
            self.relations[obj_name] = []

    def add_relation(self, subj: str, relation: str, obj: str):
        """Додати новий зв’язок між об’єктами"""
        if subj not in self.objects:
            self.add_object(subj)
        if obj not in self.objects:
            self.add_object(obj)

        self.relations[subj].append((relation, obj))

    def get_objects(self):
        """Повернути список усіх об’єктів"""
        return list(self.objects)

    def get_relations(self, obj_name: str = None):
        """Повернути всі зв’язки або тільки для конкретного об’єкта"""
        if obj_name:
            return self.relations.get(obj_name, [])
        return self.relations

    def get_statistics(self):
        """Отримати статистику по базі знань"""
        num_objects = len(self.objects)
        num_relations = sum(len(v) for v in self.relations.values())

        # Які типи зв’язків використовуються
        relation_types = set()
        for rels in self.relations.values():
            for r, _ in rels:
                relation_types.add(r)

        return {
            "num_objects": num_objects,
            "num_relations": num_relations,
            "relation_types": list(relation_types)
        }
