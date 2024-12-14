import sys
import re

def parse_args():
    # Задаем стандартные названия
    default_inputs = ["input41.txt", None, None]
    default_outputs = ["output.json", None]

    # Получаем аргументы командной строки
    args = sys.argv[1:]

    # Проверка на каждый из аргументов с помощью регулярных выражений
    input1 = default_inputs[0]
    input2 = default_inputs[1]
    input3 = default_inputs[2]
    output1 = default_outputs[0]
    output2 = default_outputs[1]

    for arg in args:
        arg = arg.strip()  # Удаляем лишние пробелы и табуляции
        if arg.startswith("input1="):
            input1 = arg.split("=", 1)[1].strip()
        elif arg.startswith("input2="):
            input2 = arg.split("=", 1)[1].strip()
        elif arg.startswith("input3="):
            input3 = arg.split("=", 1)[1].strip()
        elif arg.startswith("output1="):
            output1 = arg.split("=", 1)[1].strip()
        elif arg.startswith("output2="):
            output2 = arg.split("=", 1)[1].strip()

    return input1, input2, input3, output1, output2
