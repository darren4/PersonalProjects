from typing import List, Dict


class GraphInterface:
    class Connection:
        def __init__(self, from_node_id: int, to_node_id: int, distance: int):
            self.from_node_id: int = from_node_id
            self.to_node_id: int = to_node_id
            self.distance: int = distance

    def __init__(self, connections: List[Connection]=list()):
        self._node_connections: Dict[int, List[GraphInterface.Connection]] = {}
        for connection in connections:
            if connection.from_node_id in self._node_connections:
                self._node_connections[connection.from_node_id].append(connection)
            else:
                self._node_connections[connection.from_node_id] = [connection]

    def get_connections(self, node_id: int):
        try:
            return self._node_connections[node_id]
        except KeyError:
            return []
