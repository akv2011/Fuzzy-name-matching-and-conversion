import pandas as pd
import datetime
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from googletrans import Translator
from rapidfuzz import fuzz
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from pyphonetics import Soundex

app = Flask(__name__)
CORS(app)

# Setup database connection and SQLAlchemy engine
DATABASE_URL = "postgresql://postgres:hari%402004@localhost:5432/Names"
engine = create_engine(DATABASE_URL)

# Create a session factory
Session = sessionmaker(bind=engine)

# Initialize the translator and Soundex encoder
translator = Translator()
soundex = Soundex()

def generate_fir_number():
    """Generate a unique FIR number based on current date and random number"""
    current_date = datetime.datetime.now()
    date_str = current_date.strftime("%Y%m%d")
    random_num = random.randint(1000, 9999)
    return f"FIR{date_str}{random_num}"

# Load and preprocess the dataset
def load_and_preprocess_data():
    query = 'SELECT * FROM "Names_individuals";'
    df = pd.read_sql(query, engine)
    
    # Normalize the column names
    df.columns = df.columns.str.strip().str.lower()
    print("Columns in dataset:", df.columns)
    
    # Ensure relevant columns are strings
    df['names'] = df['names'].astype(str)
    df['voter_gender'] = df['voter_gender'].astype(str) if 'voter_gender' in df.columns else ''
    df['casetype'] = df['casetype'].astype(str)
    df['casefir'] = df['casefir'].astype(str) if 'casefir' in df.columns else ''
    df['location'] = df['location'].astype(str)

    return df

# Load the data globally
data = load_and_preprocess_data()

def translate_input(input_text):
    try:
        if input_text.isascii():
            translated = translator.translate(input_text, src='en', dest='hi').text
        else:
            translated = translator.translate(input_text, src='hi', dest='en').text
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return input_text

def get_phonetic_code(name):
    try:
        return soundex.phonetics(name)
    except Exception as e:
        print(f"Error generating phonetic code for {name}: {e}")
        return None

def get_suggestions(input_text, dataframe, limit=10):
    input_text = input_text.strip().lower()
    translated_text = translate_input(input_text).lower()  # Translate input
    
    input_phonetic = get_phonetic_code(input_text)  # Get phonetic code
    suggestions = []

    for _, row in dataframe.iterrows():
        name = row['names'].lower()
        name_phonetic = get_phonetic_code(name)
        
        partial_ratio_score = max(
            fuzz.partial_ratio(input_text, name),
            fuzz.partial_ratio(translated_text, name)
        )

        # Calculate a prefix score. Give priority to first three letters
        prefix_score = 0
        if name.startswith(input_text) or name.startswith(translated_text):
            prefix_score = 100  # Max score if name starts with input
        elif name[:3] == input_text[:3] or name[:3] == translated_text[:3]:
            prefix_score = 50 # Moderate score if first 3 letters match
        
        total_score = partial_ratio_score + prefix_score
        

        if partial_ratio_score > 60 or (input_phonetic and name_phonetic and input_phonetic == name_phonetic):
            suggestions.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'location': row.get('location', 'N/A'),
                 'score': total_score
            })

    # Sort suggestions by score
    suggestions = sorted(suggestions, key=lambda x: x['score'], reverse=True)
    
    return [sugg for sugg in suggestions[:limit] ]

@app.route('/suggest', methods=['GET'])
def suggest():
    input_text = request.args.get('name', '').strip()
    print(f"Real-time suggestion for input: {input_text}")
    
    if not input_text:
        return jsonify({"error": "Name input is required"}), 400

    try:
        suggestions = get_suggestions(input_text, data)
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        print(f"Error occurred during suggestion generation: {e}")
        return jsonify({"error": str(e)}), 500

def search_name(input_name, dataframe):
    input_name = input_name.strip().lower()
    translated_name = translate_input(input_name).lower()  # Translate input
    input_phonetic = get_phonetic_code(input_name)  # Get phonetic code

    results = []

    for _, row in dataframe.iterrows():
        name = row['names'].lower()
        name_phonetic = get_phonetic_code(name)
        
        partial_ratio_score = max(
            fuzz.partial_ratio(input_name, name),
            fuzz.partial_ratio(translated_name, name)
        )
        
        # Calculate a prefix score
        prefix_score = 0
        if name.startswith(input_name) or name.startswith(translated_name):
            prefix_score = 100  # Max score if name starts with input
        elif name[:3] == input_name[:3] or name[:3] == translated_name[:3]:
            prefix_score = 50 # Moderate score if first 3 letters match
            
        total_score = partial_ratio_score + prefix_score


        if total_score > 60 or (input_phonetic and name_phonetic and input_phonetic == name_phonetic):
            results.append({
                'name': row['names'],
                'age': row.get('age', 'N/A'),
                'casetype': row.get('casetype', 'N/A'),
                'casefir': row.get('casefir', 'N/A'),
                'location': row.get('location', 'N/A'),
                'confidence': total_score,
            })

    results.sort(key=lambda x: x['confidence'], reverse=True)
    return results

@app.route('/search', methods=['POST'])
def search():
    req_data = request.json
    input_name = req_data.get('name', '').strip()
    print(f"Received name to search: {input_name}")

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

@app.route('/add-record', methods=['POST'])
def add_record():
     try:
        record_data = request.json
        name = record_data.get('name', '').strip()
        age = record_data.get('age', '').strip()
        location = record_data.get('location', '').strip()
        caseType = record_data.get('caseType', '').strip()
        gender = record_data.get('gender', '').strip()
        caseFIR = record_data.get('caseFIR', '').strip()

        if not name or not age or not location or not caseType or not gender:
            return jsonify({"error": "All fields (name, age, location, caseType, gender) are required."}), 400

        session = Session()
        try:
            # Generate FIR number if not provided
            fir_number = caseFIR if caseFIR else generate_fir_number()

            # Handle age conversion more gracefully
            try:
                age = int(age)
            except ValueError:
                return jsonify({"error": "Age must be a valid number."}), 400

            # Format the record for database insertion
            db_record = {
                'names': name,
                'age': age,
                'location': location,
                'casetype': caseType.lower(),
                'casefir': fir_number,
                'voter_gender': gender
            }

            # Print the formatted record
            print(f"Formatted record for DB: {db_record}")

            # Use SQLAlchemy text() function for raw SQL
            sql = text("""
                INSERT INTO "Names_individuals" (names, age, location, casetype, casefir, voter_gender)
                VALUES (:names, :age, :location, :casetype, :casefir, :voter_gender)
                RETURNING names, age, location, casetype, casefir, voter_gender;
            """)
            
            result = session.execute(sql, db_record)
            inserted_record = result.fetchone()
            session.commit()

             # Format response record
            response_record = {
                'name': inserted_record.names,
                'age': inserted_record.age,
                'location': inserted_record.location,
                'caseType': inserted_record.casetype.capitalize(),
                'caseFir': inserted_record.casefir,
                'gender': inserted_record.voter_gender,
                'confidence': 100
            }


            return jsonify({
                "message": "Record added successfully.",
               "record": response_record,
            }), 201
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Detailed Database error: {str(e)}")
            return jsonify({"error": f"Database error occurred: {str(e)}"}), 500
        finally:
            session.close()

     except Exception as e:
            print(f"General error: {str(e)}")
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