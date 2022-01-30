from models.molecule import *
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np


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

        pos = self.generate_positions()  # nodes positions

        nx.draw(graph, pos=pos, labels=nodes_labels, with_labels=True, font_size=8, node_size=100)  # display nodes

        edge_weight = nx.get_edge_attributes(graph, 'weight')  # get edges weighted
        nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edge_weight, font_size=5)  # display edges

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

        pos = self.generate_positions()  # nodes positions

        colors = self.color_graph_nodes(graph.nodes)  # get nodes colored

        nx.draw(graph, pos=pos, node_color=colors, labels=nodes_labels, with_labels=True, font_size=8, node_size=100)  # display nodes
        nx.draw_networkx_edges(graph, pos=pos)  # display edges

        st.pyplot(fig)

    # generate nodes distinct colors (colored graph)
    @staticmethod
    def generate_colors(n):
        hex_values = []
        r = int(random.random() * 256)
        g = int(random.random() * 256)
        b = int(random.random() * 256)
        step = 256 / n
        for _ in range(n):
            r += step
            g += step
            b += step
            r = int(r) % 256
            g = int(g) % 256
            b = int(b) % 256
            r_hex = hex(r)[2:]
            g_hex = hex(g)[2:]
            b_hex = hex(b)[2:]
            color = '#' + r_hex + g_hex + b_hex
            while len(color) <= 6:
                color += '0'
            hex_values.append(color)
        return hex_values

    # color graph nodes
    def color_graph_nodes(self, nodes):
        labels = list(dict.fromkeys([label for label, _, _ in self.molecule.atoms_colored]))
        colors = self.generate_colors(len(labels))
        color_dict = {labels[i]: colors[i] for i in range(len(labels))}

        self.molecule.atoms_colored.sort(key=lambda element: element[1])

        nodes_colored = []
        for node in nodes:
            for atom in self.molecule.atoms_colored:
                label, id, _ = atom
                if id == node:
                    nodes_colored.append(color_dict[label])
        return nodes_colored

    # generate nodes positions using molecular representation of ChEBI in 2D
    def generate_positions(self):
        return {id: np.array([x, y]) for id, x, y in self.molecule.positions}
