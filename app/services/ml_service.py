import joblib

model = joblib.load("app/ml/model.pkl")
vectorizer = joblib.load("app/ml/vectorizer.pkl")


def classify_ticket(title: str, description: str) -> str:
    text = title + " " + description
    X = vectorizer.transform([text])
    prediction = model.predict(X)[0]
    return prediction