import json
import re


class DirectedGraph:
    def __init__(self, file_path):
        self.file_path = file_path
        self.graph = {}
        self.error_file = "error_" + file_path
        self.first_error_log = True  # Флаг для перезаписи файла при первом вызове
        self.load_graph()

    def log_error(self, message):
        # Перезаписываем файл при первом вызове, затем добавляем новые записи
        mode = 'w' if self.first_error_log else 'a'
        with open(self.error_file, mode, encoding='utf-8') as error_file:
            error_file.write(message + "\n")
        self.first_error_log = False  # Меняем режим на добавление после первого вызова

    def load_graph(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = file.read().strip()  # Считываем весь файл одной строкой
                data = data[1:-1]  # Убираем первую и последнюю скобки
                edges = data.split('), (')  # Разбиваем на отдельные рёбра

                for line_number, edge in enumerate(edges, start=1):
                    parts = [part.strip() for part in edge.split(',')]  # Разбиваем каждое ребро на части
                    if len(parts) != 3 or not all(parts):
                        error_message = f"Строка {line_number}: '({edge})'"
                        self.log_error(error_message + ' - не хватает данных')
                        continue  # Переходим к следующей строке

                    a, b, n = parts[0], parts[1], parts[2]

                    # Проверяем, что a и b являются числами, а n также должен быть числом, если присутствует
                    if not (a.isdigit() and b.isdigit() and (n.isdigit() or n == '-')):
                        error_message = f"Строка {line_number}: '({edge})'"
                        self.log_error(error_message + ' - некорректные данные')
                        continue

                    n = int(n) if n.isdigit() else None  # Преобразуем n в число, если возможно

                    # Проверяем существование вершин и добавляем в граф
                    if a not in self.graph:
                        self.graph[a] = []
                    if b not in self.graph and n is not None:
                        self.graph[b] = []

                    # Добавляем дугу, если n не None
                    if n is not None:
                        self.graph[a].append((b, n))

                # Сортировка исходящих дуг по порядковому номеру для каждой вершины
                for node, edges in self.graph.items():
                    self.graph[node] = sorted(edges, key=lambda x: x[1])

        except FileNotFoundError:
            self.log_error(f"Файл {self.file_path} не найден.")
        except Exception as e:
            self.log_error(f"Произошла непредвиденная ошибка: {e}")

    def save_graph_as_json(self, output_file):
        # Преобразуем граф в словарь для записи в JSON
        graph_dict = {node: edges for node, edges in self.graph.items()}

        try:
            # Создаем компактный JSON без лишних отступов для вложенных списков
            compact_json = json.dumps(graph_dict, ensure_ascii=False)

            # Добавляем отступы на верхнем уровне вручную
            formatted_json = (
                compact_json
                .replace('], [', '],\n        [')  # Отступ между элементами верхнего уровня
                .replace(']], "', ']\n    ],\n    "')  # Перенос строки после завершения списка для ключа
                .replace('": [', '": [\n        ')  # Начало верхнего уровня с отступом
                .replace('}}', '\n}')  # Закрывающая скобка JSON
                .replace('{', '{\n    ')  # Начало JSON с отступом
            )

            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(formatted_json)

            print(f"Граф успешно сохранен в {output_file}")
        except Exception as e:
            self.log_error(f"Ошибка при сохранении графа в файл {output_file}: {e}")

    def has_cycle(self):
        visited = set()
        rec_stack = set()

        # обход в глубину
        def dfs(v):
            visited.add(v)
            rec_stack.add(v)

            for neighbor, _ in self.graph.get(v, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    print("Цикл обнаружен в графе.")
                    return True

            rec_stack.remove(v)
            return False

        # Запуск DFS для каждой компоненты связности
        for vertex in self.graph:
            if vertex not in visited:
                if dfs(vertex):
                    return True

        print("Циклы не обнаружены в графе.")
        return False

    def find_sink(self):
        for node, edges in self.graph.items():
            if not edges:
                return node
        return None

    def build_function(self, node):
        # Инициализация списка для хранения входящих рёбер
        incoming = []
        # Перебор всех рёбер графа
        for parent, edges in self.graph.items():
            # Перебор рёбер для каждой вершины
            for child, order in edges:
                # Если текущее ребро ведёт к искомой вершине
                if child == node:
                    # Добавляем исходящую вершину и порядок ребра в список входящих
                    incoming.append((parent, order))
        # Сортировка входящих рёбер по порядку
        incoming.sort(key=lambda x: x[1])

        # Если список входящих рёбер пуст, возвращаем текущую вершину
        if not incoming:
            return node

        # Рекурсивное построение функций для каждой исходящей вершины
        children = [self.build_function(parent) for parent, _ in incoming]
        # Формирование и возвращение строки вызова текущей вершины как функции от её детей
        return f"{node}({', '.join(children)})"

    def to_prefix_notation(self):
        sink = self.find_sink()
        if not sink:
            return "Невозможно построить функцию"
        return self.build_function(sink)

    def save_prefix_notation_to_file(self, file_path):
        with open(file_path, 'w') as file:
            notation = self.to_prefix_notation()
            file.write(notation)
            print(f"Результат сохранён в файл: {file_path}")

    def display_graph(self):
        # Вывод графа для проверки
        for node, edges in self.graph.items():
            print(f"Вершина {node}: {edges}")
