import pandas as pd


def extract_sales_data(file_path):
    df = pd.read_csv(file_path)
    return df


if __name__ == "__main__":
    file_path = "data/sales.csv"

    df = extract_sales_data(file_path)

    print("\nDataset Shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nFirst 5 Rows:")
    print(df.head())

    print("\nMissing Values:")
    print(df.isnull().sum())