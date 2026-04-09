"""
DL_Practical_QB — Practical 8 Q1: Simple RNN for time-series (rainfall).

QUESTION:
  a) Prepare a sequential dataset (rainfall in mm as given in QB).
  b) Design 4-to-1 RNN model architecture.
  c) Train the RNN model.
  d) Predict future rainfall values based on previous inputs.
  e) Compare predicted vs actual values using a graph.

ANSWER:
  a) Sliding windows: input = 4 consecutive days, target = next day (shape N×4×1).
  b) SimpleRNN(16, tanh) → Dense(1) regression head.
  c) Adam + MSE; fit on all constructed windows from the short series.
  d) model.predict on same X gives one-step-ahead predictions aligned with y.
  e) Line plot of actual y vs predictions saved to output/p08_rainfall_rnn.png.
"""
import numpy as np
from tensorflow.keras.layers import Dense, SimpleRNN
from tensorflow.keras.models import Sequential

from _config import epochs_default, savefig
import matplotlib.pyplot as plt

# (a) QB rainfall series (mm)
rainfall = np.array(
    [
        2.1,
        2.5,
        3.0,
        3.4,
        3.8,
        4.0,
        4.5,
        5.1,
        5.8,
        6.2,
        6.5,
        6.9,
        7.3,
        7.8,
        8.2,
        8.6,
        9.0,
        8.5,
        8.0,
        7.6,
    ],
    dtype=np.float32,
)

# (a) Build sequences for 4-to-1 prediction
X, y = [], []
for i in range(len(rainfall) - 4):
    X.append(rainfall[i : i + 4])
    y.append(rainfall[i + 4])
X = np.array(X).reshape((-1, 4, 1))
y = np.array(y)

epochs = epochs_default(200)
# (b)(c) RNN + training
model = Sequential(
    [
        SimpleRNN(16, activation="tanh", input_shape=(4, 1)),
        Dense(1),
    ]
)
model.compile(optimizer="adam", loss="mse")
model.fit(X, y, epochs=epochs, verbose=0)
# (d) Predict
predicted = model.predict(X, verbose=0).flatten()

# (e) Graph: actual vs predicted
plt.plot(y, label="Actual")
plt.plot(predicted, label="Predicted")
plt.xlabel("Index")
plt.ylabel("Rainfall (mm)")
plt.legend()
savefig("p08_rainfall_rnn.png")
print("Saved output/p08_rainfall_rnn.png")
