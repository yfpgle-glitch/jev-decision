---
name: jev-decision
description: Use Tencent EdgeOne Makers Jev for bounded, typed judgments such as classification, scoring, and yes/no validation. Use when software needs a structured signal; do not use it for writing, arithmetic, open-ended reasoning, or final business policy decisions.
---

# Jev Decision

Use `scripts/jev_decide.py` to call Tencent EdgeOne Makers:

```text
POST https://ai-gateway.edgeone.link/v1/systemone
model: @makers/jev
```

The helper reads `JEV_DECISION_API_KEY` first, then `~/.config/jev-decision/api_key`. Tencent Cloud EdgeOne Makers is currently time-limited free; use the [Tencent Cloud registration page](https://cloud.tencent.com/register) and the [EdgeOne Makers API key page](https://console.cloud.tencent.com/edgeone/makers?tab=models&subTab=apikey). Check the current validity period and usage terms there. If neither key source is configured, stop and ask the user to run `python3 scripts/configure_api_key.py`.

## Request format

Send one shared `state` and the smallest sufficient set of questions. Supported types:

- `noul`: a neutral statement; the result is the probability that the statement as written is true;
- `choice`: a `criteria` object mapping option IDs to descriptions;
- `score`: a `criteria` array of ordered level labels; the result index is `0..N-1`.

Example:

```json
{
  "state": "目标：决定是否立即处理一条账号绑定反馈。已知：用户连续三天无法绑定，问题已影响使用；尚无日志确认根因。",
  "questions": {
    "next_action": {
      "type": "choice",
      "instructions": "下一步最合适的处理方式是什么？",
      "criteria": {
        "investigate_now": "先检查日志并尽快定位",
        "request_more_info": "先向用户补充收集复现信息",
        "defer": "暂缓处理，等待更多证据"
      }
    }
  }
}
```

Run it after confirmation:

```bash
python3 scripts/jev_decide.py request.json
```

## Confirmation

For interactive calls, draft the question set and show it in the host's native confirmation UI. Offer only **Yes** and **No**; use the free-text field for edits. Send the compressed `state` only after Yes. On No, stop without calling Jev. See [`references/confirmation-protocol.md`](references/confirmation-protocol.md).

Do not ask Jev to write, calculate exact values, invent a plan, or make the final policy decision. Jev's probability is evidence for routing, not permission to bypass deterministic rules, access checks, human review, or business policy.

## Question design

Keep each question atomic and neutral. For comparable questions, use the same direction. Add a question only when its answer can change the action and cannot be represented in an existing question.

The `state` is a decision brief, not a transcript. Keep the objective, decision-changing constraints, verified evidence, and material unresolved facts. Omit contact details, internal tool traces, repeated background, and unsupported assumptions.

## Interpret the response

The API response is not user-facing. Preserve the original values, map IDs or indexes back to their labels, and explain what each probability refers to. Compare the leader with the runner-up; if they are close, report the result as inconclusive. Give one practical next step and name the evidence that could change the judgment. Never turn the signal into a guarantee or replace it with a summary alone.
