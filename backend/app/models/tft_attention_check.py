
from pathlib import Path

import torch
from pytorch_forecasting import TemporalFusionTransformer

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MODEL_FILE = DATA_DIR / "tft_model.ckpt"


def main():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Trained TFT checkpoint missing. Run tft_train.py first."
        )

    model = TemporalFusionTransformer.load_from_checkpoint(
        str(MODEL_FILE),
        map_location="cpu",
    )
    model.eval()

    print("TFT checkpoint loaded successfully.")
    print("Architecture:", type(model).__name__)
    print("Attention heads:", model.hparams.attention_head_size)
    print("Hidden size:", model.hparams.hidden_size)

    if not hasattr(model, "interpret_output"):
        raise RuntimeError(
            "This model does not expose interpret_output()."
        )

    print(
        "\nThe TFT model supports interpretation of attention "
        "and variable-selection outputs."
    )
    print(
        "Run interpretation on a validation batch to inspect "
        "actual learned attention weights."
    )


if __name__ == "__main__":
    main()
