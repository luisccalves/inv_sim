import networkx as nx
import random
class ProcessGraph:

    def __init__(self,source,sink) -> None:
        self.G = nx.Graph()
        self.source = source
        self.sink = sink
    
    def add_edges(self,a,b,w):
        self.G.add_edge(a, b, weight=w)

    def choose_path(self,node):
        if  node==self.source or node==self.sink:
                pass
        else:

            nodes = [x[1] for x in list(self.G.edges(node, data="weight"))]
            if len(nodes)>2:
                weights = [x[2] for x in list(self.G.edges(node, data="weight"))[1:]]
                nodes = nodes[1:]

        
        
                selected = random.choices(nodes, cum_weights=weights, k=1)
                print(selected)
                nodes_remove = [x for x in nodes if x not in selected]
        
                for i in nodes_remove:
                    self.G.remove_edge(node, i)
                    self.G.remove_node(i)

    def bfs(self,start):
        visited = set()
        queue = [start]
        while len(queue):
            curr_node = queue.pop(0)
            self.choose_path(curr_node)
            visited.add(curr_node)
            queue.extend(c for c in self.G[curr_node] if c not in visited and c not in queue)
        return visited

    def return_path(self):
        self.bfs(self.source)
        return nx.dijkstra_path(self.G, self.source, self.sink)

        
