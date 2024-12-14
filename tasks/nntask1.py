from helpers.file_handler import parse_args
from graph import DirectedGraph

# python nntask1.py input1=input41.txt output1=output1.json
# python nntask2.py input1=input41.txt output1=output1.json input2=input42.txt output2=output2.json
def main():
    input1, input2, input3, output1, output2 = parse_args()
    print(f"Входные файлы: {input1}, {input2}")
    print(f"Выходные файлы: {output1}, {output2}")

    graph = DirectedGraph(input1 if input1 else "input41.txt")
    graph.save_graph_as_json(output1 if output1 else "output.json")
    graph.display_graph()

    if input2 and output2:
        print("------Второй граф------")
        graph = DirectedGraph(input2)
        graph.save_graph_as_json(output2)
        graph.display_graph()


if __name__ == '__main__':
    main()
