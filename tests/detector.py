import json
from collections import Counter

def detect_behavior_leak(events):
    methods = [e["method"] for e in events]
    freq = Counter(methods)

    if freq["eth_getBalance"] >= 3:
        return {
            "type": "behavior",
            "confidence": 0.8,
            "reason": "Repeated balance polling detected"
        }

    return None

with open("sample_traffic.json") as f:
    data = json.load(f)

result = detect_behavior_leak(data)

print(result)
