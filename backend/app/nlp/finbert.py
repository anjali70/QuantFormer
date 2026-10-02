from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class FinBERT:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "ProsusAI/finbert"
        )

    def analyze(self, text):
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True
        )

        with torch.no_grad():
            outputs = self.model(
                **inputs,
                output_hidden_states=True
            )

        probabilities = torch.softmax(outputs.logits, dim=1)[0]

        positive = float(probabilities[0])
        negative = float(probabilities[1])
        neutral = float(probabilities[2])

        sentiment_score = positive - negative

        # Get 768-dimensional FinBERT embedding
        embedding = outputs.hidden_states[-1][:, 0, :].squeeze().tolist()

        return {
            "text": text,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "sentiment_score": sentiment_score,
            "embedding": embedding
        }