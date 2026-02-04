# Fuzzy-name-matching-and-conversion


A fuzzy matching toolkit for noisy names and transliterations. Includes normalization, phonetic encoding, candidate generation, and ranking to improve recall and precision when matching names with spelling variants and script conversions.

## Highlights
- Name normalization and cleanup utilities
- Phonetic keys for sound-alike matching
- Edit-distance scoring and ranking
- Candidate generation to keep search efficient

## Approach
1. **Normalize** input strings (case, spacing, punctuation, common variants)
2. **Generate phonetic keys** to capture sound-alike matches
3. **Create candidates** using prefixes, phonetic buckets, or blocking
4. **Rank results** using edit distance and weighted scoring

## Project Structure
- `src/` - core matching and conversion logic
- `examples/` - sample inputs and usage
- `tests/` - unit tests (optional)
- `data/` - sample datasets (optional)

## Usage
- Provide two names (or a query and a candidate list)
- The library returns top matches with scores and intermediate signals (optional)

## Performance Notes
- Candidate blocking is used to reduce comparisons
- Scoring can be tuned based on the domain (names, locations, entities)

## License
Add your preferred license.
