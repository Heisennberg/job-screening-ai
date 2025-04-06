import ollama
import json
from typing import Dict, List, Tuple
from clean_data import clean_text

# Configure model parameters
OLLAMA_MODEL = "llama3"

def extract_keywords(text: str, doc_type: str = "jd") -> List[str]:
    """Extract keywords using LLM with error handling"""
    try:
        prompt = f"""Extract the top 10 most important TECHNICAL SKILLS from this {doc_type}.
        Return ONLY a comma-separated list of specific technologies/tools in lowercase.
        Example: python,django,aws,postgresql
        {doc_type.upper()}: {clean_text(text)}"""
        
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            options={'temperature': 0.1}
        )
        # Improved keyword parsing
        return list(set([kw.strip().lower() for kw in response['response'].replace("\n", "").split(",") if kw.strip()]))
    
    except Exception as e:
        print(f"Keyword extraction failed: {str(e)}")
        return []

def calculate_ats_score(jd_keywords: List[str], cv_keywords: List[str]) -> Tuple[float, List[str]]:
    """Calculate match score between JD and CV keywords"""
    if not jd_keywords or not cv_keywords:
        return 0.0, []
    
    # Normalize keywords
    jd_set = set(kw.strip().lower() for kw in jd_keywords)
    cv_set = set(kw.strip().lower() for kw in cv_keywords)
    
    matched = list(jd_set & cv_set)
    score = (len(matched) / len(jd_set)) * 100 if jd_set else 0
    return round(score, 2), matched

def detect_bias(text: str) -> Dict:
    """Analyze text for biased language with JSON validation"""
    try:
        prompt = f"""Analyze this job description for biased language (gender, age, race).
        Return JSON with these keys:
        - "bias_score": 0-100 (100=most biased)
        - "biased_phrases": array of problematic phrases
        - "alternatives": array of neutral alternatives
        
        Text: {clean_text(text)}"""
        
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            format="json"
        )
        
        result = json.loads(response['response'])
        return {
            # Fixed parenthesis and type conversion
            "bias_score": min(max(int(result.get("bias_score", 0)), 0), 100),
            "biased_phrases": list(result.get("biased_phrases", []))[:5],
            "alternatives": list(result.get("alternatives", []))[:5]
        }
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Test with improved sample inputs
    test_jd = "Senior Python Developer needed with 5+ years experience in Django and AWS. Young graduates encouraged to apply."
    test_cv = "Python developer with 6 years experience in Django, AWS, and Kubernetes. Certified AWS Solutions Architect."
    
    jd_keywords = extract_keywords(test_jd, "jd")
    cv_keywords = extract_keywords(test_cv, "cv")
    score, matches = calculate_ats_score(jd_keywords, cv_keywords)
    
    print(f"JD Keywords: {jd_keywords}")
    print(f"CV Keywords: {cv_keywords}")
    print(f"ATS Score: {score}%")
    print(f"Matches: {matches}")
    print(f"Bias Report: {detect_bias(test_jd)}")