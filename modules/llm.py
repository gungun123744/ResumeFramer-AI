
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

DEFAULT_MODEL = "qwen/qwen3.8-27b"


def get_llm(
    model=DEFAULT_MODEL,
    temperature=0.1,
    max_tokens=600,
):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY missing hai. Project ki .env file check karo."
        )

    return ChatGroq(
        model=model.strip(),
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        max_retries=2,
        timeout=120,
    )


def invoke_text(
    system_prompt,
    user_prompt,
    model=DEFAULT_MODEL,
    temperature=0.1,
    max_tokens=600,
):
    if not system_prompt or not user_prompt:
        raise ValueError("System prompt aur user prompt required hain.")

    llm = get_llm(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    content = response.content

    if isinstance(content, str):
        result = content.strip()
    elif isinstance(content, list):
        result = "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
        ).strip()
    else:
        result = ""

    if not result:
        usage = getattr(response, "usage_metadata", None)
        raise ValueError(
            "Groq ne empty response diya. "
            f"Usage details: {usage}. Dobara try karo."
        )

    return result
