# pylint: skip-file
# flake8: noqa
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch

# Flattened state machine for operational and observation state diagram
# written and validated by Giorgio Brajnik based on the diagram and spec in ADR-8.

# The graph is a MultiDiGraph with two types of nodes: operational and observational
# and two types of transitions: those triggered by commands and those triggered by internal events


# How to use this script
# - you need to install networkx and matplotlib
# - you can run this script in a Python environment
# - with the command: `python3 obsstate-transition-graph.py'
# - it will print all transitions in the state machine
# - it will print all pairs of consecutive transitions in the state machine
# - it will generate and plot a graph of the state machine (not plarticulary useful for such a large state machine)


def create_merged_graph():
    G = nx.MultiDiGraph()

    # Operational states
    op_states = ["INIT", "OFF", "ON", "OP_FAULT"]
    G.add_nodes_from(op_states, type="operational")

    # Observational states
    obs_states = [
        "EMPTY",
        "RESOURCING",
        "IDLE",
        "CONFIGURING",
        "READY",
        "SCANNING",
        "ABORTING",
        "ABORTED",
        "RESTARTING",
        "OBS_FAULT",
    ]
    G.add_nodes_from(obs_states, type="observational")

    op_transitions = [
        ("INIT", "OFF", {"label": "Initialised", "type": "event"}),
        ("INIT", "OP_FAULT", {"label": "fatal error", "type": "event"}),
        ("OFF", "EMPTY", {"label": "On", "type": "command"}),
        ("OFF", "OP_FAULT", {"label": "fatal error", "type": "event"}),
        ("OP_FAULT", "OFF", {"label": "Reset", "type": "command"}),
    ]
    # Operational transitions
    G.add_edges_from(op_transitions)

    # Observational transitions
    obs_transitions = [
        (
            "EMPTY",
            "RESOURCING",
            {"label": "AssignResources", "type": "command"},
        ),
        ("EMPTY", "OFF", {"label": "Off", "type": "command"}),
        (
            "EMPTY",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("EMPTY", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("RESOURCING", "IDLE", {"label": "Assigned", "type": "event"}),
        ("RESOURCING", "IDLE", {"label": "Released", "type": "event"}),
        ("RESOURCING", "ABORTING", {"label": "Abort", "type": "command"}),
        ("RESOURCING", "EMPTY", {"label": "All released", "type": "event"}),
        (
            "RESOURCING",
            "OBS_FAULT",
            {"label": "Observation fault", "type": "event"},
        ),
        ("RESOURCING", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("IDLE", "CONFIGURING", {"label": "Configure", "type": "command"}),
        (
            "IDLE",
            "RESOURCING",
            {"label": "ReleaseResources", "type": "command"},
        ),
        (
            "IDLE",
            "RESOURCING",
            {"label": "AssignResources", "type": "command"},
        ),
        ("IDLE", "ABORTING", {"label": "Abort", "type": "command"}),
        ("IDLE", "OBS_FAULT", {"label": "Observation Fault", "type": "event"}),
        ("IDLE", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("CONFIGURING", "READY", {"label": "Ready", "type": "event"}),
        (
            "CONFIGURING",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("CONFIGURING", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("CONFIGURING", "ABORTING", {"label": "Abort", "type": "command"}),
        ("READY", "SCANNING", {"label": "Scan", "type": "command"}),
        ("READY", "IDLE", {"label": "End", "type": "command"}),
        ("READY", "ABORTING", {"label": "Abort", "type": "command"}),
        ("READY", "CONFIGURING", {"label": "Configure", "type": "command"}),
        (
            "READY",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("READY", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("SCANNING", "READY", {"label": "EndScan", "type": "command"}),
        ("SCANNING", "ABORTING", {"label": "Abort", "type": "command"}),
        ("SCANNING", "READY", {"label": "ScanComplete", "type": "event"}),
        (
            "SCANNING",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("SCANNING", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("ABORTING", "ABORTED", {"label": "Abort complete", "type": "event"}),
        (
            "ABORTING",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("ABORTING", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("ABORTED", "RESTARTING", {"label": "Restart", "type": "command"}),
        (
            "ABORTED",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("ABORTED", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        (
            "RESTARTING",
            "EMPTY",
            {"label": "Restart Complete", "type": "event"},
        ),
        (
            "RESTARTING",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("RESTARTING", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("OBS_FAULT", "RESTARTING", {"label": "Restart", "type": "command"}),
        (
            "OBS_FAULT",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("OBS_FAULT", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
    ]
    G.add_edges_from(obs_transitions)

    # Connections between operational and observational states
    cross_transitions = [
        # ('ON', 'EMPTY', {'label': 'initialized', 'type': 'event'}),
        # ('OFF', 'EMPTY', {'label': 'Power On', 'type': 'event'}),
        # ('EMPTY', 'OFF', {'label': 'Power Off', 'type': 'event'}),
        # ('OBS_FAULT', 'OP_FAULT', {'label': 'Escalate Fault', 'type': 'event'})
    ]
    G.add_edges_from(cross_transitions)

    return G


fontsize = 15


def compute_edge_label(label, edge_type):
    if edge_type == "command":
        return f"CMD: {label}"
    else:
        return f"AUTO: {label}"


def draw_curved_edge(
    ax, posA, posB, label, edge_type, connectionstyle="arc3,rad=0.2"
):
    if edge_type == "command":
        color = "blue"
    else:
        color = "red"
    label = compute_edge_label(label, edge_type)

    arrow = FancyArrowPatch(
        posA,
        posB,
        arrowstyle="->",
        color=color,
        connectionstyle=connectionstyle,
        mutation_scale=30,  # Increased from 20 to 30
        linewidth=2,  # Increased from 1 to 2
        shrinkA=20,  # Added to start arrow further from node
        shrinkB=29,
    )
    ax.add_patch(arrow)

    # Calculate the position for the label closer to the source node
    t = 0.1  # Adjust this value to move label closer (smaller) or further (larger) from source
    label_pos = posA + t * (np.array(posB) - np.array(posA))

    # Add a small offset perpendicular to the edge direction
    diff = np.array(posB) - np.array(posA)
    perp = np.array([-diff[1], diff[0]])
    norm = np.linalg.norm(perp)
    if norm != 0:
        perp = perp / norm
    offset = perp * 0.01  # Adjust this value for perpendicular offset

    label_pos = label_pos + offset

    ax.text(
        label_pos[0],
        label_pos[1],
        label,
        fontsize=fontsize,
        ha="center",
        va="center",
        color=color,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, pad=0.5),
    )


# Create the merged graph
merged_graph = create_merged_graph()


class StateGraphAnalyzer:
    """MISSION: implement the following methods to analyze a state graph:
    - print_transitions(): prints all individual transitions in the graph
    """

    def __init__(self, graph):
        self.graph = graph

    def print_transitions(self):
        """
        Prints each transition in the format:
        start-state --> (trigger) --> end-state
        """
        for i, (start_state, end_state, data) in enumerate(
            self.graph.edges(data=True), 1
        ):
            trigger = data["label"]
            label = compute_edge_label(data["label"], data["type"])
            print(f"{i}. {start_state} --> ({label}) --> {end_state}")

    def get_outgoing_transitions(self, state):
        """
        Returns a list of outgoing transitions from the given state.
        Each transition is a tuple: (end_state, trigger, type)
        """
        return [
            (end_state, data["label"], data["type"])
            for end_state, data in self.graph[state].items()
        ]

    def get_incoming_transitions(self, state):
        """
        Returns a list of incoming transitions to the given state.
        Each transition is a tuple: (start_state, trigger, type)
        """
        return [
            (start_state, data["label"], data["type"])
            for start_state, data in self.graph.pred[state].items()
        ]

    def get_all_commands(self):
        """
        Returns a list of all unique commands in the graph.
        """
        return list(
            set(
                data["label"]
                for _, _, data in self.graph.edges(data=True)
                if data["type"] == "command"
            )
        )

    def get_all_events(self):
        """
        Returns a list of all unique events in the graph.
        """
        return list(
            set(
                data["label"]
                for _, _, data in self.graph.edges(data=True)
                if data["type"] == "event"
            )
        )

    def get_states_with_self_transitions(self):
        """
        Returns a list of states that have self-transitions.
        """
        return [
            node
            for node in self.graph.nodes()
            if self.graph.has_edge(node, node)
        ]

    def print_consecutive_transition_pairs(self):
        """
        Prints a numbered list of pairs of consecutive transitions in the graph.
        Format:
        n. start-state --> (trigger1) --> intermediate-state --> (trigger2) --> end-state
        """
        transition_pairs = []
        for start_state in self.graph.nodes():
            for mid_state, data1 in self.graph[start_state].items():
                data1 = data1[0]
                for end_state, data2 in self.graph[mid_state].items():
                    data2 = data2[0]
                    if start_state != end_state:  # Avoid cycles
                        trigger1 = compute_edge_label(
                            data1["label"], data1["type"]
                        )
                        trigger2 = compute_edge_label(
                            data2["label"], data2["type"]
                        )
                        transition_pairs.append(
                            (
                                start_state,
                                mid_state,
                                end_state,
                                trigger1,
                                trigger2,
                            )
                        )

        for i, (start, mid, end, trigger1, trigger2) in enumerate(
            transition_pairs, 1
        ):
            print(
                f"{i}. {start} --> ({trigger1}) --> {mid} --> ({trigger2}) --> {end}"
            )

    def print_transition_matrix(self):
        G = self.graph
        # Get all nodes in the graph
        nodes = list(G.nodes())

        # Create an empty DataFrame to store the transition matrix
        matrix = pd.DataFrame(index=nodes, columns=nodes)
        matrix = matrix.fillna("")

        # Populate the matrix
        for edge in G.edges(data=True):
            source, target, data = edge
            label = data.get("label", "")
            edge_type = data.get("type", "")

            # Combine label and type information
            info = f"{label} ({edge_type})"

            # If there are multiple edges between the same nodes, append the new info
            if matrix.at[source, target]:
                matrix.at[source, target] += f"\n{info}"
            else:
                matrix.at[source, target] = info

        # Convert the DataFrame to a markdown table
        markdown_table = matrix.to_markdown()

        # Print the markdown table
        print("# FSM Transition Matrix")
        print()
        print(markdown_table)


analyzer = StateGraphAnalyzer(merged_graph)

print("All transitions:")
analyzer.print_transitions()

#
print("\n\n\nAll consecutive pairs of transitions:")
analyzer.print_consecutive_transition_pairs()

analyzer.print_transition_matrix()


def plot_graph(graph):
    global data
    # Visualization
    fig, ax = plt.subplots(figsize=(40, 30))
    pos = nx.spring_layout(graph, k=2, iterations=50)
    # Draw nodes
    op_nodes = [
        node
        for node, data in graph.nodes(data=True)
        if data.get("type") == "operational"
    ]
    obs_nodes = [
        node
        for node, data in graph.nodes(data=True)
        if data.get("type") == "observational"
    ]
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=op_nodes,
        node_color="lightblue",
        node_size=3000,
        ax=ax,
    )
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=obs_nodes,
        node_color="lightgreen",
        node_size=3000,
        ax=ax,
    )
    # Draw edges with curves for bidirectional connections
    for edge in graph.edges(data=True):
        n1, n2, data = edge
        label = data["label"]
        edge_type = data["type"]

        # Unidirectional edge
        draw_curved_edge(
            ax,
            pos[n1],
            pos[n2],
            label,
            edge_type,
            connectionstyle="arc3,rad=0.3",
        )
    # Draw labels
    nx.draw_networkx_labels(
        graph, pos, font_size=15, font_weight="bold", ax=ax
    )
    plt.title(
        "Merged Operational and Observational State Machine", fontsize=20
    )
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# uncomment this to plot the graph
# plot_graph(merged_graph)
