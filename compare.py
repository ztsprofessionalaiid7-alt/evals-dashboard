import json, sqlite3

con = sqlite3.connect("logs.db")
cases = {}
for l in open("evals.jsonl", encoding="utf-8"):
    c = json.loads(l)
    cases[c["id"]] = c

def summary(prompt):
    r = con.execute("select run_id from eval_results where prompt_version=? "
                    "and split='dev' order by id desc limit 1", (prompt,)).fetchone()
    if not r:
        return None
    rows = con.execute("select case_id, tag, passed, reason from eval_results "
                       "where run_id=?", (r[0],)).fetchall()
    toks = lat = n = 0
    for cid, tag, p, why in rows:
        x = con.execute("select prompt_tokens+completion_tokens, latency_ms "
                        "from llm_logs where prompt_version=? and input_text=? "
                        "and error is null order by id desc limit 1",
                        (prompt, cases[cid]["input"])).fetchone()
        if x:
            toks += x[0]; lat += x[1]; n += 1
    return {"rows": rows, "passed": sum(r_[2] for r_ in rows),
            "total": len(rows), "toks": toks, "lat": lat // n if n else 0}

S = {}
for v in ["A", "B", "C"]:
    s = summary(v)
    if s:
        S[v] = s

print("Prompt | Pass | Tokens | Avg latency ms")
for v, s in S.items():
    print(f"{v} | {s['passed']}/{s['total']} | {s['toks']} | {s['lat']}")

print("\nPer tag:")
for tag in ["easy", "hard", "no_answer", "attack"]:
    parts = []
    for v, s in S.items():
        r = [x[2] for x in s["rows"] if x[1] == tag]
        parts.append(f"{v} {sum(r)}/{len(r)}")
    print(tag + ": " + " | ".join(parts))

last = list(S)[-1]
print(f"\nStill failing in {last}:")
for cid, tag, p, why in S[last]["rows"]:
    if not p:
        print("-", tag, "|", why, "|", cid)