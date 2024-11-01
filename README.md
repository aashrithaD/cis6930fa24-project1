# cis6930fa24 -- Project1

Name: AASHRITHA REDDY DONAPATI

# Assignment Description 
The Redactor is a Python application that effectively identifies and redacts sensitive information in text files, thereby safeguarding confidentiality. It harnesses natural language processing (NLP) through the SpaCy library and semantic insights from WordNet to target various sensitive data types, such as names, dates, phone numbers, concepts, and addresses. Additionally, the application utilizes regular expressions (regex) for precise pattern matching, enabling accurate detection of specific formats, including date and phone number structures, making regex a vital component in the redaction process.

# Expected Outcomes
1. Successful redaction of specified sensitive data from input text files.
2. Generation of detailed statistics regarding the amount and type of data redacted.
3. Preservation of the original text structure while ensuring sensitive information is anonymized.

# Environment Setup

1. Clone the Repository:

    git clone <repository-url>
    cd <folder_name>

2. Install Dependencies:

    pipenv install

3. Download Required Models
   Ensure you have the SpaCy model and NLTK data installed:

    python -m spacy download en_core_web_md
    import nltk
    nltk.download('wordnet')

## How to run

1. To execute the Sensitive Data Redactor:

pipenv run python file_name.py --input '*.txt' \
                    --names --dates --phones --address\
                    --concept 'concept_name' \
                    --output 'files/' \
                    --stats stderr

## Options:

- `--input`: Specify input files using glob patterns.
- `--output`: Specify the output directory for censored files.
- `--names`: corresponds to any type of name, it is up to you to define this.
- `--dates`: correspond to any written dates (4/9/2025, April 9th, 22/2/22, etc.)
- `--phones`: describes any phone number in its various forms.
- `--address`: corresponds to any physical (postal) address (not e-mail address).
- `--concept`: corresponds to any concept you specify.
- `--stats`: Choose statistics output destination (`stderr`, `stdout`, or a file path)

2. To run the test cases:  
pipenv run python -m pytest -v   

## The stdout/stderr Format

The program can output statistics to:
1. A specified file.
2. The standard output (stdout).
3. The standard error (stderr).

The output format for statistics is as follows:
```sh
Statistics of Redacted Files:  
File: <filename>  
Names_count: <count>  
Dates_count: <count>  
Phones_count: <count>  
Concepts_count: <count>  
Addresses_count: <count>
``` 

EXAMPLE:

1. pipenv run python main.py --input '*.txt' \
                    --names --dates --phones --address\
                    --concept 'kids' \
                    --output 'files/' \
                    --stats stderr

input: "Dear Alice Johnson, your appointment is scheduled for February 5, 2024, at 456 Maple Avenue, Springfield. If you have any questions, please call us at (123) 456-7890. Additionally, the community event for kids will be held next Saturday at the park."
 
output: "Dear █████████████, your appointment is scheduled for ████████████████, at ███ ████████████, ███████████. If you have any questions, please call us at ██████████████. ██████████████████████████████████████████████████████████████████████████████████"

## Video  
https://github.com/user-attachments/assets/92f4ef80-e87f-45fd-97fc-1caea55745f0

## Functions

#### main.py

1. **main()**: The `main` function handles command-line arguments, processes each input file for sensitive data redaction, collects statistics, and outputs the results, including error handling for file processing.

#### redactor.py

1. **redact_names(text, stats)**: Identifies and redacts names, initials, and emails in the text.
```sh
Args: 
text (str): The input text to redact.
stats (dict): A dictionary to track the count of redacted names.

Return: (str) The text with names redacted.
```

2. **redact_dates(text, stats)**: Identifies and redacts dates in various formats within the text.
```sh
Args:
text (str): The input text to redact.
stats (dict): A dictionary to track the count of redacted dates.

Return: (str) The text with dates redacted.
```
    
3. **redact_phones(text, stats)**: Identifies and redacts phone numbers in various formats within the text.
```sh
Args:
text (str): The input text to redact.
stats (dict): A dictionary to track the count of redacted phone numbers.

Return: (str) The text with phone numbers redacted.
```

