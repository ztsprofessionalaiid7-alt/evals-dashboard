import json, sqlite3

con = sqlite3.connect("logs.db")
cases = {}
for l in open("evals.jsonl", encoding="utf-8"):
    c = json.loads(l)
    cases[c["id"]] = c

def summary(prompt):
    r = con.execute("select run_id from eval_results where prompt_version=? "
                    "and split='dev' order by id desc limit 1", (prompt,)).fetchone()
    run = r[0]
    rows = con.execute("select case_id, tag, passed, reason from eval_results "
                       "where run_id=?", (run,)).fetchall()
    toks = lat = n = 0
    for cid, tag, p, why in rows:
        x = con.execute("select prompt_tokens+completion_tokens, latency_ms "
                        "from llm_logs where prompt_version=? and input_text=? "
                        "and error is null order by id desc limit 1",
                        (prompt, cases[cid]["input"])).fetchone()
        if x:
            toks += x[0]; lat += x[1]; n += 1
    return {"run": run, "rows": rows, "passed": sum(r[2] for r in rows),
            "total": len(rows), "toks": toks, "lat": lat // n if n else 0}

A, B = summary("A"), summary("B")
print("Prompt | Pass | Tokens | Avg latency ms")
for name, s in (("A", A), ("B", B)):
    print(f"{name} | {s['passed']}/{s['total']} | {s['toks']} | {s['lat']}")

print("\nPer tag (A -> B):")
for tag in ["easy", "hard", "no_answer", "attack"]:
    a = [r[2] for r in A["rows"] if r[1] == tag]
    b = [r[2] for r in B["rows"] if r[1] == tag]
    print(f"{tag}: {sum(a)}/{len(a)} -> {sum(b)}/{len(b)}")

print("\nStill failing in B:")
for cid, tag, p, why in B["rows"]:
    if not p:
        print("-", tag, "|", why, "|", cid)