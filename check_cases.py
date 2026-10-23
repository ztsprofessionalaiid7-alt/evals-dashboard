import json

cases = [json.loads(l) for l in open("evals.jsonl", encoding="utf-8")]
dev = [c for c in cases if c["split"] == "dev"]
hidden = [c for c in cases if c["split"] == "hidden"]
print("dev:", len(dev), "hidden:", len(hidden))
for c in dev[:3]:
    print(c["tag"], "|", c["expected"], "|", c["input"][-80:])