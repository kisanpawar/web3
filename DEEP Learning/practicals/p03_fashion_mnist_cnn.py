"""
DL_Practical_QB — Practical 3 Q3: Image classification using Fashion-MNIST with a CNN.

QUESTION:
  a) Load and preprocess Fashion-MNIST dataset.  [QB text says MNIST but lists Fashion-MNIST]
  b) Build a CNN architecture.
  c) Train the model and tune hyperparameters.
  d) Test on unseen images and predict class labels.
  e) Evaluate performance using accuracy and results.

ANSWER:
  a) fashion_mnist.load_data(); normalize to [0,1]; shape (28,28,1).
  b–c) Same CNN pattern as MNIST; Fashion-MNIST is harder (textures/classes).
  d–e) Test accuracy and predictions on held-out test images.
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras import datasets, layers, models

from _config import epochs_default

epochs = epochs_default(10)

# (a) Fashion-MNIST
(x_train, y_train), (x_test, y_test) = datasets.fashion_mnist.load_data()
x_train = np.expand_dims(x_train.astype("float32") / 255.0, -1)
x_test = np.expand_dims(x_test.astype("float32") / 255.0, -1)

# (b)(c) CNN + train
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
# (d)(e)
loss, acc = model.evaluate(x_test, y_test, verbose=0)
print("Test accuracy:", acc)
