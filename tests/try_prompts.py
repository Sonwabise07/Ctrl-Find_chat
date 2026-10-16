"""Sends every prompt in prompts.json to a running assistant and prints what happened.

Usage: python tests/try_prompts.py [--url http://localhost:8000] [--group counts]
Exit code is 1 when a reply does not match the expected scope and question type.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROMPTS = Path(__file__).with_name("prompts.json")


def ask(base_url: str, question: str, context: dict | None = None, email: str | None = None) -> dict:
    body = json.dumps({"question": question, "context": context, "as": email}).encode()
    request = urllib.request.Request(
        f"{base_url}/api/assistant/ask", body, {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def run_prompt(base_url: str, prompt: dict) -> dict:
    context = None
    if "after" in prompt:
        first = ask(base_url, prompt["after"], email=prompt.get("as"))
        context = {"intent": first["intent"], "slots": first["slots"]}
    return ask(base_url, prompt["q"], context, prompt.get("as"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--group", help="only groups whose name contains this text")
    args = parser.parse_args()

    try:
        urllib.request.urlopen(args.url, timeout=5)
    except urllib.error.URLError:
        print(f"Cannot reach the assistant at {args.url}. Start it first with: python -m assistant")
        return 2

    mismatches = 0
    for group in json.loads(PROMPTS.read_text()):
        if args.group and args.group.lower() not in group["group"].lower():
            continue
        print(f"\n== {group['group']}")
        for prompt in group["prompts"]:
            reply = run_prompt(args.url, prompt)
            matched = reply["scope"] == prompt["scope"] and reply["intent"] == prompt["intent"]
            mismatches += not matched
            who = f" [as {prompt['as'].split('@')[0]}]" if "as" in prompt else ""
            print(f"{'ok  ' if matched else 'FAIL'} {prompt['q']}{who}")
            print(f"     {reply['scope']} / {reply['intent']} / {reply['classifier']}")
            print(f"     {reply['answer'].replace('**', '')}")
            if reply.get("table"):
                print(f"     table: {len(reply['table']['rows'])} rows")
            if reply.get("chart"):
                print(f"     chart: {len(reply['chart']['rows'])} bars")
    print(f"\n{mismatches} mismatches")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
