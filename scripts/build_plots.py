""" This module builds map plots for the final report. """

import networkx as nx
import jenkspy
import plotly.graph_objects as go
import pandas as pd
import json

from constants import STATE_CENTROIDS

def build_base_fig() -> go.Figure:
    # Build base map plot
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

    return fig


def plot_weighted_graph(fig: go.Figure, graph: nx.Graph, rate_type: str) -> None:
    edges = graph.edges(data=True)
    edge_lons, edge_lats = [], []
    edge_text_lons, edge_text_lats, edge_text = [], [], []
    for u, v, data in edges:
        weight = round(float(data.get('weight', 0)), 2)
        edge_lons.extend([STATE_CENTROIDS[u][1], STATE_CENTROIDS[v][1], None])
        edge_lats.extend([STATE_CENTROIDS[u][0], STATE_CENTROIDS[v][0], None])
        edge_text_lons.append((STATE_CENTROIDS[u][1] + STATE_CENTROIDS[v][1]) / 2)
        edge_text_lats.append((STATE_CENTROIDS[u][0] + STATE_CENTROIDS[v][0]) / 2)
        edge_text.append(f'{weight:.2f}')

    fig.add_trace(go.Scattergeo(
        lon=edge_lons, lat=edge_lats,
        mode='lines',
        line=dict(width=1, color='gray'),
        name='Edge weights',
    ))

    fig.add_trace(go.Scattergeo(
        lon=edge_text_lons,
        lat=edge_text_lats,
        text=edge_text,
        mode='text',
        textfont=dict(size=8, color='black'),
        hoverinfo='skip',
        showlegend=False,
    ))
    
    fig.update_layout(title=f'Contiguous 48 states weighted by {rate_type} variance', width=1500, height=1000)
    fig.show()

def plot_mst(fig: go.Figure, mst: nx.Graph, cut_edges: list, rate_type: str, bin_cut: int) -> None:
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

    mst_weight_lons, mst_weight_lats, mst_weight_text = [], [], []
    for u, v, data in mst.edges(data=True):
        mst_weight_lons.append((STATE_CENTROIDS[u][1] + STATE_CENTROIDS[v][1]) / 2)
        mst_weight_lats.append((STATE_CENTROIDS[u][0] + STATE_CENTROIDS[v][0]) / 2)
        mst_weight_text.append(f"{float(data.get('weight', 0)):.2f}")

    fig.add_trace(go.Scattergeo(
        lon=mst_weight_lons,
        lat=mst_weight_lats,
        text=mst_weight_text,
        mode='text',
        textfont=dict(size=8, color='black'),
        hoverinfo='skip',
        showlegend=False,
    ))

    # Overlay cut edges
    cut_lons, cut_lats = [], []
    cut_weight_lons, cut_weight_lats, cut_weight_text = [], [], []
    for edge in cut_edges:
        u, v = edge[:2]
        cut_lons.extend([STATE_CENTROIDS[u][1], STATE_CENTROIDS[v][1], None])
        cut_lats.extend([STATE_CENTROIDS[u][0], STATE_CENTROIDS[v][0], None])
        cut_weight_lons.append((STATE_CENTROIDS[u][1] + STATE_CENTROIDS[v][1]) / 2)
        cut_weight_lats.append((STATE_CENTROIDS[u][0] + STATE_CENTROIDS[v][0]) / 2)
        if len(edge) > 2:
            cut_weight_text.append(f"{float(edge[2]):.2f}")
        else:
            cut_weight_text.append('')

    fig.add_trace(go.Scattergeo(
        lon=cut_lons, lat=cut_lats,
        mode='lines',
        line=dict(width=2.5, color='red'),
        name='Cut edges',
    ))

    fig.add_trace(go.Scattergeo(
        lon=cut_weight_lons,
        lat=cut_weight_lats,
        text=cut_weight_text,
        mode='text',
        textfont=dict(size=8, color='red'),
        hoverinfo='skip',
        showlegend=False,
    ))

    fig.update_geos(scope='usa', projection_type='albers usa')
    fig.update_layout(title=f'{rate_type} MST with cut edges. Top {bin_cut} classes cut.', width=1500, height=1000)

    fig.show()


def main():
    # Import graphs
    G_mmr = nx.read_graphml('graphs/mmr_graph.graphml')
    G_imr = nx.read_graphml('graphs/imr_graph.graphml')
    MST_mmr = nx.read_graphml('graphs/mmr_mst.graphml')
    MST_imr = nx.read_graphml('graphs/imr_mst.graphml')

    # Import cut edges
    with open('data/mmr_cut_edges.json', 'r') as f:
        MMR_cut_edges = json.load(f)
    with open('data/imr_cut_edges.json', 'r') as f:
        IMR_cut_edges = json.load(f)

    # Build base MMR map plot
    plot_weighted_graph(build_base_fig(), G_mmr, 'MMR')
    plot_weighted_graph(build_base_fig(), G_imr, 'IMR')

    # Plot MSTs
    plot_mst(build_base_fig(), MST_mmr, MMR_cut_edges[0]['cut_edges'], 'MMR', 3) 
    plot_mst(build_base_fig(), MST_mmr, MMR_cut_edges[1]['cut_edges'], 'MMR', 2) 
    plot_mst(build_base_fig(), MST_mmr, MMR_cut_edges[2]['cut_edges'], 'MMR', 1) 

    plot_mst(build_base_fig(), MST_imr, IMR_cut_edges[0]['cut_edges'], 'IMR', 3) 
    plot_mst(build_base_fig(), MST_imr, IMR_cut_edges[1]['cut_edges'], 'IMR', 2) 
    plot_mst(build_base_fig(), MST_imr, IMR_cut_edges[2]['cut_edges'], 'IMR', 1) 


if __name__ == '__main__':
    main()