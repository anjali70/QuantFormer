# train and saves the model
from pathlib import Path
import pickle

import torch
from lightning.pytorch import Trainer
from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint

from app.models.tft_setup import (
    DATA_DIR,
    load_data,
    build_datasets,
    build_model,
)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    training, validation = build_datasets(df)

    train_loader = training.to_dataloader(
        train=True,
        batch_size=32,
        num_workers=0,
    )

    validation_loader = validation.to_dataloader(
        train=False,
        batch_size=32,
        num_workers=0,
    )

    model = build_model(training)

    checkpoint_callback = ModelCheckpoint(
        dirpath=str(DATA_DIR),
        filename="tft-best",
        monitor="val_loss",
        mode="min",
        save_top_k=1,
    )

    early_stopping = EarlyStopping(
        monitor="val_loss",
        patience=3,
        mode="min",
    )

    trainer = Trainer(
        max_epochs=10,
        accelerator="auto",
        devices=1,
        gradient_clip_val=0.1,
        callbacks=[checkpoint_callback, early_stopping],
        enable_model_summary=True,
        log_every_n_steps=1,
        enable_progress_bar=True,
    )

    trainer.fit(
        model,
        train_dataloaders=train_loader,
        val_dataloaders=validation_loader,
    )

    best_checkpoint = checkpoint_callback.best_model_path

    if not best_checkpoint:
        raise RuntimeError("Training did not produce a model checkpoint.")

    # Save the parameters needed to rebuild the TFT dataset for prediction.
    parameters_file = DATA_DIR / "tft_dataset_parameters.pkl"
    with parameters_file.open("wb") as file:
        pickle.dump(training.get_parameters(), file)

    # Copy the best checkpoint to a stable filename.
    best_model_file = DATA_DIR / "tft_model.ckpt"
    state = torch.load(
        best_checkpoint,
        map_location="cpu",
        weights_only=False,
    )
    torch.save(state, best_model_file)

    print("\nTFT training completed.")
    print(f"Best validation loss: {checkpoint_callback.best_model_score}")
    print(f"Saved model: {best_model_file}")
    print(f"Saved dataset parameters: {parameters_file}")
    print(f"Dataset observations: {len(df)}")


if __name__ == "__main__":
    main()
