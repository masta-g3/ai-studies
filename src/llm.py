"""LiteLLM wrapper for Gemini API calls."""

import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from litellm import completion

load_dotenv()

MODEL = "gemini/gemini-3-flash-preview"


@dataclass
class LLMResponse:
    content: str
    usage: dict


def call_gemini(prompt: str, json_mode: bool = True) -> LLMResponse:
    """Call Gemini via LiteLLM.

    Args:
        prompt: The prompt text
        json_mode: If True, expect JSON response

    Returns:
        LLMResponse with content and token usage
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
    response = completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"} if json_mode else None,
        api_key=api_key,
    )
    return LLMResponse(
        content=response.choices[0].message.content,
        usage={
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
        },
    )


def parse_json_response(response: LLMResponse) -> dict:
    """Parse JSON from LLM response, handling common issues."""
    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content)
