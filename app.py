import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="LLM Evals Dashboard", layout="wide")

logs = pd.read_csv("logs_export.csv")
res = pd.read_csv("results_export.csv")
logs["total_tokens"] = logs["prompt_tokens"] + logs["completion_tokens"]

cases = {}
for line in open("evals.jsonl", encoding="utf-8"):
    c = json.loads(line)
    cases[c["id"]] = c
res["expected"] = res["case_id"].map(lambda i: " | ".join(cases[i]["expected"]))

page = st.sidebar.radio("Page", ["Overview", "Call logs", "Prompt comparison", "Failures"])

if page == "Overview":
    st.title("LLM Evals Dashboard")
    ok = logs[logs["error"].isna()]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("LLM calls", len(logs))
    c2.metric("Total tokens", int(ok["total_tokens"].sum()))
    c3.metric("Avg latency (ms)", int(ok["latency_ms"].mean()))
    c4.metric("Errors", int(logs["error"].notna().sum()))
    hid = res[res["split"] == "hidden"]
    if len(hid):
        st.subheader("Hidden set (run once, final prompt)")
        st.metric("Pass", f"{int(hid['passed'].sum())}/{len(hid)}")

elif page == "Call logs":
    st.title("Call logs")
    versions = sorted(logs["prompt_version"].dropna().unique())
    pv = st.multiselect("Prompt version", versions, default=versions)
    view = logs[logs["prompt_version"].isin(pv)]
    st.dataframe(view[["ts", "model", "prompt_version", "prompt_tokens",
                       "completion_tokens", "latency_ms", "error"]],
                 use_container_width=True)
    st.line_chart(view.set_index("id")["latency_ms"])

elif page == "Prompt comparison":
    st.title("Prompt comparison (dev set)")
    dev = res[res["split"] == "dev"]
    latest = dev.groupby("prompt_version")["run_id"].max()
    dev = dev[dev["run_id"].isin(latest.values)]
    summ = dev.groupby("prompt_version")["passed"].agg(["sum", "count"])
    summ["pass_rate_%"] = (summ["sum"] / summ["count"] * 100).round(1)
    calls = logs[logs["input_text"].str.startswith("Context:", na=False)
                 & logs["error"].isna()]
    perf = calls.groupby("prompt_version")[["total_tokens", "latency_ms"]].mean().round(0)
    st.dataframe(summ.join(perf), use_container_width=True)
    st.subheader("Passes per tag")
    st.bar_chart(dev.pivot_table(index="tag", columns="prompt_version",
                                 values="passed", aggfunc="sum"))

else:
    st.title("Failed cases")
    f = res[res["passed"] == 0]
    st.dataframe(f[["split", "prompt_version", "tag", "reason", "expected", "output"]],
                 use_container_width=True)