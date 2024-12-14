import json
import numpy as np
from helpers.file_handler import parse_args
import math


class NeuralNetwork:
    def __init__(self, weights_file, input_vector_file):
        self.weights_file = weights_file
        self.input_vector_file = input_vector_file
        self.error_file = f"error_{weights_file}"
        self.first_error_log = True
        self.layers = []
        self.input_vector = []
        self.network_structure = {}
        self.load_weights()
        self.load_input_vector()

    def log_error(self, message):
        mode = 'w' if self.first_error_log else 'a'
        with open(self.error_file, mode, encoding='utf-8') as error_file:
            error_file.write(message + "\n")
        self.first_error_log = False

    def load_weights(self):
        try:
            with open(self.weights_file, 'r', encoding='utf-8') as file:
                for layer_number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        # Интерпретируем строку как список нейронов (каждый нейрон — список весов)
                        layer = json.loads(f"[{line}]")
                        self.layers.append(layer)
                        self.network_structure[f"Layer {layer_number}"] = layer
                    except Exception:
                        self.log_error(f"Строка {layer_number}: некорректный формат матрицы весов '{line}'")
        except FileNotFoundError:
            self.log_error(f"Файл {self.weights_file} не найден.")
        except Exception as e:
            self.log_error(f"Произошла ошибка при загрузке весов: {e}")

    def load_input_vector(self):
        try:
            with open(self.input_vector_file, 'r', encoding='utf-8') as file:
                line = file.readline().strip()
                if not line:
                    raise ValueError("Пустой входной файл.")
                try:
                    self.input_vector = [float(x) for x in line.split()]
                except Exception:
                    self.log_error(f"Некорректный формат входного вектора: '{line}'")
        except FileNotFoundError:
            self.log_error(f"Файл {self.input_vector_file} не найден.")
        except Exception as e:
            self.log_error(f"Произошла ошибка при загрузке входного вектора: {e}")

    def activation_function(self, x):
        # Функция активации
        return 1 / (1 + math.exp(-x))

    def forward_pass(self):
        if not self.layers or not self.input_vector:
            self.log_error("Отсутствуют веса или входной вектор.")
            return None

        vector = self.input_vector
        for layer_number, layer in enumerate(self.layers, start=1):
            new_vector = []
            for neuron_number, neuron_weights in enumerate(layer, start=1):
                if len(neuron_weights) != len(vector):
                    self.log_error(
                        f"Ошибка на слое {layer_number}, нейрон {neuron_number}: "
                        f"несоответствие размерностей (вход: {len(vector)}, веса: {len(neuron_weights)})."
                    )
                    return None
                weighted_sum = sum(w * x for w, x in zip(neuron_weights, vector))
                new_vector.append(self.activation_function(weighted_sum))
            vector = new_vector
        return vector

    def save_network_structure(self, output_file):
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(self.network_structure, file, ensure_ascii=False, indent=4)
            print(f"Структура сети успешно сохранена в {output_file}")
        except Exception as e:
            self.log_error(f"Ошибка при сохранении структуры сети: {e}")

    def save_result(self, output_file):
        result = self.forward_pass()
        if result is None:
            self.log_error("Ошибка: результат не был рассчитан.")
            return
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=4)
            print(f"Результат успешно сохранен в {output_file}")
        except Exception as e:
            self.log_error(f"Ошибка при сохранении результата: {e}")


# python nntask4.py input1=input41.txt input2=input42.txt output1=output.json output2=output2.json
def main():
    # input1 - Входной файл с матрицами весов
    # input2 - Входной файл с вектором
    # output1 - Выходной файл с сетью
    # output2 -  Выходной файл с вектором
    input1, input2, input3, output1, output2 = parse_args()
    print(f"Входные файлы: {input1}, {input2}")
    print(f"Выходные файлы: {output1}, {output2}")

    nn = NeuralNetwork(input1, input2)
    nn.save_network_structure(output1)
    nn.save_result(output2)


if __name__ == '__main__':
    main()
