"""
Run all DL practical scripts. Set DL_QUICK=1 (default here) for fewer epochs.
Kaggle-dependent scripts exit 0 if download fails (skipped).
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("DL_QUICK", "1")
os.environ.setdefault("MPLBACKEND", "Agg")

SCRIPTS = [
    "p01_ffn_optimizers.py",
    "p02_regularization.py",
    "p03_cifar10_cnn.py",
    "p03_mnist_cnn.py",
    "p03_fashion_mnist_cnn.py",
    "p04_autoencoder_mnist.py",
    "p04_autoencoder_cifar.py",
    "p05_mnist_digit_nn.py",
    "p06_transfer_learning_vgg16.py",
    "p07_gan_mnist.py",
    "p07_gan_fashion.py",
    "p08_rnn_rainfall.py",
    "p08_rnn_temperature.py",
    "p09_lstm_sentiment.py",
    "p10_yolo_image.py",
    "p10_yolo_video.py",
]


def main():
    failed = []
    for name in SCRIPTS:
        path = os.path.join(ROOT, name)
        print("\n" + "=" * 60)
        print("Running", name)
        print("=" * 60)
        r = subprocess.run([sys.executable, path], cwd=ROOT)
        if r.returncode != 0:
            failed.append((name, r.returncode))
    print("\n" + "=" * 60)
    if failed:
        print("Failed:")
        for n, c in failed:
            print(" ", n, "exit", c)
        return 1
    print("All scripts finished (check output/ and console).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
