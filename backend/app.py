import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import fuzz
from googletrans import Translator
from sqlalchemy import create_engine

app = Flask(__name__)
CORS(app)

# Setup database connection and SQLAlchemy engine
DATABASE_URL = "postgresql://postgres:hari%402004@localhost:5432/Names"
engine = create_engine(DATABASE_URL)

# Initialize the translator
translator = Translator()

# Load and preprocess the dataset
def load_and_preprocess_data():
    query = 'SELECT * FROM "Names_individuals";'
    df = pd.read_sql(query, engine)
    
    # Normalize the column names
    df.columns = df.columns.str.strip().str.lower()
    print("Columns in dataset:", df.columns)  # Debugging column names
    
    # Ensure relevant columns are strings
    df['names'] = df['names'].astype(str)
    df['voter_gender'] = df['voter_gender'].astype(str)
    df['caseType'] = df['casetype'].astype(str)
    df['caseFIR'] = df['casefir'].astype(str)
    df['location'] = df['location'].astype(str)

    return df

# Load the data globally
data = load_and_preprocess_data()

# Function to translate input text
def translate_input(input_text):
    try:
        if input_text.isascii():  # Input is in English
            translated = translator.translate(input_text, src='en', dest='hi').text
        else:  # Input is in Hindi
            translated = translator.translate(input_text, src='hi', dest='en').text
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return input_text  # Fallback to original text

# Function to get real-time suggestions
def get_suggestions(input_text, dataframe, limit=10):
    input_text = input_text.strip().lower()
    translated_text = translate_input(input_text).lower()  # Translate input
    
    suggestions = []

    for _, row in dataframe.iterrows():
        name = row['names'].lower()
        if input_text in name or translated_text in name:
            suggestions.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'location': row.get('location', 'N/A'),
            })
        elif fuzz.partial_ratio(input_text, name) > 60 or fuzz.partial_ratio(translated_text, name) > 60:
            suggestions.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'location': row.get('location', 'N/A'),
            })

    # Sort suggestions by confidence
    suggestions = sorted(suggestions, key=lambda x: max(
        fuzz.partial_ratio(input_text, x['name'].lower()),
        fuzz.partial_ratio(translated_text, x['name'].lower())
    ), reverse=True)
    return suggestions[:limit]

# Define the suggestion endpoint
@app.route('/suggest', methods=['GET'])
def suggest():
    input_text = request.args.get('name', '').strip()
    
    print(f"Real-time suggestion for input: {input_text}")  # Debugging input data
    
    if not input_text:
        return jsonify({"error": "Name input is required"}), 400

    try:
        # Fetch suggestions
        suggestions = get_suggestions(input_text, data)
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        print(f"Error occurred during suggestion generation: {e}")
        return jsonify({"error": str(e)}), 500

# Function to search for a name
def search_name(input_name, dataframe):
    input_name = input_name.strip().lower()
    translated_name = translate_input(input_name).lower()  # Translate input
    results = []

    for _, row in dataframe.iterrows():
        name = row['names'].lower()
        confidence = max(
            fuzz.partial_ratio(input_name, name),
            fuzz.partial_ratio(translated_name, name)
        )
        if confidence > 60:
            results.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'caseType': row.get('casetype', 'N/A'),
                'caseFIR': row.get('casefir', 'N/A'),
                'location': row.get('location', 'N/A'),
                'confidence': confidence,
            })

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






"""import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import fuzz
import psycopg2
from sqlalchemy import create_engine

app = Flask(__name__)
CORS(app)

# Setup database connection and SQLAlchemy engine
DATABASE_URL = "postgresql://postgres:hari%402004@localhost:5432/Names"
engine = create_engine(DATABASE_URL)

# Load and preprocess the dataset
def load_and_preprocess_data():
    query = 'SELECT * FROM "Names_individuals";'
    df = pd.read_sql(query, engine)
    
    # Normalize the column names
    df.columns = df.columns.str.strip().str.lower()
    print("Columns in dataset:", df.columns)  # Debugging column names
    
    # Ensure relevant columns are strings
    df['names'] = df['names'].astype(str)
    df['voter_gender'] = df['voter_gender'].astype(str)
    df['caseType'] = df['casetype'].astype(str)
    df['caseFIR'] = df['casefir'].astype(str)
    df['location'] = df['location'].astype(str)

    return df

# Load the data globally
data = load_and_preprocess_data()

# Function to get real-time suggestions
def get_suggestions(input_text, dataframe, limit=10):
    input_text = input_text.strip().lower()
    suggestions = []

    for _, row in dataframe.iterrows():
        name = row['names'].lower()
        if input_text in name:
            suggestions.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'location': row.get('location', 'N/A'),
            })
        elif fuzz.partial_ratio(input_text, name) > 60:
            suggestions.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'location': row.get('location', 'N/A'),
            })

    # Sort suggestions by confidence
    suggestions = sorted(suggestions, key=lambda x: fuzz.partial_ratio(input_text, x['name'].lower()), reverse=True)
    return suggestions[:limit]

# Define the suggestion endpoint
@app.route('/suggest', methods=['GET'])
def suggest():
    input_text = request.args.get('name', '').strip()
    
    print(f"Real-time suggestion for input: {input_text}")  # Debugging input data
    
    if not input_text:
        return jsonify({"error": "Name input is required"}), 400

    try:
        # Fetch suggestions
        suggestions = get_suggestions(input_text, data)
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        print(f"Error occurred during suggestion generation: {e}")
        return jsonify({"error": str(e)}), 500

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

# Define the search function
def search_name(input_name, dataframe):
    input_name = input_name.strip().lower()
    results = []

    for _, row in dataframe.iterrows():
        name = row['names'].lower()
        confidence = fuzz.partial_ratio(input_name, name)
        if confidence > 60:
            results.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'caseType': row.get('casetype', 'N/A'),  # Fix caseType key
                'caseFIR': row.get('casefir', 'N/A'),    # Fix caseFIR key
                'location': row.get('location', 'N/A'),
                'confidence': confidence,
            })

    results.sort(key=lambda x: x['confidence'], reverse=True)
    return results


if __name__ == "__main__":
    app.run(debug=True, port=5000)
"""
