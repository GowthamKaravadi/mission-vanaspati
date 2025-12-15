from pathlib import Path

import torch

from config import active_config as cfg
from src.core.dataset import create_dataloaders, PlantDiseaseDataset
from src.core.model import create_model, save_model
from src.core.trainer import train


def main() -> None:
    cfg.validate_paths()
    cfg.print_config()

    data_dirs = cfg.get_data_directories()
    if not data_dirs:
        raise FileNotFoundError(
            "No data directories found. Ensure data/PlantVillage or data/NewPlantDiseases/train exists."
        )

    train_loader, val_loader, full_dataset = create_dataloaders(
        data_directories=data_dirs,
        batch_size=cfg.BATCH_SIZE,
        train_split=cfg.TRAIN_SPLIT,
        num_workers=cfg.NUM_WORKERS,
        pin_memory=cfg.PIN_MEMORY,
    )

    full_dataset.save_class_mapping(cfg.CLASS_MAPPING_PATH)

    num_classes = len(full_dataset.class_to_idx)
    device = torch.device(cfg.DEVICE)

    model = create_model(
        num_classes=num_classes,
        pretrained=cfg.USE_PRETRAINED,
        freeze_backbone=cfg.FREEZE_BACKBONE,
        hidden_units=cfg.HIDDEN_UNITS,
        dropout_rate=cfg.DROPOUT_RATE,
        device=device.type,
    )

    history = train(
        model,
        train_loader,
        val_loader,
        device=device,
        epochs=cfg.NUM_EPOCHS,
        lr=cfg.LEARNING_RATE,
        weight_decay=cfg.WEIGHT_DECAY,
        step_size=cfg.LR_STEP_SIZE,
        gamma=cfg.LR_GAMMA,
        use_amp=cfg.USE_MIXED_PRECISION,
        log_interval=cfg.LOG_EVERY_N_BATCHES,
        save_best=cfg.SAVE_BEST_MODEL,
        checkpoint_path=str(cfg.MODEL_SAVE_PATH.with_suffix(".ckpt")),
    )

    save_model(model, cfg.MODEL_SAVE_PATH)
    print(f"Training complete. Model saved to: {cfg.MODEL_SAVE_PATH}")

    if history["val_acc"]:
        print(
            f"Best Val Acc: {max(history['val_acc']):.2f}%  "
            f"Final Val Acc: {history['val_acc'][-1]:.2f}%"
        )


if __name__ == "__main__":
    main()
