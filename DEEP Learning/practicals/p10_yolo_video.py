"""
DL_Practical_QB — Practical 10 Q2: Object detection from video using YOLOv3.

QUESTION:
  a) Load dataset and class labels.
  b) Configure YOLOv3 model and load weights.
  c) Open video source and read frames.
  d) Perform object detection and apply Non-Max Suppression on each frame.
  e) Draw bounding boxes with labels and display video output.

ANSWER:
  a)(b) Same files as image script (names, cfg, weights).
  c) cv2.VideoCapture on bundled GIF or fallback image sequence.
  d) Per frame: blob → forward → parse → NMS (same as single image).
  e) Annotated frames written as PNGs under output/p10_video_frames/ (no GUI required).
"""
import glob
import os
import sys

import cv2
import numpy as np

from _config import OUTPUT_DIR


def find_file(root, name):
    for dirpath, _, filenames in os.walk(root):
        if name in filenames:
            return os.path.join(dirpath, name)
    return None


def main():
    try:
        import kagglehub
    except ImportError:
        print("pip install kagglehub")
        return 1
    try:
        path = kagglehub.dataset_download("aruchomu/data-for-yolo-v3-kernel")
    except Exception as e:
        print("Download failed:", e)
        return 0
    weights_path = find_file(path, "yolov3.weights") or os.path.join(
        path, "yolov3.weights"
    )
    names_path = find_file(path, "coco.names") or os.path.join(path, "coco.names")
    config_path = find_file(path, "yolov3.cfg")
    if not all(
        os.path.isfile(p) for p in (weights_path, names_path, config_path)
    ):
        print("Missing YOLO files")
        return 1

    # (a)
    with open(names_path, "r", encoding="utf-8") as f:
        classes = f.read().splitlines()

    # (b)
    net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
    layer_names = net.getLayerNames()
    out_layers = net.getUnconnectedOutLayers()
    if out_layers.ndim > 1:
        out_layers = out_layers.flatten()
    output_layers = [layer_names[int(i) - 1] for i in out_layers]

    vid_candidates = glob.glob(os.path.join(path, "**", "*.gif"), recursive=True)
    vid_path = vid_candidates[0] if vid_candidates else None
    if not vid_path:
        print("No gif/video found; using first jpg as single frame")
        jpgs = glob.glob(os.path.join(path, "**", "*.jpg"), recursive=True)
        if not jpgs:
            return 1
        vid_path = jpgs[0]

    # (c) Video / GIF / single image fallback
    cap = cv2.VideoCapture(vid_path)
    out_dir = os.path.join(OUTPUT_DIR, "p10_video_frames")
    os.makedirs(out_dir, exist_ok=True)
    frame_i = 0
    max_frames = 5

    while frame_i < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        height, width = frame.shape[:2]
        # (d) Detect + NMS per frame
        blob = cv2.dnn.blobFromImage(
            frame, 1 / 255.0, (416, 416), swapRB=True, crop=False
        )
        net.setInput(blob)
        outputs = net.forward(output_layers)
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
        if len(indexes) > 0:
            for j in np.array(indexes).flatten():
                x, y, w, h = boxes[j]
                label = classes[class_ids[j]]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
        # (e) Save frame with boxes (display would use cv2.imshow in GUI environment)
        out_path = os.path.join(out_dir, f"frame_{frame_i:04d}.png")
        cv2.imwrite(out_path, frame)
        print("Wrote", out_path)
        frame_i += 1
    cap.release()
    return 0


if __name__ == "__main__":
    sys.exit(main())
