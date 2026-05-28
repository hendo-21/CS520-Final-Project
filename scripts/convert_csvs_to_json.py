import pandas as pd

def main():
    #---------------------------------------------------------
    # MMR
    #---------------------------------------------------------

    # Load CSV and convert to JSON
    df = pd.read_csv('data/maternal_mortality_rate/Death.csv')

    # 'records' orientation creates a list of objects (most common format)
    df.to_json('data/maternal_mortality_rate/Death.json', orient='records', indent=4)

    # Load CSV and convert to JSON
    df = pd.read_csv('data/maternal_mortality_rate/Natality.csv')

    # 'records' orientation creates a list of objects (most common format)
    df.to_json('data/maternal_mortality_rate/Natality.json', orient='records', indent=4)

    #---------------------------------------------------------
    # IMR
    #---------------------------------------------------------
    # Load CSV and convert to JSON
    df = pd.read_csv('data/infant_mortality_rate/Linked Birth  Infant Death Records, 2017-2023 Expanded.csv')

    # 'records' orientation creates a list of objects (most common format)
    df.to_json('data/infant_mortality_rate/infant_mortality_by_state.json', orient='records', indent=4)

if __name__ == '__main__':
    main()
