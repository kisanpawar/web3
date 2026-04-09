"""
DL_Practical_QB — Practical 4 Q1: Autoencoder for data reconstruction (MNIST).

QUESTION:
  a) Load MNIST dataset and preprocess.
  b) Design encoder–decoder architecture.
  c) Train the autoencoder model.
  d) Reconstruct test images and visualize outputs.
  e) Analyze reconstruction performance.

ANSWER:
  a) Grayscale digits normalized to [0,1]; flattened to 784-D vectors.
  b) Encoder: Dense 128 → bottleneck 64; Decoder: Dense 128 → sigmoid 784.
  c) Trained with input==target, binary_crossentropy, Adam.
  d) Side-by-side original vs reconstructed grid saved to output/.
  e) Lower loss + sharper reconstructions mean the bottleneck still captures digit structure.
"""
import numpy as np
from tensorflow.keras.datasets import mnist
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

from _config import epochs_default, savefig
import matplotlib.pyplot as plt

epochs = epochs_default(20)

# (a) Load and preprocess MNIST (unsupervised: ignore labels)
(x_train, _), (x_test, _) = mnist.load_data()
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0
x_train = x_train.reshape((len(x_train), 28 * 28))
x_test = x_test.reshape((len(x_test), 28 * 28))

# (b) Encoder–decoder (bottleneck = encoding_dim)
input_dim = 784
encoding_dim = 64
input_img = Input(shape=(input_dim,))
encoded = Dense(128, activation="relu")(input_img)
encoded = Dense(encoding_dim, activation="relu")(encoded)
decoded = Dense(128, activation="relu")(encoded)
decoded = Dense(input_dim, activation="sigmoid")(decoded)
autoencoder = Model(input_img, decoded)
autoencoder.compile(optimizer=Adam(), loss="binary_crossentropy")
autoencoder.summary()

# (c) Train autoencoder
autoencoder.fit(
    x_train,
    x_train,
    epochs=epochs,
    batch_size=256,
    shuffle=True,
    validation_data=(x_test, x_test),
    verbose=1,
)

# (d) Reconstruct and visualize; (e) judge quality visually / from val loss
decoded_imgs = autoencoder.predict(x_test, verbose=0)
n = 10
plt.figure(figsize=(20, 4))
for i in range(n):
    ax = plt.subplot(2, n, i + 1)
    plt.imshow(x_test[i].reshape(28, 28), cmap="gray")
    plt.title("Original")
    plt.axis("off")
    ax = plt.subplot(2, n, i + n + 1)
    plt.imshow(decoded_imgs[i].reshape(28, 28), cmap="gray")
    plt.title("Reconstructed")
    plt.axis("off")
savefig("p04_autoencoder_mnist.png")
print("Saved reconstruction grid to output/")
