import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

NLTK_DATA_PATH = "/Users/ayushmanraj/nltk_data"

nltk.data.path.insert(0, NLTK_DATA_PATH)

REQUIRED_RESOURCES = {

    "corpora/stopwords": "stopwords",

    "corpora/wordnet": "wordnet",

    "tokenizers/punkt_tab": "punkt_tab",

}

def ensure_nltk_resources():
    """
    Ensure that the required NLTK resources are downloaded.
    """
    failed = []
    for resource_path, package in REQUIRED_RESOURCES.items():
        try:
            nltk.data.find(resource_path)
        except LookupError:
            try:
                nltk.download(package)
                nltk.data.find(resource_path)  # Verify download
            except Exception as e:
                failed.append(package)
                print(f"Failed to download {package}: {e}")
    return failed

ensure_nltk_resources()
lemmatizer = WordNetLemmatizer()

def preprocess_text(text: str) -> str:
    """
    Preprocess input text using:
    1. Lowercase
    2. Tokenization
    3. Stopword removal
    4. Punctuation removal
    5. Lemmatization
    6. Whitespace normalization
    """

    if not isinstance(text, str):
        return ""

    # Lowercase
    text = text.lower().strip()
    #normalise
    text = re.sub(r"\s+", " ", text)
    #tokenisation
    try:
        tokens = nltk.word_tokenize(text)
    except LookupError:
        tokens = re.findall(r"[a-zA-Z0-9]+", text)

    #stopwords
    stop_words = set(stopwords.words("english"))
    cleaned_tokens = []
    for token in tokens:
        # Remove punctuation
        token = token.strip(string.punctuation)

        if not token:
            continue

        # Remove stopwords
        if token in stop_words:
            continue

        #remove numbers
        if token.isnumeric():
            continue

        #remove symbols
        if re.fullmatch(r"[^\w]+",token):
            continue

        #lemmatization
        lemma = lemmatizer.lemmatize(token)
        cleaned_tokens.append(lemma)

        return " ".join(cleaned_tokens)