"""Shared settings: headless plots and optional fast training."""
import os

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib

matplotlib.use("Agg")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def quick_mode() -> bool:
    return os.environ.get("DL_QUICK", "0") == "1"


def epochs_default(full: int) -> int:
    return 3 if quick_mode() else full


def savefig(name: str) -> str:
    path = os.path.join(OUTPUT_DIR, name)
    import matplotlib.pyplot as plt

    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    return path
