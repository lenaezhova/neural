from helpers.file_handler import parse_args
from graph import DirectedGraph
import math
import re


def load_operations_from_file(operations_file):
    operations = {}
    try:
        with open(operations_file, 'r') as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()

                # Игнорируем строки с фигурными скобками
                if line == '{' or line == '}':
                    continue

                try:
                    # Разделяем строку по ':', чтобы получить имя и операцию
                    name, operation = line.split(':')
                    name = name.strip()
                    operation = operation.strip().rstrip(',')  # Убираем запятую в конце

                    # Если операция является числом, преобразуем её в float
                    if re.match(r"^-?\d+(\.\d+)?$", operation):  # Проверка на числовую константу
                        operation = float(operation)  # Преобразуем в число

                    operations[name] = operation
                except ValueError:
                    print(f"Ошибка в формате данных на строке {line_number}, строка пропущена")
    except FileNotFoundError:
        print(f"Файл не найден: {operations_file}")
    return operations


def save_result(output_file, result):
    with open(output_file, "w") as file:
        file.write(str(result))


class DirectedGraphWithOperations(DirectedGraph):
    def __init__(self, file_path, operations_file):
        super().__init__(file_path)
        self.operations = load_operations_from_file(operations_file)

    def to_prefix_with_operations(self):
        """
        Метод преобразует граф операций в префиксную запись, где каждая вершина представлена операцией
        или значением.
        """

        def dfs_with_operations(node):
            """
            Рекурсивный обход графа для построения выражения в префиксной записи.

            :param node: текущая вершина графа
            :return: строковое представление выражения для данной вершины
            """
            # Получаем операцию или значение для текущей вершины
            operation = self.operations.get(node, node)

            # Если операция числовая, возвращаем её как строку
            if isinstance(operation, (int, float)):
                return str(operation)

            # Получаем все входящие рёбра для текущей вершины
            incoming = []
            for parent, edges in self.graph.items():
                for child, order in edges:
                    if child == node:
                        incoming.append((parent, order))
            # Сортируем входящие рёбра по порядковому номеру (order)
            incoming.sort(key=lambda x: x[1])

            # Рекурсивно строим строковые выражения для всех входящих вершин
            children_str = [dfs_with_operations(parent) for parent, _ in incoming]

            # Формируем строку в зависимости от операции
            if operation == '+':
                # Суммируем значения дочерних вершин
                return f"({' + '.join(children_str)})"
            elif operation == '*':
                # Перемножаем значения дочерних вершин
                return f"({' * '.join(children_str)})"
            elif operation == 'exp':
                # Проверяем, что операция экспоненты имеет ровно один аргумент
                if len(children_str) != 1:
                    raise ValueError("Операция 'exp' должна иметь ровно один аргумент")
                return f"exp({children_str[0]})"
            else:
                # Если операция неизвестна, возвращаем её как строку
                return str(operation)

        # Находим вершину без исходящих рёбер (синк)
        sink = self.find_sink()
        if not sink:
            # Если синк не найден, выбрасываем исключение
            raise ValueError("Не удалось найти конечную вершину графа.")

        # Начинаем построение выражения с найденного синка
        return dfs_with_operations(sink)

    def evaluate_function(self):
        """
        Метод вычисляет значение функции, представленной графом операций.
        Обходит граф начиная с конечной вершины (синка) и применяет операции рекурсивно.
        """

        def evaluate(node):
            """
            Рекурсивное вычисление значения для указанной вершины графа.

            :param node: текущая вершина графа
            :return: результат вычисления для данной вершины
            """
            # Получаем операцию для данной вершины
            operation = self.operations.get(node)
            # Если операция не найдена, выбрасываем исключение
            if operation is None:
                raise ValueError(f"Операция для вершины {node} не найдена")

            # Если операция является числовой константой, возвращаем её значение
            if isinstance(operation, (int, float)):
                return operation

            # Инициализируем список для хранения входящих рёбер
            incoming = []
            # Перебираем все рёбра графа
            for parent, edges in self.graph.items():
                # Перебираем рёбра для текущей вершины
                for child, order in edges:
                    # Если ребро ведёт к искомой вершине, добавляем его
                    if child == node:
                        incoming.append((parent, order))
            # Сортируем входящие рёбра по порядковому номеру (order)
            incoming.sort(key=lambda x: x[1])

            # Рекурсивно вычисляем значения для всех дочерних вершин
            children_values = [evaluate(parent) for parent, _ in incoming]

            # Применяем операцию в зависимости от её типа
            if operation == "+":
                # Сложение всех дочерних значений
                return sum(children_values)
            elif operation == "*":
                # Умножение всех дочерних значений
                result = 1
                for value in children_values:
                    result *= value
                return result
            elif operation == "exp":
                # Вычисление экспоненты (e^x) для одного аргумента
                if len(children_values) != 1:
                    # Логируем ошибку и выбрасываем исключение, если аргументов не один
                    self.log_error("Операция 'exp' должна иметь ровно один аргумент")
                    raise ValueError("Операция 'exp' должна иметь ровно один аргумент")
                return math.exp(children_values[0])
            else:
                # Если операция неизвестна, логируем ошибку и выбрасываем исключение
                self.log_error(f"Неизвестная операция '{operation}' для вершины {node}")
                raise ValueError(f"Неизвестная операция '{operation}' для вершины {node}")

        # Находим вершину без исходящих рёбер (синк)
        sink = self.find_sink()
        if not sink:
            # Если конечная вершина (синк) не найдена, выбрасываем исключение
            raise ValueError("Не удалось найти конечную вершину графа.")

        # Начинаем вычисление с найденной конечной вершины
        return evaluate(sink)


 # python nntask3.py input1=input41.txt input2=input42.txt output1=output.txt
def main():
    input1, input2, input3, output1, output2 = parse_args()
    print(f"Входные файлы: {input1}, {input2}")
    print(f"Выходные файлы: {output1}, {output2}")

    graph = DirectedGraphWithOperations(input1, input2)
    if not graph.has_cycle():
        prefix_notation = graph.to_prefix_notation()
        print("Префиксное представление графа:", prefix_notation)

        prefix_with_operations = graph.to_prefix_with_operations()
        print("Функция с операциями:", prefix_with_operations)

        result = graph.evaluate_function()
        print("Результат вычисления функции:", result)
        save_result(output1, result)


if __name__ == '__main__':
    main()
