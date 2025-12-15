from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt


def plot_history(history: Dict[str, List[float]], out_path: Path | None = None) -> Path | None:
    if not history:
        return None

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))

    axs[0].plot(history.get("train_loss", []), label="train")
    axs[0].plot(history.get("val_loss", []), label="val")
    axs[0].set_title("Loss")
    axs[0].set_xlabel("Epoch")
    axs[0].set_ylabel("Loss")
    axs[0].legend()

    axs[1].plot(history.get("train_acc", []), label="train")
    axs[1].plot(history.get("val_acc", []), label="val")
    axs[1].set_title("Accuracy (%)")
    axs[1].set_xlabel("Epoch")
    axs[1].set_ylabel("Accuracy")
    axs[1].legend()

    plt.tight_layout()

    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        return out_path

    plt.show()
    return None
