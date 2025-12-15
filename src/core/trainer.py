from __future__ import annotations

import time
from typing import Dict, Tuple, List, Optional

import torch
import torch.nn as nn
from torch.utils.data import DataLoader


def _to_device(*tensors, device: torch.device):
    return [t.to(device, non_blocking=True) for t in tensors]


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    use_amp: bool = False,
    log_interval: int = 50,
) -> Tuple[float, float]:
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    for batch_idx, (images, labels) in enumerate(loader):
        images, labels = _to_device(images, labels, device=device)

        optimizer.zero_grad(set_to_none=True)
        with torch.cuda.amp.autocast(enabled=use_amp):
            outputs = model(images)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        if (batch_idx + 1) % log_interval == 0:
            avg_loss = running_loss / (batch_idx + 1)
            acc = 100.0 * correct / total if total else 0.0
            print(f"  Batch {batch_idx+1}/{len(loader)}  Loss: {avg_loss:.4f}  Acc: {acc:.2f}%")

    avg_loss = running_loss / len(loader)
    accuracy = 100.0 * correct / total if total else 0.0
    return avg_loss, accuracy


def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float]:
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images, labels = _to_device(images, labels, device=device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    avg_loss = running_loss / len(loader)
    accuracy = 100.0 * correct / total if total else 0.0
    return avg_loss, accuracy


def train(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    *,
    device: torch.device,
    epochs: int = 10,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    step_size: int = 5,
    gamma: float = 0.1,
    use_amp: bool = False,
    log_interval: int = 50,
    save_best: bool = True,
    checkpoint_path: Optional[str] = None,
) -> Dict[str, List[float]]:
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)

    history: Dict[str, List[float]] = {
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "lr": [],
    }

    best_val_acc = -1.0
    best_state: Optional[Dict[str, torch.Tensor]] = None

    print("Starting training...")
    for epoch in range(1, epochs + 1):
        print(f"\nEpoch {epoch}/{epochs}")

        t0 = time.time()
        train_loss, train_acc = train_one_epoch(
            model,
            train_loader,
            optimizer,
            criterion,
            device,
            use_amp=use_amp,
            log_interval=log_interval,
        )

        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        epoch_time = time.time() - t0

        scheduler.step()
        current_lr = scheduler.get_last_lr()[0]

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)
        history["lr"].append(current_lr)

        print(
            f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%  "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%  "
            f"LR: {current_lr:.6f}  Time: {epoch_time:.1f}s"
        )

        if save_best and val_acc > best_val_acc:
            best_val_acc = val_acc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            if checkpoint_path:
                torch.save({"state_dict": best_state, "val_acc": best_val_acc}, checkpoint_path)
                print(f"  Saved checkpoint to {checkpoint_path}")

    if save_best and best_state is not None:
        model.load_state_dict(best_state)
        print(f"Loaded best model state (Val Acc: {best_val_acc:.2f}%)")

    return history
