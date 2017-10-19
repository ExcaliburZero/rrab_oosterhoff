import pandas as pd

def main():
    table2_f = "table2.tsv"
    table3_f = "table3.tsv"
    output_file = "table_2_and_3.csv"

    id_col = "Name"

    table2 = pd.read_table(table2_f)
    table3 = pd.read_table(table3_f)

    data = pd.merge(table2, table3, on=id_col, how="outer")
    data.to_csv(output_file, index=False)

if __name__ == "__main__":
    main()
