"""
DL_Practical_QB — Practical 3 Q2: Image classification using MNIST with a CNN.

QUESTION:
  a) Load and preprocess MNIST dataset.
  b) Build a CNN architecture.
  c) Train the model and tune hyperparameters.
  d) Test on unseen images and predict class labels.
  e) Evaluate performance using accuracy and results.

ANSWER:
  a) mnist.load_data(); normalize; add channel dim (28,28,1).
  b) Conv→Pool×2 + Dense classifier (same pattern as CIFAR, adjusted input shape).
  c) Adam + sparse_categorical_crossentropy; validation on x_test during fit.
  d) After training, evaluate on full test set; argmax of logits gives digit class.
  e) Printed test accuracy summarizes performance.
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras import datasets, layers, models

from _config import epochs_default

epochs = epochs_default(10)

# (a) MNIST load and preprocess (channel last)
(x_train, y_train), (x_test, y_test) = datasets.mnist.load_data()
x_train = np.expand_dims(x_train.astype("float32") / 255.0, -1)
x_test = np.expand_dims(x_test.astype("float32") / 255.0, -1)

# (b)(c) CNN + training
model = models.Sequential(
    [
        layers.Conv2D(32, (3, 3), activation="relu", input_shape=(28, 28, 1)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(64, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ]
)
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
model.fit(x_train, y_train, epochs=epochs, validation_data=(x_test, y_test), verbose=1)
# (d)(e) Unseen test evaluation
loss, acc = model.evaluate(x_test, y_test, verbose=0)
print("Test accuracy:", acc)
