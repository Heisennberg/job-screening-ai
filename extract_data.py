import os
import pdfplumber
from docx import Document
from typing import List

def read_jds(folder: str = "data/jds") -> List[str]:
    """Read Word docs from jds folder"""
    jds = []
    for file in os.listdir(folder):
        if file.endswith(".docx"):
            doc = Document(os.path.join(folder, file))
            jds.append("\n".join([p.text for p in doc.paragraphs]))
    return jds

def read_cvs(folder: str = "data/cvs") -> List[str]:
    """Read PDFs from cvs folder"""
    cvs = []
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            with pdfplumber.open(os.path.join(folder, file)) as pdf:
                cvs.append("\n".join([page.extract_text() for page in pdf.pages]))
    return cvs