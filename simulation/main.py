import networkx as nx
import matplotlib.pyplot as plt
import math

G = nx.Graph()

positions = {
    1: (0,0),
    2: (0,4),
    3: (-2,4),
    4: (-2,0),
    5: (-2,3),
    6: (-5,3),
    7: (-5,5),
    8: (-5,1),
    9: (-7,3),
    10: (-7,1),
    11: (-7,5)
}

G.add_nodes_from(positions.keys())
nx.set_node_attributes(G, positions, 'pos')
pos = nx.get_node_attributes(G, 'pos')

edges = [(1,2),(1,4),(2,3),(4,5),(3,5),(5,6),(6,7),(6,8),(6,9),(9,10),(9,11)]
G.add_edges_from(edges)
for u, v in G.edges():
    x1, y1 = positions[u]
    x2, y2 = positions[v]
    dist = math.hypot(x2 - x1, y2 - y1)
    G[u][v]['weight'] = dist
    

#define start/goal
start = 10
goal = 1
path = nx.dijkstra_path(G, start, goal)
path_edges = list(zip(path, path[1:]))


nx.draw(G, pos, with_labels=True)
nx.draw_networkx_edges(
    G,
    pos,
    edgelist=path_edges,
    edge_color='red',
    width=3
)

label_pos = {
    start: (pos[start][0], pos[start][1] - 0.3),
    goal:   (pos[goal][0], pos[goal][1] - 0.3)
}

nx.draw_networkx_labels(G, label_pos, labels={start: "START", goal: "GOAL"})


plt.show()

