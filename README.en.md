<div align="center">

# jev-decision

**A structured judgment Skill for Codex, Claude Code, and Command Code**

![Agents](https://img.shields.io/badge/agents-Codex%20%7C%20Claude%20Code%20%7C%20Command%20Code-202124?style=flat-square)
![Language](https://img.shields.io/badge/language-English-2563EB?style=flat-square)
![Provider](https://img.shields.io/badge/provider-Tencent%20EdgeOne%20Makers-16A34A?style=flat-square)

[GitHub repository](https://github.com/yfpgle-glitch/jev-decision) · [简体中文](README.md)

</div>

`jev-decision` calls Tencent EdgeOne Makers Jev for probability signals on bounded, well-defined judgments. It fits classification, option comparison, and ordered scoring. It is not a writing tool, exact calculator, or replacement for business rules.

## Supported inputs

| Type | Input | Main result |
| :--- | :--- | :--- |
| `noul` | One neutral statement | Probability that the statement is true |
| `choice` | Several alternatives | Probability for each option and the winner |
| `score` | An ordered level array | Expected level index and per-level probabilities |

Each call contains one shared `state` and one or more questions. Keep only the smallest set of questions that can change the decision.

## 1. Install the Skill

Python 3 is required. Send this message to Codex, Claude Code, or Command Code:

```text
Please install the root of this repository as a Skill:
https://github.com/yfpgle-glitch/jev-decision
```

You can also clone the repository first:

```bash
git clone https://github.com/yfpgle-glitch/jev-decision.git
cd jev-decision
```

If the tool does not detect it after installation, reopen the task or session.

## 2. Create a Tencent Cloud API key

Tencent Cloud EdgeOne Makers currently offers a time-limited free allowance. Check Tencent Cloud for the current validity period and usage terms:

1. [Create a Tencent Cloud account](https://cloud.tencent.com/register).
2. Open the [EdgeOne Makers API key page](https://console.cloud.tencent.com/edgeone/makers?tab=models&subTab=apikey).
3. Create and copy an API key.

## 3. Configure the API key

Run this from the repository directory:

```bash
python3 scripts/configure_api_key.py
```

On macOS, the helper opens a hidden input dialog. On Windows and Linux, it hides input in the terminal. Paste the API key and confirm; the value is not displayed.

Check the configuration:

```bash
python3 scripts/configure_api_key.py --check
```

You can also use an environment variable.

macOS / Linux:

```bash
export JEV_DECISION_API_KEY="your-api-key"
```

Windows PowerShell:

```powershell
$env:JEV_DECISION_API_KEY = "your-api-key"
```

## Call Jev

Create `request.json`:

```json
{
  "state": "Goal: decide whether to handle an account-binding report now. Known: the user has been unable to bind for three days and the issue affects use; logs have not identified the cause.",
  "questions": {
    "next_action": {
      "type": "choice",
      "instructions": "What is the best next action?",
      "criteria": {
        "investigate_now": "Inspect logs and locate the cause",
        "request_more_info": "Collect reproduction details from the user",
        "defer": "Wait for more evidence"
      }
    }
  }
}
```

After the user selects Yes in the host confirmation UI, run:

```bash
python3 scripts/jev_decide.py request.json
```

`state` is a decision brief: objective, decision-changing constraints, verified evidence, and important unresolved facts. Do not include a full transcript, contact details, internal traces, or unrelated background.

## Interpret the result

Jev returns a structured signal. The host should:

- preserve the original probabilities and what each one refers to;
- compare the leader with the runner-up and mark close results as inconclusive;
- give one next step tied to the decision;
- identify evidence that could change the judgment.

A probability is a reference estimate, not a guarantee. It must not independently trigger irreversible actions or replace access checks, human review, or business policy.
