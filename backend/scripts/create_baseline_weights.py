#!/usr/bin/env python3
"""
Create baseline (unvalidated) ensemble weights for bootstrapping.

Honest note: these are unvalidated baseline weights for bootstrapping —
not clinically validated. They exist so the service can load an explicit
weight file rather than silently using random init at inference time.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = REPO_ROOT / "models"
WEIGHT_PATH = MODELS_DIR / "ensemble_model.pth"
REGISTRY_PATH = MODELS_DIR / "registry.json"
VERSION = "v0.0.1_unvalidated_baseline"
HONEST_NOTE = (
    "unvalidated baseline weights for bootstrapping — not clinically validated"
)


def update_registry(weight_path: Path, created: bool) -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
    else:
        registry = {"models": [], "current_model": None}

    for entry in registry.get("models", []):
        entry["is_active"] = False

    registry["models"] = [
        m for m in registry.get("models", []) if m.get("version") != VERSION
    ]

    entry = {
        "version": VERSION,
        "model_path": str(Path("models") / "ensemble_model.pth"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "note": HONEST_NOTE,
            "validated": False,
            "clinical_validation": False,
            "training": {
                "best_val_loss": None,
                "epochs_trained": 0,
            },
            "test": {
                "alzheimer": {
                    "accuracy": None,
                    "sensitivity": None,
                    "specificity": None,
                    "auc_roc": None,
                },
                "parkinson": {
                    "accuracy": None,
                    "sensitivity": None,
                    "specificity": None,
                    "auc_roc": None,
                },
            },
        },
        "description": HONEST_NOTE,
        "is_active": True,
        "weights_created": created,
    }
    registry["models"].append(entry)
    registry["current_model"] = VERSION

    for legacy in registry["models"]:
        if legacy.get("version") != VERSION and isinstance(legacy.get("metrics"), dict):
            legacy["metrics"].setdefault(
                "honesty_note",
                "Legacy metrics may be synthetic placeholders — not clinically validated",
            )

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print(f"Updated registry at {REGISTRY_PATH} (active={VERSION})")


def _build_network(torch, nn, input_dim: int = 50, hidden_dims=None):
    """Minimal MultiModalNeuralNetwork matching ai_model_service architecture."""
    if hidden_dims is None:
        hidden_dims = [256, 128, 64]

    class MultiModalNeuralNetwork(nn.Module):
        def __init__(self):
            super().__init__()
            layers = []
            prev_dim = input_dim
            for hidden_dim in hidden_dims:
                layers.append(nn.Linear(prev_dim, hidden_dim))
                layers.append(nn.ReLU())
                layers.append(nn.BatchNorm1d(hidden_dim))
                layers.append(nn.Dropout(0.3))
                prev_dim = hidden_dim
            self.feature_extractor = nn.Sequential(*layers)
            self.alzheimer_head = nn.Sequential(
                nn.Linear(hidden_dims[-1], 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.Sigmoid(),
            )
            self.parkinson_head = nn.Sequential(
                nn.Linear(hidden_dims[-1], 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.Sigmoid(),
            )

        def forward(self, x):
            features = self.feature_extractor(x)
            return self.alzheimer_head(features), self.parkinson_head(features)

    return MultiModalNeuralNetwork()


def create_weights() -> bool:
    try:
        import torch
        import torch.nn as nn
    except Exception as e:
        print(f"Torch unavailable ({e}); updating registry honesty only.")
        return False

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(42)
    model = _build_network(torch, nn)
    model.eval()
    torch.save(model.state_dict(), WEIGHT_PATH)
    print(f"Saved baseline state_dict to {WEIGHT_PATH}")
    return True


def main() -> int:
    created = create_weights()
    update_registry(WEIGHT_PATH, created=created)
    if not created:
        print(
            "NOTE: ensemble_model.pth was not created (torch missing). "
            f"Registry still points to models/ensemble_model.pth with honest metrics note."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
