# agent/core.py
# The main agent loop. Implements ReAct (think -> use tool -> observe -> repeat).
#
# How it works:
# 1. Send task + tools to Claude
# 2. Claude either responds with text (thinking/answer) or asks to use a tool
# 3. If tool requested: run it, send result back, let Claude continue
# 4. If no tool requested: we're done, return the answer
# 5. Safety cap at 10 iterations so it can't loop forever

import os
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

from agent.tools import TOOL_DEFINITIONS, execute_tool
from agent.prompts import SYSTEM_PROMPT, CODE_REVIEW_PROMPT, RESEARCH_PROMPT

load_dotenv()

PROMPTS = {
    "general": SYSTEM_PROMPT,
    "code_review": CODE_REVIEW_PROMPT,
    "research": RESEARCH_PROMPT,
}


class AgentForge:

    def __init__(self, mode: str = "general"):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        self.max_steps = 10
        self.system_prompt = PROMPTS.get(mode, SYSTEM_PROMPT)
        self.messages = []
        self.steps = []
        self.total_steps = 0

    def run(self, task: str, verbose: bool = True) -> dict:
        """
        Main entry point. Give it a task, it thinks and uses tools
        until it has an answer (or hits the step limit).
        """
        self.messages = [{"role": "user", "content": task}]
        self.steps = []
        self.total_steps = 0
        tool_call_count = 0

        if verbose:
            print(f"\n{'='*60}")
            print(f"AgentForge - processing")
            print(f"{'='*60}")
            print(f"Task: {task}\n")

        while self.total_steps < self.max_steps:
            self.total_steps += 1

            if verbose:
                print(f"-- step {self.total_steps} --")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                tools=TOOL_DEFINITIONS,
                messages=self.messages,
            )

            stop_reason = response.stop_reason
            assistant_content = response.content

            # add the full response to conversation history
            self.messages.append({"role": "assistant", "content": assistant_content})

            step_info = {
                "step": self.total_steps,
                "timestamp": datetime.now().isoformat(),
                "actions": [],
            }

            # process response blocks - could be text, tool calls, or both
            tool_results = []
            for block in assistant_content:
                if block.type == "text":
                    if verbose:
                        preview = block.text[:200] + ("..." if len(block.text) > 200 else "")
                        print(f"  thought: {preview}")
                    step_info["actions"].append({
                        "type": "thought",
                        "content": block.text,
                    })

                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_call_count += 1

                    if verbose:
                        print(f"  tool: {tool_name}")
                        print(f"  input: {json.dumps(tool_input, indent=2)[:200]}")

                    # actually run the tool
                    result = execute_tool(tool_name, tool_input)

                    if verbose:
                        preview = result[:200] + ("..." if len(result) > 200 else "")
                        print(f"  result: {preview}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

                    step_info["actions"].append({
                        "type": "tool_use",
                        "tool": tool_name,
                        "input": tool_input,
                        "result": result,
                    })

            self.steps.append(step_info)

            # if tools were used, feed results back and keep going
            if tool_results:
                self.messages.append({"role": "user", "content": tool_results})

            # if Claude stopped on its own (not waiting for tool results), we're done
            if stop_reason == "end_turn":
                final_answer = ""
                for block in assistant_content:
                    if block.type == "text":
                        final_answer += block.text

                if verbose:
                    print(f"\n{'='*60}")
                    print(f"Done - {self.total_steps} steps, {tool_call_count} tool calls")
                    print(f"{'='*60}\n")

                return {
                    "result": final_answer,
                    "steps": self.steps,
                    "tool_calls": tool_call_count,
                    "total_steps": self.total_steps,
                }

        # hit the step limit
        return {
            "result": "Hit the step limit. Here's what I have so far:\n" + self._last_thought(),
            "steps": self.steps,
            "tool_calls": tool_call_count,
            "total_steps": self.total_steps,
        }

    def _last_thought(self) -> str:
        """Grabs the most recent text the agent produced."""
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                content = msg["content"]
                if isinstance(content, list):
                    for block in content:
                        if hasattr(block, "text"):
                            return block.text
                elif isinstance(content, str):
                    return content
        return "No output."


if __name__ == "__main__":
    agent = AgentForge(mode="general")
    result = agent.run("What is the current weather in London and what should I wear?")
    print("\nAnswer:")
    print(result["result"])
