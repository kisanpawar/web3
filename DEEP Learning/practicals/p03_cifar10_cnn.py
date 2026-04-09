"""
DL_Practical_QB — Practical 3 Q1: CIFAR-10 image classification (deep learning / CNN).

QUESTION:
  a) Load and preprocess CIFAR-10 dataset.
  b) Build a CNN architecture.
  c) Train the model and tune hyperparameters.
  d) Test on unseen images and predict class labels.
  e) Evaluate performance using accuracy and results.

ANSWER:
  a) cifar10.load_data(); pixel values scaled to [0,1]; 32×32 RGB, 10 classes.
  b) Conv→Pool→Conv→Pool→Flatten→Dense→softmax (see model definition below).
  c) Trained with Adam, sparse_categorical_crossentropy; epoch count from epochs_default().
  d) model.predict on x_test; example index prints predicted vs actual class name.
  e) test accuracy from model.evaluate; qualitative check via sample grid + prediction printout.
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras import datasets, layers, models

from _config import epochs_default, savefig
import matplotlib.pyplot as plt

epochs = epochs_default(10)

# (a) Load and preprocess CIFAR-10
(x_train, y_train), (x_test, y_test) = datasets.cifar10.load_data()
print(x_train.shape, y_train.shape)
x_train = x_train / 255.0
x_test = x_test / 255.0
class_names = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
]

plt.figure(figsize=(8, 8))
for i in range(9):
    plt.subplot(3, 3, i + 1)
    plt.imshow(x_train[i])
    plt.title(class_names[y_train[i][0]])
    plt.axis("off")
savefig("p03_cifar10_samples.png")

# (b)(c) CNN architecture and training
model = models.Sequential(
    [
        layers.Conv2D(32, (3, 3), activation="relu", input_shape=(32, 32, 3)),
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

# (d)(e) Evaluate and predict on unseen test images
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print("Test accuracy:", test_acc)
predictions = model.predict(x_test, verbose=0)
index = 4000
predicted_class = int(np.argmax(predictions[index]))
print("Predicted:", class_names[predicted_class])
print("Actual:", class_names[y_test[index][0]])
