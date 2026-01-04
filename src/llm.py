"""LiteLLM wrapper for Gemini API calls."""

import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from litellm import completion

load_dotenv()

DEFAULT_MODEL = "gemini/gemini-3-flash-preview"


@dataclass
class LLMResponse:
    content: str
    usage: dict
    model: str
    reasoning_effort: str | None = None


def call_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    json_mode: bool = True,
    reasoning_effort: str | None = None,
) -> LLMResponse:
    """Call LLM via LiteLLM.

    Args:
        prompt: The prompt text
        model: Model identifier (default: gemini/gemini-3-flash-preview)
        json_mode: If True, expect JSON response
        reasoning_effort: Thinking level - "minimal", "low", "medium", "high", or None for default

    Returns:
        LLMResponse with content and token usage
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")

    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "api_key": api_key,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    if reasoning_effort:
        kwargs["reasoning_effort"] = reasoning_effort

    response = completion(**kwargs)

    return LLMResponse(
        content=response.choices[0].message.content,
        usage={
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
        },
        model=model,
        reasoning_effort=reasoning_effort,
    )


call_gemini = call_llm


def parse_json_response(response: LLMResponse) -> dict:
    """Parse JSON from LLM response, handling common issues."""
    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content)
