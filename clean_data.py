import re
import spacy
from typing import List

nlp = spacy.load("en_core_web_sm")

def clean_text(text: str) -> str:
    text = re.sub(r'[^a-zA-Z0-9\s+&/-]', '', text.lower().strip())
    doc = nlp(text)
    return ' '.join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])

# Move the example usage into a protected block
if __name__ == "__main__":
    # Import here to avoid circular dependency
    from extract_data import read_jds, read_cvs
    
    jds = [clean_text(jd) for jd in read_jds()]
    cvs = [clean_text(cv) for cv in read_cvs()]
    print("Cleaned JDs:", jds[:1])
