"""
DL_Practical_QB — Practical 9 Q9: LSTM for sentiment analysis (UMICH SI650–style).

QUESTION:
  a) Load and preprocess text dataset.
  b) Build LSTM model.
  c) Train the model with embeddings.
  d) Test model on unseen data.
  e) Evaluate model performance.

ANSWER:
  a) CSV via kagglehub; Tokenizer(5000) + pad_sequences(max_len=50).
  b) Embedding → LSTM(64) → Dense(1, sigmoid) for binary sentiment.
  c) Adam + binary_crossentropy; validation_split=0.2 during fit.
  d) Predict on test sentences; threshold 0.5 for positive/negative.
  e) Training/val accuracy from logs; sample qualitative prints for unseen reviews.
"""
import os
import sys

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import Dense, Embedding, LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

from _config import epochs_default

epochs = epochs_default(5)


def main():
    try:
        import kagglehub
    except ImportError:
        print("pip install kagglehub pandas")
        return 1
    try:
        path = kagglehub.dataset_download("seesea0203/umich-si650-nlp")
    except Exception as e:
        print("Dataset download failed:", e)
        return 0
    print("Dataset path:", path)
    train_path = os.path.join(path, "train.csv")
    test_path = os.path.join(path, "test.csv")
    if not os.path.isfile(train_path):
        print("train.csv not found in", path)
        return 1
    train_data = pd.read_csv(train_path)
    test_data = pd.read_csv(test_path)
    # (a) Text + labels
    X_train = train_data["sentence"].values
    y_train = train_data["label"].values
    X_test = test_data["sentence"].values
    tokenizer = Tokenizer(num_words=5000)
    tokenizer.fit_on_texts(X_train)
    X_train_seq = tokenizer.texts_to_sequences(X_train)
    X_test_seq = tokenizer.texts_to_sequences(X_test)
    max_len = 50
    X_train_pad = pad_sequences(X_train_seq, maxlen=max_len)
    X_test_pad = pad_sequences(X_test_seq, maxlen=max_len)
    # (b) LSTM classifier with embedding
    model = Sequential(
        [
            Embedding(input_dim=5000, output_dim=64, input_length=max_len),
            LSTM(64),
            Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"]
    )
    # (c) Train with embeddings
    model.fit(
        X_train_pad,
        y_train,
        epochs=epochs,
        batch_size=32,
        validation_split=0.2,
        verbose=1,
    )
    # (d)(e) Unseen test predictions + qualitative evaluation
    predictions = model.predict(X_test_pad, verbose=0)
    predicted_label = (predictions > 0.5).astype(int).flatten()
    for i in range(min(5, len(X_test))):
        lab = "Positive" if predicted_label[i] == 1 else "Negative"
        print(X_test[i][:80], "->", lab)
    return 0


if __name__ == "__main__":
    sys.exit(main())
