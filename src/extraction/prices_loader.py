import pandas as pd


def extract_prices_data(file_path: str) -> pd.DataFrame:
    """
    Load the sell prices dataset from a CSV file.
    """
    df = pd.read_csv(file_path)
    return df


if __name__ == "__main__":
    df = extract_prices_data("data/raw/sell_prices.csv")

    print("Prices shape:", df.shape)
    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())