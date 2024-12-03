import pandas as pd

def load_data(csv_path):
    """
    Load data from a CSV file.

    :param csv_path: Path to the CSV file.
    :return: A list of dictionaries containing the data.
    """
    try:
        data = pd.read_csv(csv_path)
        data.fillna('', inplace=True)  # Fill NaN values with empty strings
        return data.to_dict(orient="records")  # Convert DataFrame to list of dictionaries
    except Exception as e:
        raise Exception(f"Error loading CSV file: {e}")

