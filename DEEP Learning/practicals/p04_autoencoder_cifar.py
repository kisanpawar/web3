"""
DL_Practical_QB — Practical 4 Q2: Autoencoder for data reconstruction (CIFAR-10).

QUESTION:
  a) Load CIFAR-10 dataset and preprocess.
  b) Design encoder–decoder architecture.
  c) Train the autoencoder model.
  d) Reconstruct test images and visualize outputs.
  e) Analyze reconstruction performance.

ANSWER:
  a) 32×32 RGB images scaled to [0,1].
  b) Convolutional encoder with pooling; decoder with UpSampling + Conv; sigmoid RGB output.
  c) MSE loss (pixel regression); Adam optimizer.
  d) Original vs reconstructed rows in saved figure.
  e) CIFAR reconstructions are blurrier than MNIST; MSE reflects global color/texture fidelity.
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras import datasets, layers, models

from _config import epochs_default, savefig
import matplotlib.pyplot as plt

epochs = epochs_default(15)
batch_size = 128

# (a) CIFAR-10 load and normalize
(x_train, _), (x_test, _) = datasets.cifar10.load_data()
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0

# (b) Encoder + decoder
encoder = models.Sequential(
    [
        layers.Input(shape=(32, 32, 3)),
        layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
        layers.MaxPooling2D((2, 2), padding="same"),
        layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
        layers.MaxPooling2D((2, 2), padding="same"),
    ],
    name="encoder",
)
decoder = models.Sequential(
    [
        layers.Input(shape=(8, 8, 64)),
        layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
        layers.UpSampling2D((2, 2)),
        layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
        layers.UpSampling2D((2, 2)),
        layers.Conv2D(3, (3, 3), activation="sigmoid", padding="same"),
    ],
    name="decoder",
)
autoencoder = models.Sequential([encoder, decoder])
autoencoder.compile(optimizer="adam", loss="mse")
# (c) Train
autoencoder.fit(
    x_train,
    x_train,
    epochs=epochs,
    batch_size=batch_size,
    shuffle=True,
    validation_data=(x_test, x_test),
    verbose=1,
)

# (d)(e) Visual comparison on test samples
recon = autoencoder.predict(x_test[:8], verbose=0)
plt.figure(figsize=(16, 4))
for i in range(8):
    plt.subplot(2, 8, i + 1)
    plt.imshow(x_test[i])
    plt.axis("off")
    plt.subplot(2, 8, 8 + i + 1)
    plt.imshow(np.clip(recon[i], 0, 1))
    plt.axis("off")
savefig("p04_autoencoder_cifar.png")
print("Saved CIFAR reconstructions.")
