import json
import os
from typing import Any

import gradio as gr
import requests


API_URL = os.getenv("AGENTOS_API_URL", "http://127.0.0.1:8000")
UI_HOST = os.getenv("AGENTOS_UI_HOST", "0.0.0.0")
UI_PORT = int(os.getenv("AGENTOS_UI_PORT", "7860"))

AGENT_DESCRIPTIONS = {
    "knowledge-agent": "Answers from the loaded Agno docs knowledge base.",
    "mcp-agent": "Uses MCP tools to search Agno docs dynamically.",
}

EXAMPLE_PROMPTS = {
    "knowledge-agent": [
        "What is Agno?",
        "How do I create my first agent?",
        "What documents are in your knowledge base?",
    ],
    "mcp-agent": [
        "What tools do you have access to?",
        "Find examples of agents with memory.",
        "Search the docs for how to use LearningMachine.",
    ],
}


def _post_agent_run(agent_id: str, message: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_URL}/agents/{agent_id}/runs",
        files={
            "message": (None, message),
            "stream": (None, "false"),
        },
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def _format_references(payload: dict[str, Any]) -> str:
    references = payload.get("references") or []
    if not references:
        return "No references returned."

    lines: list[str] = []
    for item in references:
        for ref in item.get("references", []):
            name = ref.get("name", "Untitled")
            source_url = ref.get("meta_data", {}).get("_agno", {}).get("source_url", "")
            if source_url:
                lines.append(f"- [{name}]({source_url})")
            else:
                lines.append(f"- {name}")
    return "\n".join(lines) if lines else "No references returned."


def run_agent(agent_id: str, message: str) -> tuple[str, str, str]:
    if not message.strip():
        return "Please enter a question.", "", ""

    try:
        payload = _post_agent_run(agent_id=agent_id, message=message.strip())
    except requests.RequestException as exc:
        return f"Request failed: {exc}", "", ""

    status = payload.get("status", "UNKNOWN")
    answer = payload.get("content", "")
    if not isinstance(answer, str):
        answer = json.dumps(answer, indent=2, ensure_ascii=False)

    summary = f"Status: {status}\nModel: {payload.get('model', 'unknown')}"
    references = _format_references(payload)
    return answer, summary, references


def update_examples(agent_id: str) -> tuple[str, gr.update]:
    description = AGENT_DESCRIPTIONS[agent_id]
    return description, gr.update(
        choices=EXAMPLE_PROMPTS[agent_id],
        value=EXAMPLE_PROMPTS[agent_id][0],
    )


def apply_example(example_text: str) -> str:
    return example_text


with gr.Blocks(title="AgentOS Demo") as demo:
    gr.Markdown(
        """
        # AgentOS Demo
        Ask a question, choose an agent, and inspect the answer plus its sources.
        """
    )

    with gr.Row():
        agent_id = gr.Dropdown(
            choices=list(AGENT_DESCRIPTIONS.keys()),
            value="knowledge-agent",
            label="Agent",
        )
        agent_description = gr.Textbox(
            value=AGENT_DESCRIPTIONS["knowledge-agent"],
            label="What This Agent Does",
            interactive=False,
        )

    message = gr.Textbox(
        label="Question",
        placeholder="Ask something about Agno...",
        lines=3,
    )

    example_buttons = gr.Radio(
        choices=EXAMPLE_PROMPTS["knowledge-agent"],
        value=EXAMPLE_PROMPTS["knowledge-agent"][0],
        label="Example Questions",
    )

    submit = gr.Button("Run", variant="primary")

    answer = gr.Markdown(label="Answer")
    summary = gr.Textbox(label="Run Summary", interactive=False)
    references = gr.Markdown(label="References")

    submit.click(
        fn=run_agent,
        inputs=[agent_id, message],
        outputs=[answer, summary, references],
    )
    message.submit(
        fn=run_agent,
        inputs=[agent_id, message],
        outputs=[answer, summary, references],
    )
    agent_id.change(
        fn=update_examples,
        inputs=[agent_id],
        outputs=[agent_description, example_buttons],
    )
    example_buttons.change(
        fn=apply_example,
        inputs=[example_buttons],
        outputs=[message],
    )


if __name__ == "__main__":
    demo.launch(
        server_name=UI_HOST,
        server_port=UI_PORT,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="stone",
        ),
    )
