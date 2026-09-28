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
            outputs = self.model(**inputs)

        probabilities = torch.softmax(outputs.logits, dim=1)[0]

        labels = ["positive", "negative", "neutral"]
        result = {
            labels[i]: float(probabilities[i])
            for i in range(3)
        }

        sentiment_score = (
            result["positive"] - result["negative"]
        )

        return {
            "text": text,
            "sentiment": result,
            "score": sentiment_score
        }