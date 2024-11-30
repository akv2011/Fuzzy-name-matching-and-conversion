from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from fuzzywuzzy import process

app = Flask(__name__)
CORS(app)

# Load CSV data
CSV_PATH = './data/updated_file.csv'  # Update this with the correct file path
data = pd.read_csv(CSV_PATH)

# Define a search function
def search_name(input_name):
    results = []
    # Check against First Name, Last Name, and Alternative Roman Spellings
    for _, row in data.iterrows():
        # Combine all searchable columns
        search_fields = f"{row['First Name (Roman)']} {row['Last Name (Roman)']} {row['Alternative Roman Spellings']}"
        match = process.extractOne(input_name, [search_fields])
        
        if match and match[1] > 70:  # Match confidence threshold
            results.append({
                "name": f"{row['First Name (Roman)']} {row['Last Name (Roman)']}",
                "age": row['age'],
                "caseType": row['caseType'],
                "caseFIR": row['caseFIR'],
                "location": row['location'],
                "confidence": match[1],
            })
    return results

# API endpoint for search
@app.route('/search', methods=['POST'])
def search():
    req_data = request.json
    input_name = req_data.get('name', '')
    if not input_name:
        return jsonify({"error": "Name is required"}), 400

    results = search_name(input_name)
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
