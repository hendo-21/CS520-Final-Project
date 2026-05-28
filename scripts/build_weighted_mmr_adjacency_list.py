import json
import networkx as nx
import matplotlib.pyplot as plt

STATE_CODE_REF = {
    'Alabama': 'AL',
    'Arkansas': 'AR',
    'Arizona': 'AZ',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'District of Columbia': 'DC',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Iowa': 'IA',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Massachusetts': 'MA',
    'Maryland': 'MD',
    'Maine': 'ME',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Missouri': 'MO',
    'Mississippi': 'MS',
    'Montana': 'MT',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Nebraska': 'NE',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'Nevada': 'NV',
    'New York': 'NY',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'Wisconsin': 'WI',
    'West Virginia': 'WV',
    'Wyoming': 'WY',
}

def main():

    # read maternal deaths, births, and state adjacecny list files
    with open('state_adjacency_list.json', 'r') as f:
        state_adjacency_list = json.load(f)
    with open('data/maternal_mortality_rate/births_by_state.json', 'r') as f:
        births_by_state = json.load(f)
    with open('data/maternal_mortality_rate/maternal_deaths_by_state.json', 'r') as f:
        maternal_deaths_by_state = json.load(f)

    # compute mmr
    mmr_by_state = {}
    for target_state in STATE_CODE_REF:
        maternal_deaths = next(item['Deaths'] for item in maternal_deaths_by_state if item['State'] == target_state)
        births = next(item['Births'] for item in births_by_state if item['State of Residence'] == target_state)
        computed_mmr = (maternal_deaths / births) * 100000
        mmr_by_state[STATE_CODE_REF[target_state]] = computed_mmr

    # create the weighted networkx graph for mmr
    # make a copy of the adjacency dict and remove Vermont (VT) if present
    state_adjacency_vt_removed = dict(state_adjacency_list)
    if 'VT' in state_adjacency_vt_removed:
        del state_adjacency_vt_removed['VT']
    G = nx.Graph()
    for state in state_adjacency_vt_removed:
        for neighbor in state_adjacency_vt_removed[state]:
            if neighbor != 'VT':
                abs_mmr_diff = abs(mmr_by_state[state] - mmr_by_state[neighbor])
                G.add_edge(state, neighbor, weight=abs_mmr_diff)
    
    # export mmr graph
    nx.write_graphml(G, 'graphs/mmr_graph.graphml')
    
    '''
    for state in G:
        weighted_neighbors = [f"{neighbor} ({G[state][neighbor]['weight']:.2f})" for neighbor in G.neighbors(state)]
        print(" -> ".join([state, *weighted_neighbors]))

    pos = nx.spring_layout(G)
    labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()
    '''

if __name__ == '__main__':
    main()
