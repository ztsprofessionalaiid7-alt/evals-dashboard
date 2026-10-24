import sqlite3
import pandas as pd

con = sqlite3.connect("logs.db")
pd.read_sql("select * from llm_logs", con).to_csv("logs_export.csv", index=False)
pd.read_sql("select * from eval_results", con).to_csv("results_export.csv", index=False)
print("exported")