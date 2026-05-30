""" Builds Maternal Mortality Rate and Infant Mortality Rate weighted NetworkX graphs """

import json
import networkx as nx
import matplotlib.pyplot as plt

from constants import STATE_CODE_REF

def build_mmr_graph():
    # read maternal deaths, births, and state adjacecny list files
    with open('state_adjacency_list.json', 'r') as f:
        state_adjacency_list = json.load(f)
    with open('data/maternal_mortality_rate/births_by_state.json', 'r') as f:
        births_by_state = json.load(f)
    with open('data/maternal_mortality_rate/maternal_deaths_by_state.json', 'r') as f:
        maternal_deaths_by_state = json.load(f)

    # compute mmr
    mmr_by_state = compute_mmr(births_by_state, maternal_deaths_by_state)

    # make a copy of the adjacency dict and remove Vermont (VT) if present. Does not delete VT from adjacency lists
    state_adjacency_vt_removed = dict(state_adjacency_list)
    if 'VT' in state_adjacency_vt_removed:
        del state_adjacency_vt_removed['VT']

    # create the weighted networkx graph for mmr
    G = nx.Graph()
    for state in state_adjacency_vt_removed:
        for neighbor in state_adjacency_vt_removed[state]:
            if neighbor != 'VT':
                abs_mmr_diff = abs(mmr_by_state[state] - mmr_by_state[neighbor])
                G.add_edge(state, neighbor, weight=abs_mmr_diff)
    
    # export mmr graph
    nx.write_graphml(G, 'graphs/mmr_graph.graphml', infer_numeric_types=True)

def compute_mmr(births_by_state: dict, maternal_deaths_by_state: dict) -> dict:
    """Computes maternal mortality rate per 100,000 and builds a dict of mmr per state (ex. {'AL': 58.18})"""
    mmr_by_state = {}
    for target_state in STATE_CODE_REF:
        maternal_deaths = next(item['Deaths'] for item in maternal_deaths_by_state if item['State'] == target_state)
        births = next(item['Births'] for item in births_by_state if item['State of Residence'] == target_state)
        computed_mmr = (maternal_deaths / births) * 100000
        mmr_by_state[STATE_CODE_REF[target_state]] = computed_mmr
    return mmr_by_state

def build_imr_graph():
    # read state ajacency list and infant mortality jsons
    with open('state_adjacency_list.json', 'r') as file:
        state_adjacency_list = json.load(file)
    with open('data/infant_mortality_rate/infant_mortality_by_state.json', 'r') as file:
        infant_mortality_by_state = json.load(file)

    # remove vermont bc Wonder 'unreliable' flag. Does not delete VT as neighbor from adjacency lists
    state_adjacency_vt_removed = dict(state_adjacency_list)
    if 'VT' in state_adjacency_vt_removed:
        del state_adjacency_vt_removed['VT']

    # build dift of imr by state code
    imr_by_state = {}
    for target_state in STATE_CODE_REF:
        imr_by_state[STATE_CODE_REF[target_state]] = float(next(item['Death Rate']for item in infant_mortality_by_state if item['State'] == target_state))


    # create the weighted networkx graph for imr
    G = nx.Graph()
    for state in state_adjacency_vt_removed:
        for neighbor in state_adjacency_vt_removed[state]:
            if neighbor != 'VT':
                G.add_edge(state, neighbor, weight=imr_by_state[state])

    # export the graph
    nx.write_graphml(G, 'graphs/imr_graph.graphml', infer_numeric_types=True)


def main():
    build_mmr_graph()
    build_imr_graph()


if __name__ == '__main__':
    main()
