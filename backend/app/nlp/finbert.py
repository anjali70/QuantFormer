import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)


class FinBERT:
    def __init__(self):
        model_name = "ProsusAI/finbert"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name
        )
        self.model.eval()

    @torch.no_grad()
    def analyze(self, text):
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128,
        )

        outputs = self.model(
            **inputs,
            output_hidden_states=True,
        )

        probabilities = torch.softmax(outputs.logits, dim=1)[0]

        positive = float(probabilities[0])
        negative = float(probabilities[1])
        neutral = float(probabilities[2])

        sentiment_score = positive - negative

        embedding = (
            outputs.hidden_states[-1][:, 0, :]
            .squeeze(0)
            .tolist()
        )

        return {
            "text": text,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "sentiment_score": sentiment_score,
            "embedding": embedding,
        }