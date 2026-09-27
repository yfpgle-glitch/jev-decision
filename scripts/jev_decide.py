#!/usr/bin/env python3
"""Call Tencent EdgeOne Makers Jev without exposing credentials."""

from __future__ import annotations

import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://ai-gateway.edgeone.link/v1/systemone"
ENV_KEY = "JEV_DECISION_API_KEY"
KEY_PATH = pathlib.Path.home() / ".config/jev-decision/api_key"
QUESTION_TYPES = {"noul", "choice", "score"}


def read_api_key() -> str:
    key = os.environ.get(ENV_KEY, "").strip()
    if key:
        return key
    try:
        key = KEY_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        key = ""
    except OSError as exc:
        raise ValueError(f"could not read key file: {exc}") from exc
    if not key:
        raise ValueError(f"{ENV_KEY} is not set and no key file exists at {KEY_PATH}")
    if "\n" in key or "\r" in key:
        raise ValueError("Jev API key must be a single line")
    return key


def validate_questions(questions: object) -> None:
    if not isinstance(questions, dict) or not questions:
        raise ValueError("questions must be a non-empty object")
    for name, question in questions.items():
        if not isinstance(name, str) or not isinstance(question, dict):
            raise ValueError("each question must be an object with a string id")
        if question.get("type") not in QUESTION_TYPES:
            raise ValueError(f"question {name!r} must use noul, choice, or score")
        if not question.get("instructions"):
            raise ValueError(f"question {name!r} is missing instructions")
        if question["type"] == "choice":
            criteria = question.get("criteria")
            if not isinstance(criteria, dict) or not criteria:
                raise ValueError(f"question {name!r} choice criteria must be a non-empty object")
        if question["type"] == "score":
            criteria = question.get("criteria")
            if not isinstance(criteria, list) or not criteria:
                raise ValueError(
                    f"question {name!r} score criteria must be a non-empty array of ordered levels"
                )


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {pathlib.Path(sys.argv[0]).name} REQUEST.json", file=sys.stderr)
        return 2
    try:
        key = read_api_key()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        request = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
        if not isinstance(request, dict) or not request.get("state"):
            raise ValueError("request must contain non-empty state")
        validate_questions(request.get("questions"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"invalid request file: {exc}", file=sys.stderr)
        return 2
    payload = {"model": "@makers/jev", "state": request["state"], "questions": request["questions"]}
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        print(f"Jev HTTP {exc.code}: {detail}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Jev request failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
