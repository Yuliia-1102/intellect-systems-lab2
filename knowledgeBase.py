class KnowledgeBase:
    def __init__(self):
        self.objects = set()
        self.relations = {} # Зв’язки у форматі: {об’єкт: [(тип_зв’язку, інший_об’єкт), ...]}
        self.exceptions = {} # {об'єкт: {тип_зв'язку: {заборонені_об'єкти, ..., ....}}}

    def add_object(self, obj_name: str):
        self.objects.add(obj_name)
        if obj_name not in self.relations:
            self.relations[obj_name] = []
        if obj_name not in self.exceptions:
            self.exceptions[obj_name] = {}

    def add_relation(self, subj: str, relation: str, obj: str):
        if subj not in self.objects:
            self.add_object(subj)
        if obj not in self.objects:
            self.add_object(obj)
        self.relations[subj].append((relation, obj)) # зв'язок між об'єктами

    def add_exception(self, obj_name: str, relation_type: str, forbidden_obj: str):
        if obj_name not in self.objects:
            self.add_object(obj_name)

        if relation_type not in self.exceptions[obj_name]:
            self.exceptions[obj_name][relation_type] = set()

        self.exceptions[obj_name][relation_type].add(forbidden_obj)

    def has_exception(self, obj_name: str, relation_type: str, target_obj: str) -> bool:
        """
        Перевіряє чи є виняток для даного зв'язку

        Returns:
            True якщо зв'язок заборонений (є виняток)
        """
        if obj_name not in self.exceptions:
            return False
        if relation_type not in self.exceptions[obj_name]:
            return False
        return target_obj in self.exceptions[obj_name][relation_type]

    def get_exceptions(self, obj_name: str = None): # повернути винятки для конкретного об'єкта або всі
        if obj_name:
            return self.exceptions.get(obj_name, {})
        return self.exceptions

    def get_objects(self):
        return list(self.objects) # всі додані об'єкти

    def get_relations(self, obj_name: str = None): # повернути всі зв’язки або тільки для конкретного об’єкта
        if obj_name:
            return self.relations.get(obj_name, [])
        return self.relations

    def get_statistics(self):
        num_objects = len(self.objects)
        num_relations = sum(len(v) for v in self.relations.values())
        num_exceptions = sum(
            sum(len(targets) for targets in exc.values())
            for exc in self.exceptions.values()
        )

        relation_types = set()
        for rels in self.relations.values():
            for r, _ in rels:
                relation_types.add(r)

        return {
            "num_objects": num_objects,
            "num_relations": num_relations,
            "num_exceptions": num_exceptions,
            "relation_types": list(relation_types)
        }