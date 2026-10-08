class RiskEngine:
    def __init__(self, threshold=0.80):
        self.threshold = threshold

    def check_risk(self, crash_probability):
        if crash_probability >= self.threshold:
            return {
                "status": "HALTED",
                "message": "Trading halted due to high crash risk."
            }

        return {
            "status": "ACTIVE",
            "message": "Trading active."
        }