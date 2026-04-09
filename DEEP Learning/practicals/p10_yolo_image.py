"""
DL_Practical_QB — Practical 10 Q1: Object detection from image using YOLOv3.

QUESTION:
  a) Load dataset and class labels.
  b) Configure YOLOv3 model and load weights.
  c) Read input image and perform forward pass.
  d) Extract detections and apply Non-Max Suppression.
  e) Draw bounding boxes and display output.

ANSWER:
  a) coco.names + yolov3.weights + yolov3.cfg from kagglehub bundle.
  b) cv2.dnn.readNetFromDarknet(cfg, weights); output layer names from unconnected outs.
  c) blobFromImage 416×416, net.setInput, net.forward.
  d) Parse boxes/scores, cv2.dnn.NMSBoxes to remove overlaps.
  e) Rectangles + putText on image; saved PNG under output/ (headless-friendly).
"""
import glob
import os
import sys

import cv2
import numpy as np

from _config import OUTPUT_DIR
import matplotlib.pyplot as plt


def find_file(root, name):
    for dirpath, _, filenames in os.walk(root):
        if name in filenames:
            return os.path.join(dirpath, name)
    return None


def main():
    try:
        import kagglehub
    except ImportError:
        print("pip install kagglehub opencv-python-headless")
        return 1
    try:
        path = kagglehub.dataset_download("aruchomu/data-for-yolo-v3-kernel")
    except Exception as e:
        print("YOLO dataset download failed:", e)
        return 0
    weights_path = find_file(path, "yolov3.weights") or os.path.join(
        path, "yolov3.weights"
    )
    names_path = find_file(path, "coco.names") or os.path.join(path, "coco.names")
    config_path = find_file(path, "yolov3.cfg")
    if not config_path:
        print("yolov3.cfg not found under", path)
        return 1
    if not os.path.isfile(weights_path) or not os.path.isfile(names_path):
        print("Missing weights or names", weights_path, names_path)
        return 1

    # (a) Class labels
    with open(names_path, "r", encoding="utf-8") as f:
        classes = f.read().splitlines()

    # (b) Load network
    net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
    layer_names = net.getLayerNames()
    out_layers = net.getUnconnectedOutLayers()
    if out_layers.ndim > 1:
        out_layers = out_layers.flatten()
    output_layers = [layer_names[int(i) - 1] for i in out_layers]

    img_candidates = glob.glob(os.path.join(path, "**", "*.jpg"), recursive=True)
    img_path = next((p for p in img_candidates if "dog" in p.lower()), None)
    if not img_path and img_candidates:
        img_path = img_candidates[0]
    if not img_path:
        print("No jpg found in dataset")
        return 1

    img = cv2.imread(img_path)
    if img is None:
        print("Could not read", img_path)
        return 1
    height, width = img.shape[:2]
    # (c) Forward pass
    blob = cv2.dnn.blobFromImage(
        img, 1 / 255.0, (416, 416), swapRB=True, crop=False
    )
    net.setInput(blob)
    outputs = net.forward(output_layers)

    # (d) Detections + NMS
    boxes, confidences, class_ids = [], [], []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = int(np.argmax(scores))
            confidence = float(scores[class_id])
            if confidence > 0.5:
                cx, cy, w, h = detection[0:4] * np.array(
                    [width, height, width, height]
                )
                x = int(cx - w / 2)
                y = int(cy - h / 2)
                boxes.append([x, y, int(w), int(h)])
                confidences.append(confidence)
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    # (e) Draw boxes and save output image
    if len(indexes) > 0:
        for i in np.array(indexes).flatten():
            x, y, w, h = boxes[i]
            label = classes[class_ids[i]]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                img,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )
    out_bgr = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(10, 8))
    plt.imshow(out_bgr)
    plt.axis("off")
    out_path = os.path.join(OUTPUT_DIR, "p10_yolo_image.png")
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close()
    print("Saved", out_path, "| raw boxes:", len(boxes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
