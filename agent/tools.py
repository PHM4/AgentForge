# agent/tools.py
# Tool definitions and implementations for the agent.
# Each tool has a JSON schema (so the LLM knows what's available)
# and a Python function that actually does the work.

import os
import subprocess
import tempfile
from ddgs import DDGS


# These schemas get sent to Claude with every request.
# The descriptions are important - they're how the model decides
# which tool to pick for a given task. Took some iteration to get
# these working well (too vague = wrong tool, too specific = never used).

TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current information on any topic. "
            "Use this when you need facts, documentation, recent news, "
            "or any information you don't already know. "
            "Returns the top search results with titles, URLs, and snippets."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific for better results."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_file",
        "description": (
            "Read the contents of a file from the local filesystem. "
            "Use this to examine code files, config files, documentation, or any text file. "
            "Returns the full contents of the file."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read."
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write_file",
        "description": (
            "Write content to a file on the local filesystem. "
            "Use this to create reports, save analysis results, or generate code files. "
            "Will create the file if it doesn't exist, or overwrite if it does."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path where the file should be written."
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file."
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "run_code",
        "description": (
            "Execute a Python code snippet and return the output. "
            "Use this to test code, run calculations, validate data, "
            "or perform any computation. The code runs in an isolated environment. "
            "Returns stdout output and any errors."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute."
                }
            },
            "required": ["code"]
        }
    }
]


# -- implementations --

def web_search(query: str) -> str:
    """Searches DuckDuckGo, returns top 5 results. No API key needed."""
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=5))

        if not results:
            return "No results found."

        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                f"[{i}] {r['title']}\n"
                f"    URL: {r['href']}\n"
                f"    {r['body']}\n"
            )
        return "\n".join(formatted)

    except Exception as e:
        return f"Search error: {str(e)}"


def read_file(file_path: str) -> str:
    """Reads a local file. Caps at 1MB to avoid blowing up context."""
    try:
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            return f"Error: File not found: {abs_path}"

        if os.path.getsize(abs_path) > 1_000_000:
            return "Error: File too large (>1MB)."

        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        return f"Contents of {abs_path}:\n\n{content}"

    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """Writes content to a file. Creates parent dirs if they don't exist."""
    try:
        abs_path = os.path.abspath(file_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Wrote {len(content)} chars to {abs_path}"

    except Exception as e:
        return f"Error writing file: {str(e)}"


def run_code(code: str) -> str:
    """Runs Python in a subprocess with a 30s timeout."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        result = subprocess.run(
            ["python3", tmp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        os.unlink(tmp_path)

        output = ""
        if result.stdout:
            output += f"Output:\n{result.stdout}"
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"

        return output if output.strip() else "Code ran successfully (no output)."

    except subprocess.TimeoutExpired:
        os.unlink(tmp_path)
        return "Error: Timed out after 30s."
    except Exception as e:
        return f"Error: {str(e)}"


# maps tool name -> function call
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Routes a tool call from the LLM to the right function."""
    router = {
        "web_search": lambda args: web_search(args["query"]),
        "read_file": lambda args: read_file(args["file_path"]),
        "write_file": lambda args: write_file(args["file_path"], args["content"]),
        "run_code": lambda args: run_code(args["code"]),
    }

    if tool_name not in router:
        return f"Unknown tool: {tool_name}"

    return router[tool_name](tool_input)