4. **redact_address(text, stats)**: Identifies and redacts addresses based on SpaCy entity recognition and regex patterns.
```sh
Args:
text (str): The input text to redact.
stats (dict): A dictionary to track the count of redacted addresses.

Return: (str) The text with addresses redacted.
```

5. **word_similarity(term1, term2)**: Computes the Wu-Palmer similarity score between two terms using WordNet.
```sh
Args:
term1 (str): The first term to compare.
term2 (str): The second term to compare.

Return: (float) The similarity score between the two terms (0 to 1).
```

6. **get_similar_terms(concept, threshold=0.4)**: Generates a set of terms similar to a given concept using WordNet synonyms and hyponyms.
```sh
Args:
concept (str): The base concept to find similar terms for.
threshold (float, optional): Similarity threshold for including terms. Default is 0.4.

Return: (set) A set of terms similar to the given concept.
```

7. **redact_concepts(text, concept, stats)**: Redacts sentences in the text containing terms similar to a specified concept.
```sh
Args:
text (str): The input text to redact.
concept (str): The base concept to redact related terms.
stats (dict): A dictionary to track the count of redacted concepts.

Return: (str) The text with sentences containing the concept redacted.
```

8. **parse_arguments()**: Parses command-line arguments for the script.
```sh
Return: Parsed command-line arguments.
```

9. **output_stats(statistics, stats_output)**: Outputs redaction statistics to stdout, stderr, or a specified file.
```sh
Args:
statistics (list of dict): List of stats dictionaries for each file processed.
stats_output (str): Output destination for the statistics ("stdout", "stderr", or a file path).
```

10. **process_file(file_path, args)**: Processes a single file by applying redaction functions and saving the results.
```sh
Args:
file_path (str): Path of the file to be processed.
args (argparse.Namespace): Parsed arguments specifying redaction options.

Return: (dict) A dictionary with the filename and redaction stats.
```

### test_redactor.py

1. **test_redact_names(self)**: Tests the process_file function to ensure it correctly redacts names from the input text.

2. **test_redact_dates(self)**: Tests the process_file function to check if it correctly redacts dates from the input text.

3. **test_redact_phones(self)**: Tests the process_file function to verify it accurately redacts phone numbers from the input text.

4. **test_redact_concepts(self)**: Tests the process_file function to ensure it properly redacts specified concepts from the input text.

5. **test_redact_addresses(self)**: Tests the process_file function to check if it effectively redacts addresses from the modified input text.

## Bugs and Assumptions

Assumptions:

1. A similarity threshold of 0.4 is used for determining semantic similarity between words.
2. Names are redacted, including initials (e.g., "Sean A. O'Brien") and alphanumeric identifiers are ignored
3. Assumed that any text following greeting words (such as 'Dear,' 'Hello,' 'Hi,' or 'Greetings') is a name
4. Assumed that all content preceding the '@' symbol in email addresses is considered sensitive information and will be redacted when the 'names' flag is specified, as this content typically contains names.
5. Dates are recognized in formats such as "12/04/2023", "2023-04-12", "12-05-2024", "12/29/00", "April 12, 2023", "12th April 2023", "2023/04/12", "12.04.23", "04-12-23", "Monday, April 12th, 2023", "April 2000", and standalone years between 1900 and 2025.
6. Phone numbers are redacted in formats like "(123) 456-7890", "+1 (123) 456-7890", "123 456 7890", "1234567890", "+11234567890", and "123-456-7890 x1234.
7. Addresses are identified in formats like "123 Main St", "123 Main St, Springfield, IL 62701", and standalone ZIP codes (e.g., "62701").
8. Concepts are redacted using synonyms and hyponyms sourced from WordNet, including their stemmed variations.
9. Assumed that sentences are split based on !, ., and ? when redacting concepts.
10. Assumed that if the text contains both a first name and a last name, they are redacted as a single entity.

Bugs:

1. Some names that are part of longer words or contain underscores are not redacted correctly.
2. Terms like "cc" and "bcc" are occasionally treated as names.
3. The word "thu" is sometimes incorrectly identified as a name.
4. Addresses are not redacted properly when they include elements like floor numbers, country or state or city codes, or specific identifiers such as "502" in "502 Blvd, Downtown."
5. Names stats are counted twice because they are counted based on both regex match and SpaCy
