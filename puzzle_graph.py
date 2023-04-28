import networkx as nx
from matplotlib import pyplot as plt

test = 2
if test == 1:
    people = ['Ann', 'Betty', 'Charlotte', 'Edith', 'Felicia', 'Georgia', 'Helen']
    people_met = {'Ann': ['Betty', 'Charlotte', 'Felicia', 'Georgia'],
                  'Betty': ['Ann', 'Charlotte', 'Edith', 'Felicia', 'Helen'],
                  'Charlotte': ['Ann', 'Betty', 'Edith'],
                  'Edith': ['Betty', 'Charlotte', 'Felicia'],
                  'Felicia': ['Ann', 'Betty', 'Edith', 'Helen'],
                  'Georgia': ['Ann', 'Helen'],
                  'Helen': ['Betty', 'Felicia', 'Georgia']}
else:
    people = ['Betty', 'Charlotte', 'Edith', 'Felicia', 'Georgia', 'Helen']
    people_met = {'Betty': ['Charlotte', 'Edith', 'Felicia', 'Helen'],
                  'Charlotte': ['Betty', 'Edith'],
                  'Edith': ['Betty', 'Charlotte', 'Felicia'],
                  'Felicia': ['Betty', 'Edith', 'Helen'],
                  'Georgia': ['Helen'],
                  'Helen': ['Betty', 'Felicia', 'Georgia']}


def create_graph(plot_graph=False):
    """
    Generate graph based on interrogation, and draw it it plot_graph = True
    :param plot_graph: True if graph is plotted
    :return: Graph
    """
    G = nx.Graph()
    for person in people:
        G.add_node(person)
    for p1 in people_met.keys():
        for p2 in people_met[p1]:
            G.add_edge(p1, p2)
    if plot_graph:
        nx.draw_spectral(G, node_size=500, node_color=['red', 'green', 'pink', 'brown', 'yellow', 'orange', 'skyblue'],
                         with_labels=True)
        plt.show()
    return G


def check_cycles(G):
    """
    Print all the chordless cycles with length = 4
    :param G: Input graph
    """
    list_cycles = list(sorted(nx.simple_cycles(G.to_directed())))
    for l in list_cycles:
        if len(l) == 4:
            H = G.subgraph(l)
            if not nx.is_chordal(H):
                print(l, len(l))


G = create_graph(False)
check_cycles(G)
