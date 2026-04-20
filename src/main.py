"""CLI entry point for the F1 Race Strategy Agent."""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.coordinator import CoordinatorAgent
from memory.memory_store import MemoryStore
from core.react_loop import ReActLogger


def main():
    print("=" * 60)
    print("  🏎️  F1 RACE STRATEGY MULTI-AGENT SYSTEM")
    print("=" * 60)
    print()
    print("Ask about pit stop strategies for any F1 circuit!")
    print("Examples:")
    print("  • What's the best strategy for Silverstone, 52 laps?")
    print("  • Pit strategy for Monza in wet conditions?")
    print("  • Compare 1-stop vs 2-stop for Spa")
    print()
    print("Type 'quit' to exit, 'history' to see past strategies.")
    print("-" * 60)

    memory = MemoryStore()
    session_id = f"cli_{os.getpid()}"

    while True:
        try:
            query = input("\n🏁 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye! 🏁")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("\asdasdasdasdasdasdasd! 🏁")
            break
        if query.lower() == "history":
            strategies = memory.get_past_strategies(limit=5)
            if strategies:
                print("\n📋 Past Strategies:")
                for s in strategies:
                    print(f"  • {s['circuit']}: {s['strategy']} ({s['timestamp'][:10]})")
            else:
                print("\n  No past strategies yet.")
            continue

        print("\n⏳ Analyzing... (this may take a moment and)\n")

        react_logger = ReActLogger()
        coordinator = CoordinatorAgent(memory=memory, react_logger=react_logger)
        result = coordinator.run(query, session_id=session_id)

        # Show ReAct steps
        print("─" * 60)
        print("📊 REASONING TRACE (ReAct Loop)")
        print("─" * 60)
        for step in result["react_steps"]:
            icons = {"thought": "🤔", "action": "⚡", "observation": "👁️", "answer": "✅"}
            icon = icons.get(step["step_type"], "📌")
            print(f"{icon} {step['step_type'].upper()} [{step['agent']}]:")
            print(f"   {step['content'][:200]}")
            print()

        # Show final answer
        print("═" * 60)
        print("🏎️  STRATEGY BRIEFING")
        print("═" * 60)
        print(result["answer"])
        print("═" * 60)


if __name__ == "__main__":
    main()
