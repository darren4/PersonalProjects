from typing import List, Dict
import queue


class GraphInterface:
    class Connection:
        def __init__(self, from_node_id: int, to_node_id: int, distance: int = 1):
            self.from_node_id: int = from_node_id
            self.to_node_id: int = to_node_id
            self.distance: int = distance

    def __init__(self, connections: List[Connection] = list()):
        if not connections:
            raise ValueError("connections list cannot be empty")
        self._viewable_nodes = {connections[0].from_node_id}
        self._node_connections: Dict[int, List[GraphInterface.Connection]] = {}
        for connection in connections:
            if connection.from_node_id in self._node_connections:
                self._node_connections[connection.from_node_id].append(connection)
            else:
                self._node_connections[connection.from_node_id] = [connection]

    def get_connections(self, node_id: int):
        if node_id not in self._viewable_nodes:
            raise ValueError(f"Node id {node_id} never returned as destination")
        try:
            connections: List[GraphInterface.Connection] = self._node_connections[
                node_id
            ]
        except KeyError:
            connections = []
        for connection in connections:
            self._viewable_nodes.add(connection.to_node_id)
        return connections

    def reset(self):
        self._viewable_nodes.clear()


if __name__ == "__main__":
    connections_list = [
        GraphInterface.Connection(1, 2),
        GraphInterface.Connection(2, 1),
        GraphInterface.Connection(3, 2),
        GraphInterface.Connection(2, 3),
        GraphInterface.Connection(2, 6),
        GraphInterface.Connection(6, 2),
        GraphInterface.Connection(3, 6),
        GraphInterface.Connection(6, 3),
        GraphInterface.Connection(3, 4),
        GraphInterface.Connection(4, 3),
        GraphInterface.Connection(4, 5),
        GraphInterface.Connection(5, 4),
    ]

    graph_interface = GraphInterface(connections_list)

    node_left = 6
    node_right = 4
    shortest_distance = 2
    shortest_path = [6, 3, 4]

    # attempt 1
    search = queue.SimpleQueue()
    search.put(1)
    start_node = None
    while not search.empty():
        current_node = search.get()
        if current_node == node_left or current_node == node_right:
            start_node = current_node
            break
        connections = graph_interface.get_connections(current_node)
        for connection in connections:
            search.put(connection.to_node_id)

    search = queue.SimpleQueue()
    search.put(start_node)
    if start_node == node_left:
        end_node = node_right
    else:
        end_node = node_left

    steps_back = {start_node: start_node}
    first_step_back = None
    while not search.empty():
        current_node = search.get()
        connections = graph_interface.get_connections(current_node)
        for connection in connections:
            if connection.to_node_id == end_node:
                first_step_back = current_node
                break
            if connection.to_node_id not in steps_back:
                search.put(connection.to_node_id)
                steps_back[connection.to_node_id] = current_node
        if first_step_back:
            break

    shortest_path_attempt = [end_node, first_step_back]
    current_node = first_step_back
    while current_node != start_node:
        current_node = steps_back[current_node]
        shortest_path_attempt.append(current_node)

    print(shortest_path_attempt)
