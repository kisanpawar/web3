"""
DL_Practical_QB — Practical 1 (Q1, Q2, Q3 same steps; optimizer pairs differ).

QUESTION — Implement a Feed-Forward Neural Network and compare optimizers.
  a) Load and preprocess the MNIST dataset.
  b) Design a Feed-Forward Neural Network architecture.
  c) Train the model using: Q1) SGD & Adam | Q2) SGD & RMSProp | Q3) Adam & RMSProp.
  d) Evaluate performance using accuracy and loss curves.
  e) Compare results and justify which optimizer performs better.

ANSWER (what this program demonstrates):
  a) MNIST is loaded; pixels scaled to [0,1]; images flattened to 784-D vectors (see below).
  b) Architecture: Input(784) → Dense(128, relu) → Dense(64, relu) → Dense(10, softmax).
  c) Same model is trained three times with SGD, RMSProp, and Adam (covers every QB pair).
  d) Training loss and validation accuracy per epoch are plotted; test loss/accuracy printed.
  e) Typically Adam converges fastest with best test accuracy; RMSProp beats plain SGD;
     justify using your printed metrics and the saved plot (output/p01_ffn_optimizers.png).
"""
import os

import tensorflow as tf
from _config import OUTPUT_DIR, epochs_default, quick_mode, savefig
import matplotlib.pyplot as plt

os.makedirs(OUTPUT_DIR, exist_ok=True)

# (a) Load and preprocess MNIST
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0
x_train_flat = x_train.reshape(-1, 28 * 28)
x_test_flat = x_test.reshape(-1, 28 * 28)


# (b) Feed-forward architecture
def build_ffn():
    return tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(784,)),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(10, activation="softmax"),
        ]
    )


batch_size = 128
epochs = epochs_default(10)
loss_fn = "sparse_categorical_crossentropy"
metrics = ["accuracy"]
optimizers = {
    "SGD": tf.keras.optimizers.SGD(learning_rate=0.01),
    "RMSProp": tf.keras.optimizers.RMSprop(learning_rate=0.001),
    "Adam": tf.keras.optimizers.Adam(learning_rate=0.001),
}
histories = {}

# (c) Train with each optimizer; (d) metrics collected in history
for name, opt in optimizers.items():
    print(f"\n--- Training with optimizer: {name} ---")
    model = build_ffn()
    model.compile(optimizer=opt, loss=loss_fn, metrics=metrics)
    vb = 2 if not quick_mode() else 1
    history = model.fit(
        x_train_flat,
        y_train,
        validation_split=0.1,
        epochs=epochs,
        batch_size=batch_size,
        verbose=vb,
    )
    test_loss, test_acc = model.evaluate(x_test_flat, y_test, verbose=0)
    print(f"{name} test accuracy: {test_acc:.4f}, test loss: {test_loss:.4f}")
    histories[name] = {
        "history": history.history,
        "test_loss": test_loss,
        "test_acc": test_acc,
    }

# (d) Loss and accuracy curves
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
for name, data in histories.items():
    plt.plot(data["history"]["loss"], label=f"{name} train loss")
plt.title("Training Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()

plt.subplot(1, 2, 2)
for name, data in histories.items():
    plt.plot(data["history"]["val_accuracy"], label=f"{name} val acc")
plt.title("Validation Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.tight_layout()
path = savefig("p01_ffn_optimizers.png")
print("Saved plot:", path)

# (e) Compare final test metrics (justify in your lab report using these numbers + plot)
print("\nFinal test accuracies:")
for name, data in histories.items():
    print(f"{name}: accuracy={data['test_acc']:.4f}, loss={data['test_loss']:.4f}")
