import spacy
import argparse
import os
import sys
import glob
import re
import nltk
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import wordnet as wn

nltk.download('wordnet')
nlp = spacy.load("en_core_web_md")

# Redact names from the text and update the stats
def redact_names(text, stats):
    doc = nlp(text)

    # Handle greetings followed by names 
    greeting_regex_pattern = r'\b(Dear|Hello|Hi|Greetings)\s+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?)\b'  
    text, greeting_count = re.subn(greeting_regex_pattern, 
        lambda match: f"{match.group(1)} " + "█" * len(match.group(2).replace(" ", "")), text) 
    stats['Names_count'] += greeting_count  

    # Redact names with initials (e.g., "Sean A. O'Brien")
    name_with_initial_pattern = r'\b([A-Z][a-z]+)\s([A-Z]\.)\s([A-Z][a-zA-Z\']+)\b'
    text, initial_count = re.subn(name_with_initial_pattern,
        lambda match: "█" * (len(match.group(1)) + len(match.group(2)) + len(match.group(3)) + 2), text)
    stats['Names_count'] += initial_count 

    # General pattern to detect alphanumeric identifiers
    identifier_pattern = r'\b[A-Za-z]+[-_]?[0-9]+[A-Za-z0-9-]*\b'
    text = re.sub(identifier_pattern, lambda match: match.group(0), text)

    # Redacting before "@" in email addresses
    email_pattern = r'([a-zA-Z0-9._%+-]+(?:\'[a-zA-Z0-9._%+-]+)*)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    found_emails = re.findall(email_pattern, text)
    text = re.sub(email_pattern, lambda match: "█" * len(match.group(1)) + "@" + match.group(2), text)
    stats['Names_count'] += len(found_emails)  

    # Redact `PERSON` entities only
    for entity in doc.ents:
        if entity.label_ == "PERSON" and not re.search(identifier_pattern, entity.text):
            stats['Names_count'] += 1
            text = re.sub(rf'\b{re.escape(entity.text)}\b', "█" * len(entity.text), text)

    return text

# Redact date formats from the text and update the stats
def redact_dates(text, stats):

    # Specific date patterns to redact based on exact formats provided
    date_patterns = [
        r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b', 
        r'\b\d{2}/\d{2}/\d{4}\b',                     # e.g., 12/04/2023
        r'\b\d{4}-\d{2}-\d{2}\b',                     # e.g., 2023-04-12
        r'\b\d{2}-\d{2}-\d{4}\b',                     # e.g., 12-05-2024
        r'\b\d{2}/\d{2}/\d{2}\b',                     # e.g., 12/29/00
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',  # e.g., April 12, 2023
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',  # e.g., 12th April 2023
        r'\b\d{4}/\d{2}/\d{2}\b',                     # e.g., 2023/04/12
        r'\b\d{2}\.\d{2}\.\d{2}\b',                   # e.g., 12.04.23
        r'\b\d{2}-\d{2}-\d{2}\b',                     # e.g., 04-12-23
        r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',  # e.g., Monday, April 12th, 2023
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',  # e.g., April 2000
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}\b',  # e.g., May 30
        r'\b(?:19[0-9]{2}|20[0-2][0-5])\b',            # Standalone years from 1900 to 2025
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        stats['Dates_count'] += len(matches)
        text = re.sub(pattern, lambda match: "█" * len(match.group(0)), text, flags=re.IGNORECASE)

    return text

# Redact phone numbers from the text and update the stats
def redact_phones(text, stats):
    # Patterns for phone numbers
    phone_patterns = [
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',                           # Standard 10-digit formats: 123-456-7890
        r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b',                             # Format with parentheses: (123) 456-7890
        r'\b\+?[1-9]{1,2}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', # International format: +1 (123) 456-7890
        r'\b\d{3}\s\d{3}\s\d{4}\b',                                     # Spaced format: 123 456 7890
        r'\b\d{10}\b',                                                  # Continuous standard format without spaces: 1234567890
        r'\b\+?[1-9]{1,2}\d{10}\b',                                    # Continuous international format: +11234567890
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}(?:\s?(?:x|ext\.?)\s?\d{1,5})?\b' # With extensions: 123-456-7890 x1234
    ]

    # Combine patterns into a single regex
    combined_pattern = '|'.join(f'({pattern})' for pattern in phone_patterns)

    # Iterate through all matches in the text
    for match in re.finditer(combined_pattern, text):
        matched_number = match.group(0)
        stats['Phones_count'] += 1

        text = text.replace(matched_number, "█" * len(matched_number))

    return text

# Redact addresses from the text and update the stats
def redact_address(text, stats):
    # Use SpaCy to identify GPE, LOC, and FAC entities
    doc = nlp(text)

    for entity in doc.ents:
        if entity.label_ in ["GPE", "LOC", "FAC"]:
            stats['Addresses_count'] +=1
            text = re.sub(rf'\b{re.escape(entity.text)}\b', "█" * len(entity.text), text)

    # Define regex patterns for specific address formats
    address_patterns = [
        r'\b\d{1,5}\s(?:[A-Za-z]+\s)*(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Lane|Ln|Way|Plaza|Square|Place|Court|Ct|Crescent|Cres|Circle|Cir)\b',  # Basic street address
        r'\b\d{1,5}\s(?:[A-Za-z]+\s)*\d{5}(?:-\d{4})?\b',  # Address with ZIP code
        r'\b\d{5}\b'  # Standalone ZIP code
        ]

    # Apply each regex pattern for address formats
    for pattern in address_patterns:
        matches = re.findall(pattern, text)
        stats['Addresses_count'] += len(matches)  
        text = re.sub(pattern, lambda match: "█" * len(match.group(0)), text, flags=re.IGNORECASE)

    return text

