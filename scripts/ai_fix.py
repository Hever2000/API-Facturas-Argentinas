import os
import sys
import subprocess
import re
from pathlib import Path

ERRORS_FILE = Path("errors.txt")
PATCH_FILE = Path("ai_fix.patch")


def read_errors() -> str:
    """Read errors from file."""
    if not ERRORS_FILE.exists():
        print("No errors.txt found, running ruff check...")
        result = subprocess.run(
            ["python", "-m", "ruff", "check", "."],
            capture_output=True,
            text=True,
        )
        return result.stdout + result.stderr
    return ERRORS_FILE.read_text()


def call_openai(prompt: str) -> str:
    """Call OpenAI API to fix errors."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a senior Python engineer. Fix Ruff linting errors. Return ONLY the fixed files as a unified diff (patch format) or list of file changes. Do NOT explain, just fix.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def call_openrouter(prompt: str) -> str:
    """Call OpenRouter API (free tier available)."""
    import requests

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "google/gemini-2.0-flash-001",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a senior Python engineer. Fix Ruff linting errors. Return ONLY the fixed files as a unified diff (patch format) or list of file changes with the exact content to write. Do NOT explain, just fix.",
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def call_ollama(prompt: str) -> str:
    """Call local Ollama instance."""
    import requests

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "codellama",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a senior Python engineer. Fix Ruff linting errors. Return ONLY the fixed files as a unified diff (patch format) or list of file changes. Do NOT explain, just fix.",
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def apply_patch(patch: str) -> None:
    """Apply patch or direct file writes from AI response."""
    if not patch.strip():
        print("No patch generated")
        return

    if patch.startswith("diff") or "---" in patch:
        PATCH_FILE.write_text(patch)
        result = subprocess.run(["git", "apply", "patch"], capture_output=True)
        if result.returncode != 0:
            print(f"Patch failed: {result.stderr}")
        else:
            print("Patch applied successfully")
    else:
        apply_direct_fixes(patch)


def apply_direct_fixes(response: str) -> None:
    """Parse and apply direct file fixes from AI response."""
    lines = response.strip().split("\n")
    current_file = None
    current_content = []

    for line in lines:
        if line.startswith("FILE:"):
            if current_file and current_content:
                write_file(current_file, "\n".join(current_content))
            current_file = line.replace("FILE:", "").strip()
            current_content = []
        elif current_file:
            current_content.append(line)

    if current_file and current_content:
        write_file(current_file, "\n".join(current_content))


def write_file(filepath: str, content: str) -> None:
    """Write content to file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"Fixed: {filepath}")


def run_ruff_check() -> bool:
    """Run ruff check to verify fixes."""
    result = subprocess.run(
        ["python", "-m", "ruff", "check", "."],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main():
    errors = read_errors()

    if not errors.strip():
        print("No errors found!")
        return

    prompt = f"""You are a senior Python engineer.

Fix the following CI/Ruff errors:

```
{errors}
```

Project context:
- FastAPI backend (FacturaAI)
- Use Ruff for linting
- Fix F841 (unused variables), F401 (unused imports), E/W style issues
- DO NOT break functionality
- DO NOT change API contracts
- Improve error handling (use structured responses)
- Use meaningful variable names
- Remove dead code

Return the fixes as:
1. A unified diff (patch), OR
2. Each file with FILE: path/to/file.py and the full fixed content

Do NOT explain - just return the fixes."""

    print("Calling AI to fix errors...")

    try:
        if os.getenv("OPENAI_API_KEY"):
            response = call_openai(prompt)
        elif os.getenv("OPENROUTER_API_KEY"):
            response = call_openrouter(prompt)
        elif os.getenv("OLLAMA_URL"):
            response = call_ollama(prompt)
        else:
            print("No AI API key configured. Set OPENAI_API_KEY, OPENROUTER_API_KEY, or use Ollama.")
            sys.exit(1)

        print("Applying fixes...")
        apply_patch(response)

        if run_ruff_check():
            print("✅ All errors fixed!")
        else:
            print("⚠️ Some errors may remain, please review")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()