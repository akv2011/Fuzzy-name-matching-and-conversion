from fuzzywuzzy import fuzz, process

def search_name(input_name, data, confidence_threshold=70):
    """
    Perform fuzzy matching to find relevant records.

    :param input_name: The name input by the user.
    :param data: The dataset as a list of dictionaries.
    :param confidence_threshold: The minimum confidence score to consider a match.
    :return: A list of matching results.
    """
    results = []

    input_name_lower = input_name.lower()

    for record in data:
        # Combine Romanized and alternative spellings for matching
        search_fields = (
            f"{record.get('First Name (Roman)', '')} "
            f"{record.get('Middle Name (Roman)', '')} "
            f"{record.get('Last Name (Roman)', '')} "
            f"{record.get('Alternative Roman Spellings', '')} "
            f"{record.get('First Name (Devanagari)', '')} "
            f"{record.get('Middle Name (Devanagari)', '')} "
            f"{record.get('Last Name (Devanagari)', '')}"
        ).lower()

        # Use fuzzywuzzy to find the best match
        match = process.extractOne(input_name_lower, [search_fields], scorer=fuzz.token_sort_ratio)

        if match and match[1] >= confidence_threshold:
            results.append({
                "name": f"{record.get('First Name (Roman)', '')} {record.get('Middle Name (Roman)', '')} {record.get('Last Name (Roman)', '')}".strip(),
                "nameDevanagari": f"{record.get('First Name (Devanagari)', '')} {record.get('Middle Name (Devanagari)', '')} {record.get('Last Name (Devanagari)', '')}".strip(),
                "gender": "Male" if record.get('Gender') == 1 else "Female",
                "age": record.get("age", "Unknown"),
                "caseType": record.get("caseType", "Unknown"),
                "caseFIR": record.get("caseFIR", "Unknown"),
                "location": record.get("location", "Unknown"),
                "confidence": match[1],
            })

    # Sort results by confidence score in descending order
    results.sort(key=lambda x: x['confidence'], reverse=True)

    return results
