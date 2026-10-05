import torch
from torch.utils.data import Dataset, DataLoader


class QuantFormerDataset(Dataset):
    def __init__(self, market_data, sentiment_data, labels):
        self.market_data = torch.tensor(
            market_data, dtype=torch.float32
        )

        self.sentiment_data = torch.tensor(
            sentiment_data, dtype=torch.float32
        )

        self.labels = torch.tensor(
            labels, dtype=torch.float32
        )

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        return (
            self.market_data[index],
            self.sentiment_data[index],
            self.labels[index]
        )


def create_dataloader(
    market_data,
    sentiment_data,
    labels,
    batch_size=4
):
    dataset = QuantFormerDataset(
        market_data,
        sentiment_data,
        labels
    )

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True
    )