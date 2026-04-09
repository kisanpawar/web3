"""
DL_Practical_QB — Practical 7 Q1: GAN for synthetic digit images (MNIST).

QUESTION:
  a) Load and preprocess dataset.
  b) Design Generator and Discriminator models.
  c) Compile GAN and freeze Discriminator (for stacked training phase).
  d) Train GAN and display loss.
  e) Generate and visualize synthetic images.

ANSWER:
  a) MNIST flattened; scaled to [-1,1] with tanh on generator output.
  b) Generator: noise→Dense layers→784 tanh; Discriminator: 784→Dense→sigmoid (real/fake).
  c) Discriminator compiled alone; then discriminator.trainable=False inside combined GAN.
  d) Alternate train_on_batch on real/fake for D, then train G via GAN on noise→real labels.
  e) Sample noise after training and plot 16 grayscale synthetic digits.
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.layers import Dense, LeakyReLU
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

from _config import quick_mode, savefig
import matplotlib.pyplot as plt

# (a) Preprocess MNIST for GAN
(x_train, _), (_, _) = mnist.load_data()
x_train = (x_train.astype(np.float32) - 127.5) / 127.5
x_train = x_train.reshape(x_train.shape[0], 784)

latent_dim = 100
gan_epochs = 400 if quick_mode() else 2000
batch_size = 64


# (b) Generator + Discriminator architectures
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
        ],
        name="generator",
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
        ],
        name="discriminator",
    )


# (c) Compile discriminator; stack GAN with D frozen
discriminator = build_discriminator()
discriminator.compile(
    loss="binary_crossentropy", optimizer=Adam(0.0002, 0.5), metrics=["accuracy"]
)
generator = build_generator()
discriminator.trainable = False
gan = Sequential([generator, discriminator])
gan.compile(loss="binary_crossentropy", optimizer=Adam(0.0002, 0.5))

# (d) Adversarial training loop (loss printed periodically)
for epoch in range(gan_epochs):
    idx = np.random.randint(0, x_train.shape[0], batch_size)
    real_images = x_train[idx]
    noise = np.random.normal(0, 1, (batch_size, latent_dim))
    fake_images = generator.predict(noise, verbose=0)
    real_labels = np.ones((batch_size, 1))
    fake_labels = np.zeros((batch_size, 1))
    discriminator.trainable = True
    d_loss_real = discriminator.train_on_batch(real_images, real_labels)
    d_loss_fake = discriminator.train_on_batch(fake_images, fake_labels)
    discriminator.trainable = False
    noise = np.random.normal(0, 1, (batch_size, latent_dim))
    g_loss = gan.train_on_batch(noise, real_labels)
    if epoch % max(1, gan_epochs // 10) == 0:
        print(
            f"Epoch {epoch} | D real loss: {d_loss_real[0]:.4f} | G loss: {g_loss:.4f}"
        )

# (e) Generate and visualize synthetic digits
noise = np.random.normal(0, 1, (16, latent_dim))
samples = generator.predict(noise, verbose=0)
plt.figure(figsize=(8, 8))
for i in range(16):
    plt.subplot(4, 4, i + 1)
    plt.imshow(samples[i].reshape(28, 28), cmap="gray")
    plt.axis("off")
savefig("p07_gan_mnist_samples.png")
print("Saved synthetic digits to output/p07_gan_mnist_samples.png")
