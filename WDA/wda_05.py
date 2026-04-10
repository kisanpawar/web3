"""
WDA 5 — Spam classifier: TF-IDF + Naive Bayes (or Logistic Regression).

Dependencies: pip install scikit-learn
"""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


def build_dataset():
    """Small embedded SMS-style corpus (ham / spam)."""
    messages = [
        ("hey are we still meeting at 5", "ham"),
        ("thanks for the update", "ham"),
        ("can you send the file", "ham"),
        ("lunch tomorrow?", "ham"),
        ("WINNER!! You have been selected for a $1000 prize. Call now!!!", "spam"),
        ("URGENT! You have won a free cruise. Text YES to claim", "spam"),
        ("Congratulations you won click here http://spam.test", "spam"),
        ("FREE entry in weekly lottery! Text WIN to 12345", "spam"),
        ("see you at the office", "ham"),
        ("project deadline moved to Friday", "ham"),
    ]
    X = [m for m, _ in messages]
    y = [lbl for _, lbl in messages]
    return X, y


def make_model(use_logistic: bool = False):
    clf = LogisticRegression(max_iter=200) if use_logistic else MultinomialNB()
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    token_pattern=r"(?u)\b\w\w+\b",
                ),
            ),
            ("clf", clf),
        ]
    )


def main() -> None:
    X, y = build_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    model = make_model(use_logistic=False)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    print(f"Hold-out accuracy (tiny dataset): {acc:.2f}\n")

    samples = [
        "Hi mom, I'll be late for dinner",
        "WIN cash now!!! Click this exclusive offer",
        "Meeting notes attached",
    ]
    preds = model.predict(samples)
    probs = model.predict_proba(samples)
    labels = model.classes_
    print("Sample predictions:")
    for msg, pred, pr in zip(samples, preds, probs):
        p_spam = pr[list(labels).index("spam")] if "spam" in labels else pr[1]
        print(f"  Message: {msg!r}")
        print(f"  -> {pred} (P_spam ~ {p_spam:.3f})\n")


if __name__ == "__main__":
    main()
