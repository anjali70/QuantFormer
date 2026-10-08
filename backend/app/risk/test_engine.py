from risk_engine import RiskEngine

risk_engine = RiskEngine(threshold=0.80)

high_risk = risk_engine.check_risk(0.85)
low_risk = risk_engine.check_risk(0.40)

print("High Risk Test:")
print(high_risk)

print("\nLow Risk Test:")
print(low_risk)