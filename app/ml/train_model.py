import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# tiny dataset (you can expand later)
texts = [
    "charged twice for order",
    "refund not received",
    "payment failed",
    "app is crashing",
    "system error occurs",
    "bug in app",
    "cannot login",
    "forgot password",
]

labels = [
    "billing",
    "billing",
    "billing",
    "technical",
    "technical",
    "technical",
    "authentication",
    "authentication",
]

# vectorize text
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# train model
model = LogisticRegression()
model.fit(X, labels)

# ✅ ensure folder exists
os.makedirs("app/ml", exist_ok=True)

# ✅ save in correct location
joblib.dump(model, "app/ml/model.pkl")
joblib.dump(vectorizer, "app/ml/vectorizer.pkl")

print("Model trained and saved to app/ml/")