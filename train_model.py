import os
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from extract_data import read_jds, read_cvs  # Use actual data functions
from clean_data import clean_text  # Proper text cleaning

def train_matching_model():
    """Train and save a job-CV matching model"""
    try:
        # 1. Load and prepare data
        print("📂 Loading data...")
        jds = [clean_text(jd) for jd in read_jds()]
        cvs = [clean_text(cv) for cv in read_cvs()]
        
        if not jds or not cvs:
            raise ValueError("No JDs or CVs found in data folders!")

        # 2. Create training pairs (replace with your actual labels)
        print("⚙️ Creating training pairs...")
        combined_texts = [f"JD: {jd} CV: {cv}" for jd, cv in zip(jds, cvs)]
        labels = np.random.randint(0, 2, size=len(combined_texts))  # Replace with real labels
        
        # 3. Train/Test split
        X_train, X_test, y_train, y_test = train_test_split(
            combined_texts, labels, test_size=0.2, random_state=42
        )

        # 4. Text vectorization
        print("🔡 Vectorizing text...")
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2), 
            max_features=5000
        )
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)

        # 5. Model training
        print("🤖 Training model...")
        model = LogisticRegression(
            class_weight='balanced',
            max_iter=1000
        )
        model.fit(X_train_vec, y_train)

        # 6. Evaluation
        preds = model.predict(X_test_vec)
        print(f"✅ Model trained! Accuracy: {accuracy_score(y_test, preds):.2f}")

        # 7. Save artifacts
        os.makedirs("models", exist_ok=True)
        joblib.dump(vectorizer, "models/vectorizer.joblib")
        joblib.dump(model, "models/matching_model.joblib")
        print("💾 Saved model artifacts to models/ directory")

    except Exception as e:
        print(f"❌ Training failed: {str(e)}")

if __name__ == "__main__":
    train_matching_model()