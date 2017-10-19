import pandas as pd

def main():
    data_file = "asu.tsv"

    data = pd.read_table(data_file)

    data.to_csv(data_file, index=False)

if __name__ == "__main__":
    main()
