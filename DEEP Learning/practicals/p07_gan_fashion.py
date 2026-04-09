"""
DL_Practical_QB — Practical 7 Q2: GAN for synthetic fashion images (Fashion-MNIST).

QUESTION:
  a) Load and preprocess Fashion-MNIST dataset.
  b) Design Generator and Discriminator.
  c) Compile GAN model.
  d) Train GAN with real and fake samples.
  e) Generate and display synthetic fashion images.

ANSWER:
  a) Same preprocessing as MNIST GAN: flatten, scale to [-1,1].
  b–c) Same architecture pattern as digit GAN (784 outputs, tanh).
  d) Alternating D and G updates on minibatches.
  e) 4×4 grid of generated clothing-like patterns saved to output/.
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras.layers import Dense, LeakyReLU
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

from _config import quick_mode, savefig
import matplotlib.pyplot as plt

# (a)
(x_train, _), (_, _) = fashion_mnist.load_data()
x_train = (x_train.astype(np.float32) - 127.5) / 127.5
x_train = x_train.reshape(x_train.shape[0], 784)

latent_dim = 100
gan_epochs = 400 if quick_mode() else 2000
batch_size = 64


# (b)
def build_generator():
    return Sequential(
        [
            Dense(256, input_dim=latent_dim),
            LeakyReLU(0.2),
            Dense(512),
            LeakyReLU(0.2),
            Dense(1024),
            LeakyReLU(0.2),
            Dense(784, activation="tanh"),
        ]
    )


def build_discriminator():
    return Sequential(
        [
            Dense(1024, input_dim=784),
            LeakyReLU(0.2),
            Dense(512),
            LeakyReLU(0.2),
            Dense(256),
            LeakyReLU(0.2),
            Dense(1, activation="sigmoid"),
        ]
    )


# (c)
discriminator = build_discriminator()
discriminator.compile(
    loss="binary_crossentropy", optimizer=Adam(0.0002, 0.5), metrics=["accuracy"]
)
generator = build_generator()
discriminator.trainable = False
gan = Sequential([generator, discriminator])
gan.compile(loss="binary_crossentropy", optimizer=Adam(0.0002, 0.5))

# (d)
for epoch in range(gan_epochs):
    idx = np.random.randint(0, x_train.shape[0], batch_size)
    real_images = x_train[idx]
    noise = np.random.normal(0, 1, (batch_size, latent_dim))
    fake_images = generator.predict(noise, verbose=0)
    real_labels = np.ones((batch_size, 1))
    fake_labels = np.zeros((batch_size, 1))
    discriminator.trainable = True
    discriminator.train_on_batch(real_images, real_labels)
    discriminator.train_on_batch(fake_images, fake_labels)
    discriminator.trainable = False
    noise = np.random.normal(0, 1, (batch_size, latent_dim))
    gan.train_on_batch(noise, real_labels)

# (e)
noise = np.random.normal(0, 1, (16, latent_dim))
samples = generator.predict(noise, verbose=0)
plt.figure(figsize=(8, 8))
for i in range(16):
    plt.subplot(4, 4, i + 1)
    plt.imshow(samples[i].reshape(28, 28), cmap="gray")
    plt.axis("off")
savefig("p07_gan_fashion_samples.png")
print("Saved output/p07_gan_fashion_samples.png")
