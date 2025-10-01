from collections import deque, defaultdict

class ConnectionPath:
    def __init__(self):
        self.steps = []
        self.found = False

    def add_step(self, from_obj, relation, to_obj):
        self.steps.append((from_obj, relation, to_obj))

    def set_found(self, status: bool):
        self.found = status

    def length(self):
        return len(self.steps)

    def __str__(self):
        if not self.found:
            return "Зв’язок не знайдено."
        path_str = " → ".join([f"{a} -[{r}]-> {b}" for a, r, b in self.steps])
        return f"Знайдено шлях ({self.length()} кроків): {path_str}"

class ConnectionFinder:
    """
    BFS-пошук зв'язку з урахуванням:
    1) Успадкування is_habitat_of/part_of від предків суб'єкта (subject-side).
    2) Спеціалізації part_of по об'єкту (цілому) вниз до нащадків.
    3) Формування ПРОМІЖНИХ КРОКІВ у шляху для спеціалізованих part_of:
       (A part_of T) + (T is_a D) => шлях: A -[part_of]-> T -> ... -> D.
    """
    INHERITED_SUBJECT_RELS = {"is_habitat_of", "part_of"}
    SPECIALIZE_OBJECT_RELS = {"part_of", "is_habitat_of"}

    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self._parents = defaultdict(set)   # child -> {parents} (зберігає батьків для кожної дитини)
        self._children = defaultdict(set)  # parent -> {children} (зберігає дітей для кожного батька)
        self._built_taxonomy = False

    def find_path(self, start, target):
        self._ensure_taxonomy()

        visited = set()
        # Кожен елемент черги: (current_node, path_steps_so_far), де path_steps_so_far — список кроків (from, rel, to)
        queue = deque([(start, [])])

        while queue:
            current, path = queue.popleft()
            if current == target:
                conn = ConnectionPath()
                for step in path:
                    conn.add_step(*step)
                conn.set_found(True)
                return conn

            if current in visited:
                continue
            visited.add(current)

            # Отримуємо ефективні ребра з current разом із пояснювальними кроками
            for rel, nbr, expl_steps in self._effective_relations_from_with_expl(current):
                # expl_steps — це вже послідовність кроків від 'current' до 'nbr' (для спеціалізації part_of містить проміжні кроки is_a)
                new_path = path + expl_steps
                queue.append((nbr, new_path))

        # не знайдено
        conn = ConnectionPath()
        conn.set_found(False)
        return conn

    def _ensure_taxonomy(self):
        if self._built_taxonomy:
            return
        for obj in self.kb.get_objects():
            for rel, parent in self.kb.get_relations(obj):
                if rel == "is_a":
                    self._parents[obj].add(parent)
                    self._children[parent].add(obj)
        self._built_taxonomy = True

    def _ancestors(self, node):
        self._ensure_taxonomy()
        res, stack = set(), [node]
        while stack:
            cur = stack.pop()
            for p in self._parents.get(cur, ()):
                if p not in res:
                    res.add(p)
                    stack.append(p)
        return res

    def _descendants(self, node):
        self._ensure_taxonomy()
        res, stack = set(), [node]
        while stack:
            cur = stack.pop()
            for ch in self._children.get(cur, ()):
                if ch not in res:
                    res.add(ch)
                    stack.append(ch)
        return res

    def _down_is_a_path_nodes(self, ancestor, descendant):
        """
        Знайти шлях вузлів ancestor -> ... -> descendant,
        рухаючись ВНИЗ по таксономії (через _children).
        Повертає список вузлів [ancestor, ..., descendant] або [] якщо шляху немає.
        """
        if ancestor == descendant:
            return [ancestor]
        q = deque([ancestor])
        prev = {ancestor: None}
        while q:
            v = q.popleft()
            for ch in self._children.get(v, ()):
                if ch not in prev:
                    prev[ch] = v
                    if ch == descendant:
                        # відновити шлях
                        path = [ch]
                        while path[-1] is not None:
                            p = prev[path[-1]]
                            if p is None:
                                break
                            path.append(p)
                        path.reverse()
                        return path
                    q.append(ch)
        return []

    def _effective_relations_from_with_expl(self, node):
        """
        Повертає список кортежів (rel, neighbor, expl_steps), де:
        - rel, neighbor — "ефективне" ребро з урахуванням успадкування/спеціалізації;
        - expl_steps — послідовність кроків (from, rel, to), яка ПОВНІСТЮ
          описує перехід від node до neighbor. Для спеціалізованих part_of
          містить проміжні кроки is_a.
        """
        # [("part_of", "Судинна")]
        base_edges = list(self.kb.get_relations(node))
        # ("part_of", "Судинна", [("Листок", "part_of", "Судинна")])
        explained = [(rel, obj, [(node, rel, obj)]) for (rel, obj) in base_edges]

        # 2) Успадковані від предків суб'єкта (тільки обрані типи)
        for anc in self._ancestors(node):
            for rel, obj in self.kb.get_relations(anc):
                if rel in self.INHERITED_SUBJECT_RELS:
                    # Перевірити винятки:
                    if not self.kb.has_exception(node, rel, obj):
                        explained.append((rel, obj, [(node, rel, obj)]))

        # 3) Спеціалізація вниз по ОБ'ЄКТУ для part_of:
        #    (node -[part_of]-> T) => також (node -[part_of]-> D) для кожного нащадка D T,
        #    а пояснення включає (node -[part_of]-> T) + (T -[is_a]-> ... -> D)
        specialized = []
        for rel, obj, expl in explained:
            specialized.append((rel, obj, expl))  # зберігаємо оригінал
            if rel in self.SPECIALIZE_OBJECT_RELS:
                for d in self._descendants(obj):
                    # Перевірка винятку для спеціалізованого зв'язку
                    if not self.kb.has_exception(node, rel, d):
                        nodes_path = self._down_is_a_path_nodes(obj, d)
                        if not nodes_path or len(nodes_path) < 2:
                            continue
                        sp_expl = [(node, rel, obj)]
                        for i in range(len(nodes_path) - 1):
                            a, b = nodes_path[i], nodes_path[i + 1]
                            sp_expl.append((b, "is_a", a))
                        specialized.append((rel, d, sp_expl))

        # 4) Унікалізація: якщо є кілька шляхів до того самого (rel, neighbor),
        #    залишаємо найкоротше пояснення (мінімум кроків).
        best = {}
        for rel, nb, expl in specialized:
            key = (rel, nb)
            if key not in best or len(expl) < len(best[key]):
                best[key] = expl

        # Повертаємо у потрібному форматі
        out = []
        for (rel, nb), expl in best.items():
            out.append((rel, nb, expl))
        return out