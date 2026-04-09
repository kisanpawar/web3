"""
DL_Practical_QB — Practical 5 Q1: Neural Network for digit recognition (MNIST).

QUESTION:
  a) Load and explore MNIST dataset, and normalize input data.
  b) Design and build a Feed-Forward Neural Network model.
  c) Compile and train the model with validation.
  d) Test the model and predict unseen digit(s).
  e) Visualize results and evaluate performance.

ANSWER:
  a) Shapes printed; pixels divided by 255.
  b) Flatten → Dense(128,relu) → Dense(10,softmax).
  c) Adam, sparse_categorical_crossentropy, validation_data=(x_test,y_test).
  d) argmax on softmax for a chosen test index; printed predicted vs actual.
  e) Sample grid + single-digit plot with predicted title; test accuracy printed.
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras import datasets, layers, models

from _config import epochs_default, savefig

import matplotlib.pyplot as plt

epochs = epochs_default(20)

# (a) Load, explore, normalize
(x_train, y_train), (x_test, y_test) = datasets.mnist.load_data()
print(x_train.shape, y_train.shape)
x_train = x_train / 255.0
x_test = x_test / 255.0

plt.figure(figsize=(6, 6))
for i in range(9):
    plt.subplot(3, 3, i + 1)
    plt.imshow(x_train[i], cmap="gray")
    plt.title(str(y_train[i]))
    plt.axis("off")
savefig("p05_mnist_samples.png")

# (b)(c) FFN + training with validation
model = models.Sequential(
    [
        layers.Flatten(input_shape=(28, 28)),
        layers.Dense(128, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ]
)
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
model.fit(
    x_train, y_train, epochs=epochs, validation_data=(x_test, y_test), verbose=1
)
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print("Test accuracy:", test_acc)
# (d) Prediction on unseen test image
predictions = model.predict(x_test, verbose=0)
index = 9
predicted_digit = int(np.argmax(predictions[index]))
print("Predicted:", predicted_digit, "Actual:", int(y_test[index]))

plt.figure(figsize=(4, 4))
plt.imshow(x_test[index], cmap="gray")
plt.title(f"Predicted: {predicted_digit}")
plt.axis("off")
savefig("p05_prediction.png")
# (e) Performance = test_acc; visualization = samples + prediction figure
