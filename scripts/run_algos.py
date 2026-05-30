""" This module runs MST and APSP algorithms on IMR and MMR graphs """

import networkx as nx
import jenkspy
import plotly.graph_objects as go

from constants import STATE_CENTROIDS


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

def generate_mst(graph: nx.Graph) -> nx.Graph:
    """Generate MST for a NetworkX graph loaded from GraphML."""
    mst = nx.minimum_spanning_tree(graph)
    return mst

def plot_mst(mst: nx.Graph, cut_edges: list) -> None:
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
    for u, v, w in cut_edges:
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

def generate_cut_edges(mst: nx.Graph, weight_break: float) -> list:
    cut_edges = []
    mst_edges = list(mst.edges(data=True))

    rate_weight_list = []
    for edge in mst_edges:
        rate_weight_list.append(edge[2]['weight'])
    breaks = jenkspy.jenks_breaks(rate_weight_list, n_classes=5)
    breaks = [float(x) for x in breaks]

    # TODO: Cluster edges using Jenks instead of arbitrary weight selection
    for edge in mst_edges:
        if edge[2]["weight"] > weight_break:
            cut_edges.append(edge)
    return cut_edges


def main():
    G_imr = nx.read_graphml('graphs/imr_graph.graphml')
    G_mmr = nx.read_graphml('graphs/mmr_graph.graphml')

    # Generate and print IMR MST
    mst_imr = generate_mst(G_imr)
    if mst_imr:
        print("\nIMR Edge Weights:")
        sorted_edges = sorted(mst_imr.edges(data=True), key=lambda x:x[2].get("weight", 1))
        for line in sorted_edges:
            print(line)

    # Generate and print MMR MST
    mst_mmr = generate_mst(G_mmr)
    if mst_mmr:
        print("\nMMR Edge Weights:")
        sorted_edges = sorted(mst_mmr.edges(data=True), key=lambda x:x[2].get("weight", 1))
        for line in sorted_edges:
            print(line)

    # Generate and print MMR cut edges
    mmr_cut_edges = generate_cut_edges(mst_mmr, 4)
    if mmr_cut_edges:
        print("\nMMR Cut Edges")
        for line in mmr_cut_edges:
            print(line)
    
    # Generate and print IMR cut edges
    imr_cut_edges = generate_cut_edges(mst_imr, 6)
    if imr_cut_edges:
        print("\nIMR Cut Edges")
        for line in imr_cut_edges:
            print(line)

    # Plot MMR MST
    # plot_mst(mst_mmr, mmr_cut_edges)

    # Plit IMR MST
    plot_mst(mst_imr, imr_cut_edges)


if __name__ == '__main__':
    main()