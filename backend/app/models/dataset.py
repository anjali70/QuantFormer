import torch
from torch.utils.data import Dataset, DataLoader


class QuantFormerDataset(Dataset):
    def __init__(self, market_data, sentiment_data, labels):
        if not (
            len(market_data)
            == len(sentiment_data)
            == len(labels)
        ):
            raise ValueError(
                "Market data, sentiment data and labels "
                "must have equal lengths."
            )

        self.market = torch.as_tensor(
            market_data, dtype=torch.float32
        )
        self.sentiment = torch.as_tensor(
            sentiment_data, dtype=torch.float32
        )
        self.labels = torch.as_tensor(
            labels, dtype=torch.float32
        )

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        return (
            self.market[index],
            self.sentiment[index],
            self.labels[index],
        )


def create_dataloader(
    market_data,
    sentiment_data,
    labels,
    batch_size=4,
    shuffle=True,
):
    dataset = QuantFormerDataset(
        market_data,
        sentiment_data,
        labels,
    )

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
    )