from helpers.file_handler import parse_args
from graph import DirectedGraph


# python nntask2.py input1=input41.txt output1=output1.txt
# python nntask2.py input1=input41.txt output1=output1.txt input2=input42.txt output2=output2.txt
def main():
    input1, input2, input3, output1, output2 = parse_args()
    print(f"Входные файлы: {input1}, {input2}")
    print(f"Выходные файлы: {output1}, {output2}")

    graph = DirectedGraph(input1 if input1 else "input41.txt")
    if not graph.has_cycle():
        prefix_notation = graph.to_prefix_notation()
        graph.display_graph()
        print("Префиксное представление графа:", prefix_notation)
        graph.save_prefix_notation_to_file(output1 if output1 else "output.txt")

    if input2 and output2:
        print("------Второй граф------")
        graph = DirectedGraph(input2)
        if not graph.has_cycle():
            prefix_notation = graph.to_prefix_notation()
            print("Префиксное представление графа:", prefix_notation)
            graph.save_prefix_notation_to_file(output2)


if __name__ == '__main__':
    main()
