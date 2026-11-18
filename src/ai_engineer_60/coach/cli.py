"""CLI entry point.

coach today                 today's assignment (no API call)
coach status                progress stats (no API call)
coach plan [--day N]        any day's plan (no API call)
coach checkin               chat with the Coach agent (daily log + accountability)
coach quiz                  8-question strict quiz
coach interview             45-minute mock interview round
"""

from __future__ import annotations

import argparse
import json
import sys

from .agents import Agent, build_tools, current_day_number
from .store import Store

OPENERS = {
    "coach": "Start my daily check-in.",
    "quiz": "Start the quiz.",
    "interview": "I'm ready for my mock interview.",
}


def chat(persona: str, store: Store) -> None:
    agent = Agent(persona, store)
    print(f"[{persona}] type 'exit' to quit\n")
    print(agent.send(OPENERS[persona]), "\n")
    while True:
        try:
            msg = input("you> ").strip()
        except EOFError, KeyboardInterrupt:
            break
        if msg.lower() in {"exit", "quit"}:
            break
        if msg:
            print("\n" + agent.send(msg) + "\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="coach")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("today")
    sub.add_parser("status")
    pp = sub.add_parser("plan")
    pp.add_argument("--day", type=int)
    for name in ("checkin", "quiz", "interview"):
        sub.add_parser(name)
    args = p.parse_args(argv)

    store = Store()
    tools = build_tools(store)
    if args.cmd == "today":
        print(json.dumps(tools["get_plan"].fn(), indent=2))
    elif args.cmd == "plan":
        print(json.dumps(tools["get_plan"].fn(args.day), indent=2))
    elif args.cmd == "status":
        print(f"Day {current_day_number()} of 60")
        print(json.dumps(tools["get_progress"].fn(), indent=2, default=str))
    else:
        chat({"checkin": "coach", "quiz": "quiz", "interview": "interview"}[args.cmd], store)
    return 0


if __name__ == "__main__":
    sys.exit(main())
