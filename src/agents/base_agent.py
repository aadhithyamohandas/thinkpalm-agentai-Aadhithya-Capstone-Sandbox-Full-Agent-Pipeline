"""Base Agent — Abstract base class for all F1 strategy agents."""

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
from core.react_loop import ReActLogger


class BaseAgent:
    """Base class providing LLM access and ReAct logging for all agents."""

    def __init__(self, name: str, role: str, react_logger: ReActLogger = None):
        self.name = name
        self.role = role
        self.react_logger = react_logger or ReActLogger()
        self.client = Groq(api_key=GROQ_API_KEY)

    def _call_llm(self, system_prompt: str, user_message: str,
                  temperature: float = 0.3) -> str:
        """Call Groq LLM with error handling."""
        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM Error: {str(e)}"

    def run(self, query: str, context: dict = None) -> dict:
        """Execute the agent's task. Must be implemented by subclasses."""
        raise NotImplementedError
