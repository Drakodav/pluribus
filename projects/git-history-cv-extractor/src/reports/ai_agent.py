import argparse
import asyncio
from pathlib import Path

from google.antigravity import Agent, LocalAgentConfig


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run AI analysis on contribution reports."
    )
    parser.add_argument("--prompt", required=True, help="Prompt query for AI")
    parser.add_argument(
        "--reports-dir", required=True, help="Directory containing reports"
    )
    parser.add_argument("--output", required=True, help="Target markdown file path")
    args = parser.parse_args()

    reports_path = Path(args.reports_dir)
    output_path = Path(args.output)

    # 1. Read generated report markdown files as context (skipping ai/ subdir)
    reports_content = []
    for file in sorted(reports_path.glob("*.md")):
        if file.parent.name == "ai":
            continue
        reports_content.append(
            f"=== File: {file.name} ===\n{file.read_text(encoding='utf-8')}\n"
        )

    if not reports_content:
        raise ValueError(
            f"No report markdown files found in: {reports_path.as_posix()}"
        )

    context = "\n".join(reports_content)
    full_prompt = (
        f"You are an AI assistant analyzing a developer's software "
        f"engineering contributions.\n"
        f"Here is the context of their generated Git contribution reports:\n\n"
        f"{context}\n\n"
        f"Instruction: {args.prompt}\n"
    )

    # 2. Instantiate AGY Agent and run chat turn
    async with Agent(LocalAgentConfig()) as agent:
        response = await agent.chat(full_prompt)
        result_text = await response.text()

    # 3. Write results to output path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result_text, encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
