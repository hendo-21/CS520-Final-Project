import json
from scripts.constants import STATE_ADJACENCY


def main():
    state_adjacency = {}
    for state in STATE_ADJACENCY:
        state_adjacency[state["code"]] = state["Neighborcodes"]

    with open('state_adjacency_list.json', 'w') as file:
        json.dump(state_adjacency, file, indent=4)


if __name__ == '__main__':
    main()
