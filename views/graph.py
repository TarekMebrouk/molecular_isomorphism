from models.molecule import *
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt


class Graph:
    # initialize graph with selected molecule
    def __init__(self, molecule):
        self.molecule = molecule

    # draw simple molecular structure (before modification)
    def simple(self):
        # create networkx graph
        graph = nx.Graph(width="100%", font_color="black")
        fig, ax = plt.subplots()

        # prepare nodes labels & edges lists
        nodes_labels = {id: label for label, id in self.molecule.atoms_id}
        edges = [(link[0], link[1], int(link[2])) for link in self.molecule.links]

        graph.add_weighted_edges_from(edges)  # add edges

        pos = nx.spring_layout(graph)  # nodes positions

        nx.draw(graph, pos, labels=nodes_labels, with_labels=True, font_size=8, node_size=100)  # display nodes

        edge_weight = nx.get_edge_attributes(graph, 'weight')  # get edges weighted
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_weight, font_size=5)  # display edges

        st.pyplot(fig)

    # draw advanced molecular structure (after transformation)
    def advanced(self):
        # create networkx graph
        graph = nx.Graph(width="100%", font_color="black")
        fig, ax = plt.subplots()

        # prepare nodes labels & edges lists
        nodes_labels = {id: label for label, id, _ in self.molecule.atoms_colored}
        for key in nodes_labels:
            if nodes_labels[key] == 'ZZZ':
                nodes_labels[key] = '-'
        edges = [(link[0], link[1]) for link in self.molecule.links_colored]

        graph.add_edges_from(edges)  # add edges

        pos = nx.spring_layout(graph)  # nodes positions

        nx.draw(graph, pos, labels=nodes_labels, with_labels=True, font_size=8, node_size=100)  # display nodes
        nx.draw_networkx_edges(graph, pos)  # display edges

        st.pyplot(fig)
