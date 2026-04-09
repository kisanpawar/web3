"""
DL_Practical_QB — Practical 2: Regularization (this file answers Q1 L2 and Q2 Dropout).

QUESTION Q1 — Regularization (L2):
  a) Load dataset and split into training/testing sets.
  b) Train a baseline model without regularization.
  c) Apply L2 regularization technique.
  d) Compare training vs validation performance.
  e) Analyze how regularization reduces overfitting.

QUESTION Q2 — Regularization (Dropout): same (a)(b), (c) Apply Dropout, (d)(e) as above.

ANSWER:
  a) MNIST loaded; Keras provides train/test split (60k / 10k); inputs normalized to [0,1].
  b) Baseline: two Dense(256,relu) hidden layers + softmax — may overfit (high train vs val gap).
  c) L2: kernel_regularizer=l2(0.001) on hidden Dense layers. Dropout: 0.5 after each hidden block.
  d) Val-accuracy curves plotted for no-reg vs L2 vs Dropout (see output/p02_regularization.png).
  e) L2 shrinks weights; Dropout prevents co-adaptation — both typically narrow train–val gap
     and improve or stabilize validation accuracy vs the baseline.
"""
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers
from tensorflow.keras.datasets import mnist

from _config import epochs_default, savefig
import matplotlib.pyplot as plt

epochs = epochs_default(20)

# (a) MNIST train/test split and preprocessing
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.reshape(60000, 28 * 28) / 255.0
x_test = x_test.reshape(10000, 28 * 28) / 255.0

# (b) Baseline — no regularization
model_no_reg = models.Sequential(
    [
        layers.Dense(256, activation="relu", input_shape=(784,)),
        layers.Dense(256, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ]
)
model_no_reg.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)
history_no_reg = model_no_reg.fit(
    x_train, y_train, epochs=epochs, validation_data=(x_test, y_test), verbose=1
)

# (c) Q1 — L2 regularization on hidden layers
model_l2 = models.Sequential(
    [
        layers.Dense(
            256,
            activation="relu",
            kernel_regularizer=regularizers.l2(0.001),
            input_shape=(784,),
        ),
        layers.Dense(256, activation="relu", kernel_regularizer=regularizers.l2(0.001)),
        layers.Dense(10, activation="softmax"),
    ]
)
model_l2.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)
history_l2 = model_l2.fit(
    x_train, y_train, epochs=epochs, validation_data=(x_test, y_test), verbose=1
)

# (c) Q2 — Dropout regularization
model_dropout = models.Sequential(
    [
        layers.Dense(256, activation="relu", input_shape=(784,)),
        layers.Dropout(0.5),
        layers.Dense(256, activation="relu"),
        layers.Dropout(0.5),
        layers.Dense(10, activation="softmax"),
    ]
)
model_dropout.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)
history_dropout = model_dropout.fit(
    x_train, y_train, epochs=epochs, validation_data=(x_test, y_test), verbose=1
)

# (d) Compare validation performance across models
plt.figure(figsize=(8, 5))
plt.plot(history_no_reg.history["val_accuracy"], label="No Reg")
plt.plot(history_l2.history["val_accuracy"], label="L2")
plt.plot(history_dropout.history["val_accuracy"], label="Dropout")
plt.legend()
plt.title("Validation accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
path = savefig("p02_regularization.png")
print("Saved plot:", path)
# (e) Explain in report: lower gap between train and val acc with L2/Dropout vs baseline
