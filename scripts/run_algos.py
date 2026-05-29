""" This module runs MST and APSP algorithms on IMR and MMR graphs """

import networkx as nx
import plotly.graph_objects as go


STATE_CENTROIDS = {
    "AL": (32.7794, -86.8287),
    "AK": (64.0685, -152.2782),
    "AZ": (34.2744, -111.6602),
    "AR": (34.8938, -92.4426),
    "CA": (37.1841, -119.4696),
    "CO": (38.9972, -105.5478),
    "CT": (41.6219, -72.7273),
    "DE": (38.9896, -75.505),
    "DC": (38.9101, -77.0147),
    "FL": (28.6305, -82.4497),
    "GA": (32.6415, -83.4426),
    "HI": (20.2927, -156.3737),
    "ID": (44.3509, -114.613),
    "IL": (40.0417, -89.1965),
    "IN": (39.8942, -86.2816),
    "IA": (42.0751, -93.496),
    "KS": (38.4937, -98.3804),
    "KY": (37.5347, -85.3021),
    "LA": (31.0689, -91.9968),
    "ME": (45.3695, -69.2428),
    "MD": (39.055, -76.7909),
    "MA": (42.2596, -71.8083),
    "MI": (44.3467, -85.4102),
    "MN": (46.2807, -94.3053),
    "MS": (32.7364, -89.6678),
    "MO": (38.3566, -92.458),
    "MT": (47.0527, -109.6333),
    "NE": (41.5378, -99.7951),
    "NV": (39.3289, -116.6312),
    "NH": (43.6805, -71.5811),
    "NJ": (40.1907, -74.6728),
    "NM": (34.4071, -106.1126),
    "NY": (42.9538, -75.5268),
    "NC": (35.5557, -79.3877),
    "ND": (47.4501, -100.4659),
    "OH": (40.2862, -82.7937),
    "OK": (35.5889, -97.4943),
    "OR": (43.9336, -120.5583),
    "PA": (40.8781, -77.7996),
    "RI": (41.6762, -71.5562),
    "SC": (33.9169, -80.8964),
    "SD": (44.4443, -100.2263),
    "TN": (35.858, -86.3505),
    "TX": (31.4757, -99.3312),
    "UT": (39.3055, -111.6703),
    "VT": (44.0687, -72.6658),
    "VA": (37.5215, -78.8537),
    "WA": (47.3826, -120.4472),
    "WV": (38.6409, -80.6227),
    "WI": (44.6243, -89.9941),
    "WY": (42.9957, -107.5512),
}


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