<div align="center">

# jev-decision

**面向 Codex、Claude Code 和 Command Code 的结构化判断 Skill**

![Agents](https://img.shields.io/badge/agents-Codex%20%7C%20Claude%20Code%20%7C%20Command%20Code-202124?style=flat-square)
![Language](https://img.shields.io/badge/language-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-2563EB?style=flat-square)
![Provider](https://img.shields.io/badge/provider-Tencent%20EdgeOne%20Makers-16A34A?style=flat-square)

[GitHub 仓库](https://github.com/yfpgle-glitch/jev-decision) · [English](README.en.md)

</div>

`jev-decision` 调用腾讯 EdgeOne Makers Jev，为有限、可描述的判断提供概率信号。它适合分类、选项比较和等级评分；不用于写作、精确计算或替代业务规则。

## 适用范围

| 类型 | 输入 | 返回重点 |
| :--- | :--- | :--- |
| `noul` | 一个中性陈述 | 陈述为真的概率 |
| `choice` | 多个候选项 | 各候选项概率与胜出项 |
| `score` | 有序等级数组 | 等级索引与各等级概率 |

一次调用使用一个共享 `state`，并携带一个或多个问题。默认只保留能改变选择的最小问题集。

## 一、安装 Skill

需要 Python 3。把这句话发给 Codex、Claude Code 或 Command Code：

```text
请把这个仓库根目录作为 Skill 安装：
https://github.com/yfpgle-glitch/jev-decision
```

也可以先下载仓库：

```bash
git clone https://github.com/yfpgle-glitch/jev-decision.git
cd jev-decision
```

安装后，如果工具没有识别，重新打开一个任务或会话。

## 二、注册腾讯云并创建 API key

腾讯云 EdgeOne Makers 当前提供限时免费额度，具体有效期和使用规则以腾讯云页面为准：

1. [注册腾讯云账号](https://cloud.tencent.com/register)。
2. 打开 [EdgeOne Makers API key 页面](https://console.cloud.tencent.com/edgeone/makers?tab=models&subTab=apikey)。
3. 创建并复制 API key。

## 三、配置 API key

在仓库目录运行：

```bash
python3 scripts/configure_api_key.py
```

macOS 会打开隐藏输入框；Windows 和 Linux 会在终端中隐藏输入。粘贴 API key 后确认，输入内容不会显示。

检查是否配置成功：

```bash
python3 scripts/configure_api_key.py --check
```

也可以通过环境变量配置。

macOS / Linux：

```bash
export JEV_DECISION_API_KEY="你的 API key"
```

Windows PowerShell：

```powershell
$env:JEV_DECISION_API_KEY = "你的 API key"
```

## 调用

创建 `request.json`：

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

用户在宿主的确认界面选择 Yes 后运行：

```bash
python3 scripts/jev_decide.py request.json
```

`state` 只写决策摘要：目标、会改变选择的约束、已核实证据和重要未决事实。不要放入完整对话、联系方式、内部日志或无关背景。

## 解释结果

Jev 返回的是结构化信号。宿主应：

- 保留原始概率，并说明每个概率对应的选项或陈述；
- 比较最高项与次高项，差距很小时标记为不确定；
- 给出一条与当前决策直接相关的下一步；
- 说明哪些证据可能改变判断。

概率是参考估计，不是保证。它不能单独触发不可逆操作，也不能替代权限检查、人工复核或业务政策。
