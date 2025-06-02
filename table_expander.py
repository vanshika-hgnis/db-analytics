# table_expander.py
def expand_tables(detected_tables, fk_graph, max_depth=1):
    expanded = set(detected_tables)
    queue = list(detected_tables)

    for _ in range(max_depth):
        next_queue = []
        for table in queue:
            for neighbor in fk_graph[table]:
                if neighbor not in expanded:
                    expanded.add(neighbor)
                    next_queue.append(neighbor)
        queue = next_queue

    return list(expanded)
