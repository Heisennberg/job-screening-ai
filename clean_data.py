import re
import sys
import subprocess
from typing import List

def load_spacy_model():
    """Safe spaCy loader with auto-install fallback"""
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            return nlp
        except OSError:
            print("Downloading spaCy model...")
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
            return spacy.load("en_core_web_sm")
    except ImportError:
        print("Installing spaCy...")
        subprocess.run([sys.executable, "-m", "pip", "install", "spacy==3.7.0"], check=True)
        import spacy
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

def clean_text(text: str) -> str:
    """Robust text cleaner with error handling"""
    if not text or not isinstance(text, str):
        return ""
    
    try:
        # Basic cleaning
        text = re.sub(r'http\S+', '', text)  # Remove URLs
        text = re.sub(r'\S+@\S+', '', text)  # Remove emails
        text = re.sub(r'[^a-zA-Z0-9\s+&/-]', '', text.lower().strip())
        
        # NLP processing
        doc = nlp(text)
        return ' '.join([
            token.lemma_ 
            for token in doc 
            if not token.is_stop and token.is_alpha
        ])
    except Exception as e:
        print(f"Text cleaning error: {str(e)}")
        return text.lower().strip()  # Fallback to basic cleaning

if __name__ == "__main__":
    # Test with sample text if run directly
    test_text = "Python developer with 5+ years experience in Django and AWS."
    print(clean_text(test_text))
