import unittest
import tempfile
import os
from main import process_file
from argparse import Namespace
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import wordnet as wn

nltk.download('wordnet')

class TestSensitiveDataRedactor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for output
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Create a temporary input file with test content
        self.test_input_file = os.path.join(self.test_dir.name, "test_input.txt")
        with open(self.test_input_file, 'w') as f:
            f.write("Dear anna, please call me at (123) 456-7890. "
                     "My email is anna@example.com. I meet you on Sept 21, 2024 at 5 PM.")

    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()

    def test_redact_names(self):
        args = Namespace(
            names=True,
            dates=False,
            phones=False,
            concept=None,
            address=False,
            output=self.test_dir.name,
            input=[self.test_input_file],
            stats=None
        )
        result = process_file(self.test_input_file, args)
        self.assertEqual(result["stats"]["Names_count"], 2)  

    def test_redact_dates(self):
        args = Namespace(
            names=False,
            dates=True,
            phones=False,
            concept=None,
            address=False,
            output=self.test_dir.name,
            input=[self.test_input_file],
            stats=None
        )
        result = process_file(self.test_input_file, args)
        self.assertEqual(result["stats"]["Dates_count"], 1) 

    def test_redact_phones(self):
        args = Namespace(
            names=False,
            dates=False,
            phones=True,
            concept=None,
            address=False,
            output=self.test_dir.name,
            input=[self.test_input_file],
            stats=None
        )
        result = process_file(self.test_input_file, args)
        self.assertEqual(result["stats"]["Phones_count"], 1)  

    def test_redact_concepts(self):
        args = Namespace(
            names=False,
            dates=False,
            phones=False,
            concept="meet",
            address=False,
            output=self.test_dir.name,
            input=[self.test_input_file],
            stats=None
        )
        result = process_file(self.test_input_file, args)
        self.assertEqual(result["stats"]["Concepts_count"], 1) 

    def test_redact_addresses(self):
        # Modify the input file to include an address
        with open(self.test_input_file, 'w') as f:
            f.write("Please send the package to 123 Main St, Springfield, IL 62701.")
        
        args = Namespace(
            names=False,
            dates=False,
            phones=False,
            concept=None,
            address=True,
            output=self.test_dir.name,
            input=[self.test_input_file],
            stats=None
        )
        result = process_file(self.test_input_file, args)
        self.assertEqual(result["stats"]["Addresses_count"], 3) 

if __name__ == "__main__":
    unittest.main()
