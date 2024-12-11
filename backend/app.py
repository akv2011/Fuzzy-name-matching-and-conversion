import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from googletrans import Translator
from rapidfuzz import fuzz
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pyphonetics import Soundex  # Correct import

app = Flask(__name__)
CORS(app)

# Setup database connection and SQLAlchemy engine
DATABASE_URL = "postgresql://postgres:hari%402004@localhost:5432/Names"
engine = create_engine(DATABASE_URL)

# Initialize the translator and Soundex encoder
translator = Translator()
soundex = Soundex()

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
    df['casetype'] = df['casetype'].astype(str)
    df['casefir'] = df['casefir'].astype(str)
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

# Function to get phonetic code
def get_phonetic_code(name):
    try:
        return soundex.phonetics(name)
    except Exception as e:
        print(f"Error generating phonetic code for {name}: {e}")
        return None

# Function to get real-time suggestions
def get_suggestions(input_text, dataframe, limit=10):
    input_text = input_text.strip().lower()
    translated_text = translate_input(input_text).lower()  # Translate input
    
    input_phonetic = get_phonetic_code(input_text)  # Get phonetic code
    suggestions = []

    for _, row in dataframe.iterrows():
        name = row['names'].lower()
        name_phonetic = get_phonetic_code(name)

        if input_text in name or translated_text in name:
            suggestions.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'location': row.get('location', 'N/A'),
            })
        elif (
            fuzz.partial_ratio(input_text, name) > 60 or 
            fuzz.partial_ratio(translated_text, name) > 60 or
            (input_phonetic and name_phonetic and input_phonetic == name_phonetic)
        ):
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
    input_phonetic = get_phonetic_code(input_name)  # Get phonetic code

    results = []

    for _, row in dataframe.iterrows():
        name = row['names'].lower()
        name_phonetic = get_phonetic_code(name)

        confidence = max(
            fuzz.partial_ratio(input_name, name),
            fuzz.partial_ratio(translated_name, name)
        )

        if confidence > 60 or (input_phonetic and name_phonetic and input_phonetic == name_phonetic):
            results.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'casetype': row.get('casetype', 'N/A'),
                'casefir': row.get('casefir', 'N/A'),
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

# Define the add record endpoint
@app.route('/add-record', methods=['POST'])
def add_record():
    try:
        record_data = request.json
        name = record_data.get('name', '').strip()
        age = record_data.get('age', '').strip()
        location = record_data.get('location', '').strip()
        casetype = record_data.get('casetype', '').strip()

        # Validate required fields
        if not name or not age or not location or not casetype:
            return jsonify({"error": "All fields (name, age, location, casetype) are required."}), 400

        # Insert the record into the database
        query = f"""
        INSERT INTO "Names_individuals" (names, age, location, casetype)
        VALUES ('{name}', {int(age)}, '{location}', '{casetype}')
        RETURNING *;
        """
        result = engine.execute(query).fetchone()
        if result:
            return jsonify({"message": "Record added successfully.", "record": dict(result)}), 201
        else:
            return jsonify({"error": "Failed to add the record."}), 500

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error adding record: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)


"""import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from googletrans import Translator
from rapidfuzz import fuzz
from sqlalchemy import create_engine
from pyphonetics import Soundex  # Correct import

app = Flask(__name__)
CORS(app)

# Setup database connection and SQLAlchemy engine
DATABASE_URL = "postgresql://postgres:hari%402004@localhost:5432/Names"
engine = create_engine(DATABASE_URL)

# Initialize the translator and Soundex encoder
translator = Translator()
soundex = Soundex()

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

# Function to get phonetic code
def get_phonetic_code(name):
    try:
        return soundex.phonetics(name)
    except Exception as e:
        print(f"Error generating phonetic code for {name}: {e}")
        return None

# Function to get real-time suggestions
def get_suggestions(input_text, dataframe, limit=10):
    input_text = input_text.strip().lower()
    translated_text = translate_input(input_text).lower()  # Translate input
    
    input_phonetic = get_phonetic_code(input_text)  # Get phonetic code
    suggestions = []

    for _, row in dataframe.iterrows():
        name = row['names'].lower()
        name_phonetic = get_phonetic_code(name)

        if input_text in name or translated_text in name:
            suggestions.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'location': row.get('location', 'N/A'),
            })
        elif (
            fuzz.partial_ratio(input_text, name) > 60 or 
            fuzz.partial_ratio(translated_text, name) > 60 or
            (input_phonetic and name_phonetic and input_phonetic == name_phonetic)
        ):
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
    input_phonetic = get_phonetic_code(input_name)  # Get phonetic code

    results = []

    for _, row in dataframe.iterrows():
        name = row['names'].lower()
        name_phonetic = get_phonetic_code(name)

        confidence = max(
            fuzz.partial_ratio(input_name, name),
            fuzz.partial_ratio(translated_name, name)
        )

        if confidence > 60 or (input_phonetic and name_phonetic and input_phonetic == name_phonetic):
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
"""






"""import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from googletrans import Translator
from rapidfuzz import fuzz
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
"""






"""import pandas as pd
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
"""