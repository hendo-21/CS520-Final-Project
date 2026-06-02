""" This module runs MST and APSP algorithms on IMR and MMR graphs """

import networkx as nx
import jenkspy
import plotly.graph_objects as go
import pandas as pd
import json

from constants import STATE_CENTROIDS

def generate_mst(graph: nx.Graph) -> nx.Graph:
    """Generate MST for a NetworkX graph loaded from GraphML."""
    mst = nx.minimum_spanning_tree(graph)
    return mst

def plot_mst(mst: nx.Graph, cut_edges: list) -> None:
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

    # Add MST edges to figure
    mst_lons, mst_lats = [], []
    for u, v in mst.edges():
        mst_lons.extend([STATE_CENTROIDS[u][1], STATE_CENTROIDS[v][1], None])
        mst_lats.extend([STATE_CENTROIDS[u][0], STATE_CENTROIDS[v][0], None])

    fig.add_trace(go.Scattergeo(
        lon=mst_lons, lat=mst_lats,
        mode='lines',
        line=dict(width=1, color='gray'),
        name='MST edges',
    ))

    # Overlay cut edges
    cut_lons, cut_lats = [], []
    for u, v in cut_edges:
        cut_lons.extend([STATE_CENTROIDS[u][1], STATE_CENTROIDS[v][1], None])
        cut_lats.extend([STATE_CENTROIDS[u][0], STATE_CENTROIDS[v][0], None])

    fig.add_trace(go.Scattergeo(
        lon=cut_lons, lat=cut_lats,
        mode='lines',
        line=dict(width=2.5, color='red'),
        name='Cut edges',
    ))


    # Add state labels
    fig.add_trace(go.Scattergeo(
        lon=[c[1] for c in STATE_CENTROIDS.values()],
        lat=[c[0] for c in STATE_CENTROIDS.values()],
        text=list(STATE_CENTROIDS.keys()),
        mode='markers+text',
        marker=dict(size=4, color='black'),
        textposition='top center',
        textfont=dict(size=8),
        name='States',
    ))

    fig.update_geos(scope='usa', projection_type='albers usa')
    fig.update_layout(title='MMR MST with cut edges', width=900, height=600)
    fig.show()

def generate_cut_edges(mst: nx.Graph, threshold: int) -> list:
    cut_edges = []
    mst_edges = list(mst.edges(data=True))

    rate_weight_list = []
    for edge in mst_edges:
        rate_weight_list.append(edge[2]['weight'])
    breaks = jenkspy.jenks_breaks(rate_weight_list, n_classes=5)
    breaks = [float(x) for x in breaks]

    # Cluster edges using Jenks instead of arbitrary weight selection
    bin_of = {}
    for edge in mst_edges:
        if breaks[0] <= edge[2]['weight'] < breaks[1]:
            bin_of[(edge[0], edge[1])] = 0
        elif breaks[1] <= edge[2]['weight'] < breaks[2]:
            bin_of[(edge[0], edge[1])] = 1
        elif breaks[2] <= edge[2]['weight'] < breaks[3]:
            bin_of[(edge[0], edge[1])] = 2
        elif breaks[3] <= edge[2]['weight'] < breaks[4]:
            bin_of[(edge[0], edge[1])] = 3
        elif breaks[4] <= edge[2]['weight'] <= breaks[5]:
            bin_of[(edge[0], edge[1])] = 4

    cut_edges = []
    for edge in bin_of:
        if bin_of[edge] >= threshold:
            cut_edges.append(edge)
    return cut_edges

def run_floyd_warshall(graph: nx.Graph) -> dict:
    apsp = {}
    apsp = nx.floyd_warshall(graph)
    return apsp

def build_apsp_dataframe(graph: nx.Graph, distances: dict, filename: str) -> pd.DataFrame:
    apsp_paths, _ = nx.floyd_warshall_predecessor_and_distance(graph)
    rows_list = []
    seen_pairs = set()
    for first_state in distances:
        for second_state in distances[first_state]:
            if first_state == second_state:
                continue
            pair_key = frozenset((first_state, second_state))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            
            path = nx.reconstruct_path(first_state, second_state, apsp_paths)
            hops = len(path) - 1
            distance = distances[first_state][second_state]
            
            rows_list.append({
                'state1': first_state,
                'state2': second_state,
                'distance': distance,
                'hops': hops,
                'distance_per_hop': distance / hops if hops > 0 else 0,
                'states_in_path': path,
            })
    
    df = pd.DataFrame(rows_list)
    df.to_json(f'data/{filename}.json', orient='records', indent=4)
    return df

def main():
    G_imr = nx.read_graphml('graphs/imr_graph.graphml')
    G_mmr = nx.read_graphml('graphs/mmr_graph.graphml')

    # Generate and export MST
    mst_imr = generate_mst(G_imr)
    nx.write_graphml(mst_imr, 'graphs/imr_mst.graphml', infer_numeric_types=True)


    # Generate and export MST
    mst_mmr = generate_mst(G_mmr)
    nx.write_graphml(mst_mmr, 'graphs/mmr_mst.graphml', infer_numeric_types=True)

    # Generate and export cut edges for cutting edges in top 3 bins
    mmr_cut_edges_top_3 = generate_cut_edges(mst_mmr, 2)
    mmr_cut_edges_top_2 = generate_cut_edges(mst_mmr, 3)
    mmr_cut_edges_top_1 = generate_cut_edges(mst_mmr, 4)
    mmr_cut_edges = [
        {'threshold': 2, 'cut_edges': mmr_cut_edges_top_3},
        {'threshold': 3, 'cut_edges': mmr_cut_edges_top_2},
        {'threshold': 4, 'cut_edges': mmr_cut_edges_top_1},
    ]
    with open('data/mmr_cut_edges.json', 'w') as f:
        json.dump(mmr_cut_edges, f)
    
    # Generate and export cut edges for cutting edges in top 3 bins
    imr_cut_edges_top_3 = generate_cut_edges(mst_imr, 2)
    imr_cut_edges_top_2 = generate_cut_edges(mst_imr, 3)
    imr_cut_edges_top_1 = generate_cut_edges(mst_imr, 4)
    imr_cut_edges = [
        {'threshold': 2, 'cut_edges': imr_cut_edges_top_3},
        {'threshold': 3, 'cut_edges': imr_cut_edges_top_2},
        {'threshold': 4, 'cut_edges': imr_cut_edges_top_1},
    ]
    with open('data/imr_cut_edges.json', 'w') as f:
        json.dump(imr_cut_edges, f)

    apsp_mmr = run_floyd_warshall(G_mmr)
    d = build_apsp_dataframe(G_mmr, apsp_mmr, 'mmr_apsp')

    apsp_imr = run_floyd_warshall(G_imr)
    d_imr = build_apsp_dataframe(G_imr, apsp_imr, 'imr_apsp')

if __name__ == '__main__':
    main()