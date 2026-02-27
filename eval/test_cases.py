# eval/test_cases.py
# Runs the agent against predefined test cases and scores the results.
# Flags anything that scores below 60 as a "bad case" for investigation.

import json
import os
from datetime import datetime
from agent.core import AgentForge


TEST_CASES = [
    {
        "id": "search_01",
        "description": "simple factual search",
        "task": "What is the ReAct framework for AI agents? Explain it briefly.",
        "mode": "general",
        "expected_tools": ["web_search"],
        "expected_keywords": ["reason", "act", "observation", "tool", "loop"],
        "max_steps": 5,
    },
    {
        "id": "search_02",
        "description": "multi-source comparison",
        "task": "Compare Dify and Coze as low-code AI agent platforms. Pros and cons of each.",
        "mode": "research",
        "expected_tools": ["web_search"],
        "expected_keywords": ["dify", "coze", "low-code", "agent"],
        "max_steps": 8,
    },
    {
        "id": "code_01",
        "description": "code generation + execution",
        "task": "Write a Python function that checks if a string is a palindrome, then test it with 5 examples by running the code.",
        "mode": "general",
        "expected_tools": ["run_code"],
        "expected_keywords": ["palindrome", "true", "false"],
        "max_steps": 5,
    },
    {
        "id": "code_02",
        "description": "file creation + verification",
        "task": "Create a Python file called 'hello_agent.py' that prints 'AgentForge is working!' and then run it to verify.",
        "mode": "general",
        "expected_tools": ["write_file", "run_code"],
        "expected_keywords": ["agentforge", "working"],
        "max_steps": 5,
    },
    {
        "id": "research_01",
        "description": "broad research + synthesis",
        "task": "What are the top 3 AI agent frameworks in 2025? Compare their features briefly.",
        "mode": "research",
        "expected_tools": ["web_search"],
        "expected_keywords": ["langchain", "agent", "framework"],
        "max_steps": 8,
    },
]


def score_run(test_case: dict, result: dict) -> dict:
    """
    Scores an agent run on three things:
    - did it use the right tools? (30%)
    - did the answer contain the right info? (40%)
    - did it finish in a reasonable number of steps? (30%)
    """
    issues = []
    answer = result["result"].lower()
    steps_used = result["total_steps"]
    max_steps = test_case["max_steps"]

    # tool score
    tools_used = set()
    for step in result["steps"]:
        for action in step["actions"]:
            if action["type"] == "tool_use":
                tools_used.add(action["tool"])

    expected = set(test_case["expected_tools"])
    hits = len(expected.intersection(tools_used))
    tool_score = (hits / len(expected)) * 100 if expected else 100

    if hits < len(expected):
        missing = expected - tools_used
        issues.append(f"didn't use expected tools: {missing}")

    # keyword score
    keywords = test_case["expected_keywords"]
    found = sum(1 for kw in keywords if kw.lower() in answer)
    keyword_score = (found / len(keywords)) * 100 if keywords else 100

    if found < len(keywords):
        missing_kw = [kw for kw in keywords if kw.lower() not in answer]
        issues.append(f"answer missing: {missing_kw}")

    # efficiency
    if steps_used <= max_steps:
        efficiency_score = 100
    else:
        over = steps_used - max_steps
        efficiency_score = max(0, 100 - (over * 20))
        issues.append(f"took {steps_used} steps, expected max {max_steps}")

    overall = (tool_score * 0.3) + (keyword_score * 0.4) + (efficiency_score * 0.3)
    is_bad = overall < 60

    if is_bad:
        issues.append("BAD CASE - needs investigation")

    return {
        "test_id": test_case["id"],
        "description": test_case["description"],
        "tool_score": round(tool_score, 1),
        "keyword_score": round(keyword_score, 1),
        "efficiency_score": round(efficiency_score, 1),
        "overall_score": round(overall, 1),
        "is_bad_case": is_bad,
        "issues": issues,
        "steps_used": steps_used,
        "tools_used": list(tools_used),
    }


def run_eval(test_ids: list = None, verbose: bool = True) -> list:
    """Runs test cases and prints a report. Saves results to eval/results/."""
    cases = TEST_CASES
    if test_ids:
        cases = [tc for tc in TEST_CASES if tc["id"] in test_ids]

    results = []
    bad_cases = []

    print(f"\nRunning {len(cases)} test cases\n{'-'*40}")

    for i, tc in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] {tc['description']}")
        print(f"  task: {tc['task'][:80]}...")

        agent = AgentForge(mode=tc["mode"])
        try:
            result = agent.run(tc["task"], verbose=False)
        except Exception as e:
            result = {
                "result": f"ERROR: {str(e)}",
                "steps": [],
                "tool_calls": 0,
                "total_steps": 0,
            }

        score = score_run(tc, result)
        score["raw_result"] = result["result"][:500]
        results.append(score)

        status = "pass" if not score["is_bad_case"] else "FAIL"
        print(f"  [{status}] {score['overall_score']}/100 "
              f"(tools:{score['tool_score']} keywords:{score['keyword_score']} "
              f"efficiency:{score['efficiency_score']})")

        for issue in score["issues"]:
            print(f"  > {issue}")
        print()

        if score["is_bad_case"]:
            bad_cases.append(score)

    # save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"eval/results/eval_{timestamp}.json"
    os.makedirs("eval/results", exist_ok=True)

    with open(out_path, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "total": len(cases),
            "bad_cases": len(bad_cases),
            "avg_score": round(sum(r["overall_score"] for r in results) / len(results), 1),
            "results": results,
        }, f, indent=2)

    avg = sum(r["overall_score"] for r in results) / len(results)
    print(f"{'-'*40}")
    print(f"avg: {avg:.1f}/100 | bad cases: {len(bad_cases)}/{len(cases)}")
    print(f"saved: {out_path}\n")

    return results


if __name__ == "__main__":
    run_eval(test_ids=["search_01", "code_01"])
