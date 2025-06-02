# fk_graph_builder.py
from collections import defaultdict

def build_fk_graph(fk_lines):
    graph = defaultdict(set)
    for fk in fk_lines:
        left, right = fk.replace("Join Hint: ", "").split("=")
        table_a = left.split(".")[0].strip()
        table_b = right.split(".")[0].strip()
        graph[table_a].add(table_b)
        graph[table_b].add(table_a)
    return graph
