import os, time
from dotenv import load_dotenv
from groq import Groq
from logger import init_db, log_call

load_dotenv()
init_db()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-20b"

def call_llm(user_input, system_prompt, prompt_version="A", model=MODEL):
    start = time.time()
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0,
        )
        out = r.choices[0].message.content
        ms = int((time.time() - start) * 1000)
        log_call(model, prompt_version, user_input, out,
                 r.usage.prompt_tokens, r.usage.completion_tokens, ms)
        return out
    except Exception as e:
        ms = int((time.time() - start) * 1000)
        log_call(model, prompt_version, user_input, None, 0, 0, ms, str(e))
        raise