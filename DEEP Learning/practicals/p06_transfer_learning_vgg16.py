"""
DL_Practical_QB — Practical 6 Q1: Transfer learning for image classification (cats vs dogs).

QUESTION:
  a) Load the Cats vs Dogs dataset.
  b) Implement Transfer Learning using the VGG16 model.
  c) Freeze layers and modify final layers.
  d) Train the model on the new dataset.
  e) Evaluate and analyze performance.

ANSWER:
  a) Dataset downloaded via kagglehub (folder with class subdirs); ImageDataGenerator rescales RGB.
  b) VGG16(weights='imagenet', include_top=False) as feature extractor.
  c) base_model.trainable = False; new head = Flatten → Dense(256,relu) → Dense(1,sigmoid).
  d) Binary classification with flow_from_directory; train and validation generators (80/20 split).
  e) model.evaluate on validation generator reports accuracy; faster convergence than from scratch.
"""
import sys

import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from _config import epochs_default

epochs = max(1, epochs_default(2))


def main():
    try:
        import kagglehub
    except ImportError:
        print("Install kagglehub: pip install kagglehub")
        return 1
    try:
        path = kagglehub.dataset_download("chetankv/dogs-cats-images")
    except Exception as e:
        print(
            "Could not download cats/dogs dataset (network/Kaggle). Error:", e,
            "\nSet KAGGLE_USERNAME/KAGGLE_KEY if required, or run when online.",
        )
        return 0
    print("Dataset path:", path)

    # (a)(d) Load from directory; train/val split
    train_datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)
    train_generator = train_datagen.flow_from_directory(
        directory=path,
        target_size=(224, 224),
        batch_size=32,
        class_mode="binary",
        subset="training",
    )
    validation_generator = train_datagen.flow_from_directory(
        directory=path,
        target_size=(224, 224),
        batch_size=32,
        class_mode="binary",
        subset="validation",
    )

    # (b)(c) VGG16 backbone frozen; custom classification head
    base_model = VGG16(
        weights="imagenet", include_top=False, input_shape=(224, 224, 3)
    )
    base_model.trainable = False
    model = Sequential(
        [
            base_model,
            Flatten(),
            Dense(256, activation="relu"),
            Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"]
    )
    model.fit(
        train_generator,
        validation_data=validation_generator,
        epochs=epochs,
        verbose=1,
    )
    # (e) Performance analysis
    model.evaluate(validation_generator, verbose=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
