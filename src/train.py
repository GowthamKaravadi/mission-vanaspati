from pathlib import Path
import sys

import torch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
        freeze_backbone=cfg.FREEZE_BACKBONE if not cfg.TWO_STAGE_TRAINING else True,  # Freeze for stage 1
        hidden_units=cfg.HIDDEN_UNITS,
        dropout_rate=cfg.DROPOUT_RATE,
        device=device.type,
    )

    total_epochs = cfg.STAGE1_EPOCHS + cfg.STAGE2_EPOCHS if cfg.TWO_STAGE_TRAINING else cfg.NUM_EPOCHS
    
    history = train(
        model,
        train_loader,
        val_loader,
        device=device,
        epochs=total_epochs,
        lr=cfg.LEARNING_RATE,
        weight_decay=cfg.WEIGHT_DECAY,
        scheduler_type=cfg.LR_SCHEDULER,
        step_size=cfg.LR_STEP_SIZE,
        gamma=cfg.LR_GAMMA,
        lr_min=cfg.LR_MIN,
        use_amp=cfg.USE_MIXED_PRECISION,
        log_interval=cfg.LOG_EVERY_N_BATCHES,
        save_best=cfg.SAVE_BEST_MODEL,
        checkpoint_path=str(cfg.MODEL_SAVE_PATH.with_suffix(".ckpt")),
        use_mixup=cfg.USE_MIXUP,
        mixup_alpha=cfg.MIXUP_ALPHA,
        two_stage=cfg.TWO_STAGE_TRAINING,
        stage1_epochs=cfg.STAGE1_EPOCHS,
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
