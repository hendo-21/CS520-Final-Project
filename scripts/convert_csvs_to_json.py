import pandas as pd

def main():
    # Load CSV and convert to JSON
    df = pd.read_csv('data/maternal_mortality_rate/Death.csv')

    # 'records' orientation creates a list of objects (most common format)
    df.to_json('data/maternal_mortality_rate/Death.json', orient='records', indent=4)

    # Load CSV and convert to JSON
    df = pd.read_csv('data/maternal_mortality_rate/Natality.csv')

    # 'records' orientation creates a list of objects (most common format)
    df.to_json('data/maternal_mortality_rate/Natality.json', orient='records', indent=4)


if __name__ == '__main__':
    main()
