import networkx as nx
import jenkspy
import json
import plotly.graph_objects as go
from plotly.colors import qualitative

from build_weighted_graphs import compute_mmr
from constants import STATE_CENTROIDS

def build_mmr_rate_list() -> list:
    with open('data/maternal_mortality_rate/maternal_deaths_by_state.json', 'r') as file:
        maternal_deaths = json.load(file)
    with open('data/maternal_mortality_rate/births_by_state.json', 'r') as file:
        births = json.load(file)
    
    mmr_by_state = compute_mmr(births, maternal_deaths)
    return list(mmr_by_state.values())

def gen_breaks(rate_list: list) -> list:
    breaks = jenkspy.jenks_breaks(rate_list, n_classes=5)
    breaks = [float(x) for x in breaks]
    return breaks

def build_graph(breaks: list) -> tuple[list[set[str]], list[tuple[str, str]]]:
    with open('data/maternal_mortality_rate/maternal_deaths_by_state.json', 'r') as file:
        maternal_deaths = json.load(file)
    with open('data/maternal_mortality_rate/births_by_state.json', 'r') as file:
        births = json.load(file)
    with open('state_adjacency_list.json', 'r') as file:
        state_adjacency = json.load(file)
    
    rates_by_state = compute_mmr(births, maternal_deaths)

    bin_of = {}
    for state in rates_by_state:
        if breaks[0] <= rates_by_state[state] < breaks[1]:
            bin_of[state] = 0
        elif breaks[1] <= rates_by_state[state] < breaks[2]:
            bin_of[state] = 1
        elif breaks[2] <= rates_by_state[state] < breaks[3]:
            bin_of[state] = 2
        elif breaks[3] <= rates_by_state[state] < breaks[4]:
            bin_of[state] = 3
        elif breaks[4] <= rates_by_state[state] <= breaks[5]:
            bin_of[state] = 4

    # make a copy of the adjacency dict and remove Vermont (VT) if present. Does not delete VT from adjacency lists
    state_adjacency_vt_removed = dict(state_adjacency)
    if 'VT' in state_adjacency_vt_removed:
        del state_adjacency_vt_removed['VT']

    filtered_edges = []
    for state in state_adjacency_vt_removed:
        for neighbor in state_adjacency_vt_removed[state]:
            if neighbor != 'VT':
                if bin_of[state] == bin_of[neighbor]:
                    filtered_edges.append((state, neighbor))
    
    G_filtered = nx.Graph()
    G_filtered.add_nodes_from(state_adjacency_vt_removed)
    G_filtered.add_edges_from(filtered_edges)
    clusters = list(nx.connected_components(G_filtered))
    return clusters, filtered_edges

def plot_g(clusters: list[set[str]], filtered_edges: list[tuple[str, str]]) -> None:
    fig = go.Figure()

    fig.add_trace(go.Choropleth(
        locationmode='USA-states',
        locations=list(STATE_CENTROIDS.keys()),
        z=[1] * len(STATE_CENTROIDS),
        showscale=False,
        colorscale=[[0, '#f0f0f0'], [1, '#f0f0f0']],
        marker_line_color='gray',
        marker_line_width=0.5,
    ))

    palette = qualitative.Dark24

    cluster_lookup = {}
    for index, cluster in enumerate(clusters):
        for state in cluster:
            cluster_lookup[state] = index

    for state_a, state_b in filtered_edges:
        cluster_index = cluster_lookup[state_a]
        color = palette[cluster_index % len(palette)]
        fig.add_trace(go.Scattergeo(
            lon=[STATE_CENTROIDS[state_a][1], STATE_CENTROIDS[state_b][1]],
            lat=[STATE_CENTROIDS[state_a][0], STATE_CENTROIDS[state_b][0]],
            mode='lines',
            line=dict(width=1, color=color),
            opacity=0.55,
            showlegend=False,
            hoverinfo='skip',
        ))

    for index, cluster in enumerate(clusters):
        states = sorted(cluster)
        fig.add_trace(go.Scattergeo(
            lon=[STATE_CENTROIDS[state][1] for state in states],
            lat=[STATE_CENTROIDS[state][0] for state in states],
            text=states,
            mode='markers+text',
            marker=dict(size=8, color=palette[index % len(palette)], line=dict(width=0.5, color='black')),
            textposition='top center',
            textfont=dict(size=8),
            name=f'Cluster {index + 1} ({len(states)})',
        ))

    fig.update_layout(
        title='Regional MMR Clusters',
        geo=dict(scope='usa', projection_type='albers usa'),
        legend_title_text='Clusters',
    )

    fig.show()

def main():
    rates = build_mmr_rate_list()
    breaks = gen_breaks(rates)
    clusters, filtered_edges = build_graph(breaks)
    for cluster in clusters:
        print(cluster)
    plot_g(clusters, filtered_edges)

if __name__ == '__main__':
    main()
