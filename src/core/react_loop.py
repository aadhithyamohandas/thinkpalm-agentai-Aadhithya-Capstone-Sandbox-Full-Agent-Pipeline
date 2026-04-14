"""ReAct Loop Engine — Thought → Action → Observation → Answer logging.

Provides structured logging for the ReAct reasoning pattern used by
all agents in the F1 strategy pipeline.
"""

from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class ReActStep:
    """A single step in the ReAct reasoning loop."""
    step_type: str      # "thought", "action", "observation", "answer"
    agent: str          # name of the agent performing this step
    content: str        # description of what happened
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


STEP_ICONS = {
    "thought": "🤔",
    "action": "⚡",
    "observation": "👁️",
    "answer": "✅",
}


class ReActLogger:
    """Logger that records all ReAct steps across all agents."""

    def __init__(self):
        self.steps: List[ReActStep] = []

    def thought(self, agent: str, content: str) -> ReActStep:
        """Log a Thought step — agent reasoning about what to do."""
        step = ReActStep("thought", agent, content)
        self.steps.append(step)
        return step

    def action(self, agent: str, content: str) -> ReActStep:
        """Log an Action step — agent calling a tool."""
        step = ReActStep("action", agent, content)
        self.steps.append(step)
        return step

    def observation(self, agent: str, content: str) -> ReActStep:
        """Log an Observation step — processing tool results."""
        step = ReActStep("observation", agent, content)
        self.steps.append(step)
        return step

    def answer(self, agent: str, content: str) -> ReActStep:
        """Log an Answer step — agent's final output."""
        step = ReActStep("answer", agent, content)
        self.steps.append(step)
        return step

    def get_steps(self) -> List[dict]:
        """Get all steps as dicts."""
        return [s.to_dict() for s in self.steps]

    def get_steps_by_agent(self, agent: str) -> List[dict]:
        """Get steps filtered by a specific agent."""
        return [s.to_dict() for s in self.steps if s.agent == agent]

    def format_for_display(self) -> str:
        """Format all steps as a readable markdown string."""
        lines = []
        for step in self.steps:
            icon = STEP_ICONS.get(step.step_type, "📌")
            lines.append(
                f"{icon} **{step.step_type.upper()}** [{step.agent}]: {step.content}"
            )
        return "\n\n".join(lines)

    def clear(self):
        """Clear all logged steps."""
        self.steps.clear()
