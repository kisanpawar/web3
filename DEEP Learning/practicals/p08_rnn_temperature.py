"""
DL_Practical_QB — Practical 8 Q2: Simple RNN for time-series (temperature).

QUESTION:
  a) Prepare a sequential dataset (temperature in °C as given in QB).
  b) Design 4-to-1 RNN model architecture.
  c) Train the RNN model.
  d) Predict future temperature values based on previous inputs.
  e) Compare predicted vs actual values using a graph.

ANSWER:
  a–d) Same pipeline as rainfall: 4-day window → next day; SimpleRNN + Dense(1); MSE.
  e) Plot saved to output/p08_temperature_rnn.png shows fit on the supplied short series.
"""
import numpy as np
from tensorflow.keras.layers import Dense, SimpleRNN
from tensorflow.keras.models import Sequential

from _config import epochs_default, savefig
import matplotlib.pyplot as plt

# (a) QB temperature series
temperature = np.array(
    [30, 31, 32, 33, 34, 35, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 28, 29, 30, 31],
    dtype=np.float32,
)

# (a) 4-step windows → next value
X, y = [], []
for i in range(len(temperature) - 4):
    X.append(temperature[i : i + 4])
    y.append(temperature[i + 4])
X = np.array(X).reshape((-1, 4, 1))
y = np.array(y)

epochs = epochs_default(200)
# (b)(c)
model = Sequential(
    [SimpleRNN(16, activation="tanh", input_shape=(4, 1)), Dense(1)]
)
model.compile(optimizer="adam", loss="mse")
model.fit(X, y, epochs=epochs, verbose=0)
# (d)
predicted = model.predict(X, verbose=0).flatten()

# (e)
plt.plot(y, label="Actual")
plt.plot(predicted, label="Predicted")
plt.xlabel("Index")
plt.ylabel("Temperature (C)")
plt.legend()
savefig("p08_temperature_rnn.png")
print("Saved output/p08_temperature_rnn.png")