# Calculate the Wu-Palmer similarity between two terms
def word_similarity(term1, term2):
    syn1 = wn.synsets(term1)
    syn2 = wn.synsets(term2)

    if syn1 and syn2:
        return syn1[0].wup_similarity(syn2[0])  # Wu-Palmer Similarity
    return 0

# Retrieve similar terms for a given concept using WordNet
def get_similar_terms(concept, threshold=0.4):
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    similar_terms = set()
    base_term = lemmatizer.lemmatize(concept.lower())
    stemmed_term = stemmer.stem(base_term)
    similar_terms.add(stemmed_term) 

    for syn in wn.synsets(base_term):
        for lemma in syn.lemmas():
            similar_terms.add(lemma.name().replace("_", " "))  # Add synonym to set

    # Adding hyponyms
    for syn in wn.synsets(base_term):
        for hypo in syn.hyponyms():
            for lemma in hypo.lemmas():
                term = lemma.name().replace("_", " ")
                if word_similarity(term, base_term) >= 0.4:
                    similar_terms.add(term)

    # Add stemmed variations of synonyms
    stemmed_similar_terms = {stemmer.stem(term) for term in similar_terms}
    similar_terms.update(stemmed_similar_terms)

    return similar_terms

# Redact concepts from the text based on similar terms and update the stats
def redact_concepts(text, concept, stats):
    if not concept:
        return text

    similar_terms = get_similar_terms(concept)
    similar_terms = {term.lower() for term in similar_terms}  # Convert to lower case
    redacted_lines = []
    found_terms = []

    similar_pattern = r'\b(' + '|'.join(similar_terms) + r')(s|es|ing)?\b'  # Matches the base word and its variations

    lines = text.splitlines()

    for line in lines:
        sentences = re.split(r'(?<=[.!?]) +|(?<=\.\.\.)', line)  # Split on '.', '?', '!', or '...'
        redacted_sentences = []

        for sentence in sentences:
            # Check if any term in the sentence matches the similar terms
            match = re.search(similar_pattern, sentence.lower())
            if match:
                stats['Concepts_count'] += 1
                found_terms.append(match.group(0))  
                redacted_sentences.append("█" * len(sentence))  
            else:
                redacted_sentences.append(sentence)

        # Rejoin redacted sentences into a single line
        redacted_lines.append(" ".join(redacted_sentences))

    print("Found similar words:", set(found_terms))  

    return "\n".join(redacted_lines)  

# Parse command-line arguments for the script
def parse_arguments():
    parser = argparse.ArgumentParser(description="Sensitive Data Redactor - Redacts Names, Dates, Phone Numbers, Concepts, and Addresses")
    parser.add_argument('--input', type=str, nargs='+', required=True, help="Input files")
    parser.add_argument('--output', type=str, required=True, help="Directory for censored files")
    parser.add_argument('--names', action='store_true', help="Redact names")
    parser.add_argument('--dates', action='store_true', help="Redact dates")
    parser.add_argument('--phones', action='store_true', help="Redact phone numbers")
    parser.add_argument('--concept', type=str, help="Concept to redact related terms")
    parser.add_argument('--address', action='store_true', help="Redact addresses") 
    parser.add_argument('--stats', type=str, help="Output file for stats (use 'stdout' or 'stderr' for standard output)")
    return parser.parse_args()

# Output the statistics of redacted files to the specified destination
def output_stats(statistics, stats_output):
    output = []
    output.append("Statistics of Redacted Files:")
    for stat in statistics:
        output.append(f"File: {stat['filename']}")
        for key, value in stat["stats"].items():
            output.append(f"{key}: {value}")
        output.append("\n")

    output_text = "\n".join(output)
    if stats_output == 'stdout':
        print(output_text)
    elif stats_output == 'stderr':
        print(output_text, file=sys.stderr)
    else:
        with open(stats_output, 'w') as file:
            file.write(output_text)

# Process a given file to redact sensitive information 
def process_file(file_path, args):

    if not os.path.exists(args.output):
        os.makedirs(args.output)
        
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    stats = {
        "Names_count": 0,
        "Dates_count": 0,
        "Phones_count": 0,
        "Concepts_count": 0,
        "Addresses_count": 0,
    }

    if args.names:
        text = redact_names(text, stats)
    if args.dates:
        text = redact_dates(text, stats)
    if args.phones:
        text = redact_phones(text, stats)
    if args.concept:
        text = redact_concepts(text, args.concept, stats)
    if args.address:
        text = redact_address(text, stats)

    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    censored_filename = base_filename + ".censored"
    censored_path = os.path.join(args.output, censored_filename)

    with open(censored_path, 'w', encoding='utf-8') as file:
        file.write(text)

    return {
        "filename": censored_filename,
        "stats": stats,
    }

def main():
    args = parse_arguments()
    statistics = []

    for pattern in args.input:
        for file_path in glob.glob(pattern):
            try:
                stats = process_file(file_path, args)
                statistics.append(stats)
            except Exception as e:
                print(f"Error processing {file_path}: {e}", file=sys.stderr)

    if args.stats:
        output_stats(statistics, args.stats)

if __name__ == "__main__":
    main()