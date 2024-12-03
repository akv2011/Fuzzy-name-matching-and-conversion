import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import fuzz, process

app = Flask(__name__)
CORS(app)

# Load and preprocess the dataset
CSV_PATH = './data/data.csv'

def load_and_preprocess_data(csv_path):
    df = pd.read_csv(csv_path)
    # Normalize column names to handle potential formatting issues
    df.columns = df.columns.str.strip().str.lower()
    # Ensure relevant columns are of type string
    df['names'] = df['names'].astype(str)
    df['age'] = df['age'].astype(str)
    df['caseType'] = df['casetype'].astype(str)
    df['casefir'] = df['casefir'].astype(str)
    df['location'] = df['location'].astype(str)
    print("Columns in dataset:", df.columns)  # Debugging column names
    return df

data = load_and_preprocess_data(CSV_PATH)

# Fuzzy search implementation
def search_name(input_name, dataframe):
    input_name = input_name.strip().lower()
    results = []

    for index, row in dataframe.iterrows():
        try:
            # Prepare list of all names to match against (consider names and their variations)
            names_to_match = [row['names']]  # We will match only the 'names' column for now

            # Convert all names to lowercase for case-insensitive matching
            names_to_match = [name.lower() for name in names_to_match]

            # Check for partial substring matches or fuzzy match
            partial_matches = [name for name in names_to_match if input_name in name]

            if partial_matches:
                confidence = 100  # High confidence for exact substring matches
            else:
                matches = [(name, fuzz.partial_ratio(input_name, name)) for name in names_to_match]
                best_match = max(matches, key=lambda x: x[1])  # Get the name with the highest match score
                if best_match[1] > 60:  # Threshold for fuzzy match confidence
                    partial_matches = [best_match[0]]
                    confidence = best_match[1]
                else:
                    continue  # Skip if no good match is found

            # Add all matches as results
            for matched_name in partial_matches:
                results.append({
                    'name': row['names'],
                    'age': row['age'],
                    'case_type': row['caseType'],  # Include case type
                    'fir': row['casefir'],
                    'location': row['location'],
                    'confidence': confidence
                })
        except KeyError as e:
            print(f"KeyError occurred while processing row {index}: {e}")
        except Exception as e:
            print(f"Unexpected error occurred while processing row {index}: {e}")

    # Sort results by confidence score
    results.sort(key=lambda x: x['confidence'], reverse=True)
    return results

# Define the search endpoint
@app.route('/search', methods=['POST'])
def search():
    req_data = request.json
    input_name = req_data.get('name', '').strip()

    print(f"Received name to search: {input_name}")  # Debugging input data

    if not input_name:
        return jsonify({"error": "Name is required"}), 400

    try:
        results = search_name(input_name, data)
        if not results:
            return jsonify({"message": "No results found for the given name."}), 404
        return jsonify({"results": results})
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
