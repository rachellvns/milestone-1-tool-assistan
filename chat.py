import anthropic
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
from config import API_KEY, BASE_URL, MODEL
from tools import TOOLS, REGISTRY
from extract import extract_json, render_report_from_json, save_report_json

client = anthropic.Anthropic(api_key=API_KEY, base_url=BASE_URL)

PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8")

PROMPTS = {
    "default": load_prompt("default_output"),
    "json": load_prompt("json_output"),
}

# report mode: "default" (default, human-readable, streamed) or "json" (structured output, buffered)
REPORT_MODE = "default"

# holds the most recent successfully-parsed JSON report, so it can be saved
# on demand via "/save report" without needing to re-run a turn
last_report: dict | None = None


class Transcript(BaseModel):
    saved_at: datetime
    system: str
    turns: list[dict]

# store conversation memory
history: list[dict] = []

# track cumulative token usage
total_in = total_out = 0

# USD per 1M tokens (input/output)
PRICE_IN, PRICE_OUT = 3.0, 15.0

# maximum exchanges kept
MAX_TURNS = 10

# maximum tool calls allowed per user turn
MAX_TOOL_CALLS = 8

# history cap
def capped(h: list[dict]) -> list[dict]:
    return h[-MAX_TURNS * 2:]


def run_turn(msgs: list) -> str:
    """Runs the agentic tool-use loop. In 'default' (prose) mode, text is
    streamed live to the terminal as it's generated. In 'json' mode, output
    is buffered (not streamed) since we need the complete text before we
    can parse/validate it as JSON."""
    global total_in, total_out
    calls = 0
    system_prompt = PROMPTS[REPORT_MODE]
    stream_output = (REPORT_MODE == "default")

    while True:
        if stream_output:
            with client.messages.stream(model=MODEL, max_tokens=1000,
                    system=system_prompt, tools=TOOLS, messages=msgs) as stream:
                for chunk in stream.text_stream:
                    print(chunk, end="", flush=True)
                resp = stream.get_final_message()
        else:
            resp = client.messages.create(model=MODEL, max_tokens=1000,
                    system=system_prompt, tools=TOOLS, messages=msgs)

        total_in += resp.usage.input_tokens
        total_out += resp.usage.output_tokens

        if stream_output:
            print()  # newline after any streamed text, before DEBUG/tool lines
        print(f"DEBUG: stop_reason={resp.stop_reason}")

        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content
                           if b.type == "text")

        tool_blocks = [b for b in resp.content if b.type == "tool_use"]
        for b in tool_blocks:
            print(f"DEBUG: calling tool '{b.name}' with input {b.input}")

        calls += len(tool_blocks)
        if calls > MAX_TOOL_CALLS:
            return "Stopped: too many tool calls."
        msgs.append({"role": "assistant",
                     "content": resp.content})
        results = [{"type": "tool_result",
                    "tool_use_id": b.id,
                    "content": REGISTRY[b.name](b.input)}
                   for b in tool_blocks]
        msgs.append({"role": "user", "content": results})


while True:
    # get user input
    user = input("you> ").strip()

    # handle exit commands
    if user in {"/quit", "exit"}: break

    # display current token usage and estimated API cost
    if user == "/tokens":
        cost = (total_in/1e6 * PRICE_IN) + (total_out/1e6 * PRICE_OUT)
        print(
                f"Input tokens: {total_in}\n"
                f"Output tokens: {total_out}\n"
                f"Estimated cost: ${cost:.4f}"
            )
        continue

    # switch report mode
    if user == "/mode default":
        REPORT_MODE = "default"
        print("Switched to default report mode (streamed).")
        continue

    if user == "/mode json":
        REPORT_MODE = "json"
        print("Switched to JSON report mode (buffered).")
        continue

    # save the full conversation transcript
    if user == "/save":
        t = Transcript(saved_at=datetime.now(),
                        system=PROMPTS[REPORT_MODE],
                        turns=history)
        path = f"Transcript-{t.saved_at:%Y%m%d-%H%M%S}.json"
        with open(path, "w", encoding="utf-8") as f:
            f.write(t.model_dump_json(indent=2))
        print("saved", path)
        continue

    # save just the last health report (not the whole conversation)
    if user == "/save report":
        if last_report is None:
            print("No health report available yet — generate one in JSON mode first "
                  "(/mode json, then ask for a report).")
        else:
            path = save_report_json(last_report)
            print("saved", path)
        continue

    # store user message for multi-turn conversation context
    history.append({"role": "user", "content": user})

    if REPORT_MODE == "default":
        print("bot> ", end="", flush=True)
        reply = run_turn(list(capped(history)))
        # reply was already streamed live above; nothing left to print
    else:
        reply = run_turn(list(capped(history)))
        parsed = extract_json(reply)
        if parsed is None:
            # model didn't return usable JSON - fall back to showing raw reply
            print("bot> [Warning: expected structured JSON but couldn't parse the response. Showing raw output instead.]")
            print(reply)
        else:
            last_report = parsed
            try:
                rendered = render_report_from_json(parsed)
                print("bot>", rendered)
                print("(tip: type /save report to save this as a JSON file)")
            except Exception as e:
                print(f"bot> [Warning: JSON parsed but report rendering failed: {e}]")
                print("Raw JSON:", reply)

    # store assistant response for future context (raw reply)
    history.append({"role": "assistant", "content": reply})