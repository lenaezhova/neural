import json
import numpy as np
import math
from helpers.file_handler import parse_args


def read_from_text_file(filename):
    try:
        with open(filename, 'r') as f:
            message = f.read().strip()
        return message
    except FileNotFoundError:
        print(f"Ошибка: файл {filename} не найден.")
        return None



class NeuralNetwork:
    def __init__(self, weights_file, dataset_file, iterations, learning_rate=0.1):
        self.weights_file = weights_file
        self.dataset_file = dataset_file
        self.iterations = iterations
        self.learning_rate = learning_rate
        self.layers = []
        self.dataset = []
        self.network_structure = {}
        self.error_file = f"error_{weights_file}"
        self.first_error_log = True
        self.load_weights()
        self.load_dataset()

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
                        layer = json.loads(f"[{line}]")
                        self.layers.append(np.array(layer, dtype=np.float64))
                        self.network_structure[f"Layer {layer_number}"] = layer
                    except Exception:
                        self.log_error(f"Строка {layer_number}: некорректный формат матрицы весов '{line}'")
        except FileNotFoundError:
            self.log_error(f"Файл {self.weights_file} не найден.")
        except Exception as e:
            self.log_error(f"Произошла ошибка при загрузке весов: {e}")

    def load_dataset(self):
        try:
            with open(self.dataset_file, 'r', encoding='utf-8') as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        inputs, outputs = line.split("->")
                        x = [float(i) for i in inputs.strip().split(",")]
                        y = [float(o) for o in outputs.strip().split(",")]
                        self.dataset.append((np.array(x), np.array(y)))
                    except Exception:
                        self.log_error(f"Строка {line_number}: некорректный формат строки обучающей выборки: '{line}'")
        except FileNotFoundError:
            self.log_error(f"Файл {self.dataset_file} не найден.")
        except Exception as e:
            self.log_error(f"Произошла ошибка при загрузке обучающей выборки: {e}")

    def activation_function(self, x):
        return 1 / (1 + np.exp(-x))  # Сигмоид

    def activation_derivative(self, x):
        return x * (1 - x)  # Производная сигмоида

    def forward_pass(self, inputs):
        activations = [inputs]
        for layer in self.layers:
            inputs = self.activation_function(np.dot(inputs, layer.T))
            activations.append(inputs)
        return activations

    def backpropagate(self, activations, expected_output):
        errors = [expected_output - activations[-1]]  # Ошибка выходного слоя
        deltas = [errors[-1] * self.activation_derivative(activations[-1])]

        # Обратное распространение ошибки
        for i in range(len(self.layers) - 1, 0, -1):
            error = np.dot(deltas[-1], self.layers[i])  # Ошибка предыдущего слоя
            delta = error * self.activation_derivative(activations[i])
            errors.append(error)
            deltas.append(delta)

        errors.reverse()
        deltas.reverse()

        # Обновление весов
        for i in range(len(self.layers)):
            self.layers[i] += self.learning_rate * np.outer(deltas[i], activations[i])

        return np.mean(np.abs(errors[0]))

    def train(self, history_file):
        history = []
        for iteration in range(1, self.iterations + 1):
            total_error = 0
            for inputs, expected_output in self.dataset:
                activations = self.forward_pass(inputs)
                error = self.backpropagate(activations, expected_output)
                total_error += error

            average_error = total_error / len(self.dataset)
            history.append(f"{iteration - 1}: {average_error}")

        try:
            with open(history_file, 'w', encoding='utf-8') as file:
                file.write("\n".join(history))
            print(f"История обучения успешно сохранена в {history_file}")
        except Exception as e:
            self.log_error(f"Ошибка при сохранении истории обучения: {e}")


# python nntask5.py input1=input51.txt input2=input52.txt input3=input53.txt output1=output51.txt
def main():
    # input1 - Входной файл с матрицами весов
    # input2 - Входной файл с обучающей выборкой
    # output1 - Число итераций обучения
    # output2 - Файл с историей ошибок
    input1, input2, input3, output1, output2 = parse_args()
    print(f"Входные файлы: {input1}, {input2}")
    print(f"Число итераций: {input3}")
    print(f"Выходной файл: {output1}")
    nn = NeuralNetwork(input1, input2, int(read_from_text_file(input3)))
    nn.train(output1)


if __name__ == '__main__':
    main()
