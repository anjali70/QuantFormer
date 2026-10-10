class RiskEngine:
    def __init__(self, threshold=0.80):
        self.threshold = threshold

    def check_risk(self, crash_probability):
        halted = float(crash_probability) >= self.threshold

        if halted:
            return {
                "status": "HALTED",
                "message": (
                    "Trading halted due to high "
                    "simulated crash risk."
                ),
            }

        return {
            "status": "ACTIVE",
            "message": (
                "Trading active; risk is below threshold."
            ),
        }