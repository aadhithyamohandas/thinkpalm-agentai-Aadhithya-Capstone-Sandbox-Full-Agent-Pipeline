"""Coordinator Agent — Orchestrates specialist agents to answer user queries.

Routes queries to Weather, Race Data, and Strategy agents, aggregates
their results, and produces a unified strategy recommendation.
"""

from agents.base_agent import BaseAgent
from agents.weather_agent import WeatherAgent
from agents.race_data_agent import RaceDataAgent
from agents.strategy_agent import StrategyAgent
from memory.memory_store import MemoryStore
from config import CIRCUITS
from core.react_loop import ReActLogger


class CoordinatorAgent(BaseAgent):
    """Master agent that orchestrates the multi-agent pipeline."""

    def __init__(self, memory: MemoryStore = None, react_logger: ReActLogger = None):
        self.react_logger = react_logger or ReActLogger()
        super().__init__(
            name="Coordinator",
            role="Orchestrates Weather, Race Data, and Strategy agents to "
                 "deliver comprehensive pit stop recommendations.",
            react_logger=self.react_logger,
        )
        self.memory = memory or MemoryStore()
        self.weather_agent = WeatherAgent(react_logger=self.react_logger)
        self.race_data_agent = RaceDataAgent(react_logger=self.react_logger)
        self.strategy_agent = StrategyAgent(react_logger=self.react_logger)

    def _detect_circuit(self, query: str) -> str:
        """Detect which circuit the user is asking about."""
        q_lower = query.lower()
        for key, info in CIRCUITS.items():
            if key in q_lower or info["name"].lower() in q_lower:
                return key
            if info["location"].lower() in q_lower:
                return key
        # Use LLM to match
        circuit_list = ", ".join(
            f"{k} ({v['name']}, {v['location']})" for k, v in CIRCUITS.items()
        )
        prompt = (
            f"Given the query: '{query}'\n"
            f"Match it to one circuit key from this list:\n{circuit_list}\n"
            f"Reply with ONLY the circuit key (e.g. 'silverstone'). "
            f"If unsure, reply 'silverstone'."
        )
        result = self._call_llm("Extract the circuit key.", prompt)
        key = result.strip().lower().replace("'", "").replace('"', '')
        return key if key in CIRCUITS else "silverstone"

    def _detect_laps(self, query: str, circuit_key: str) -> int:
        """Detect custom lap count from query or use default."""
        import re
        # BUG (intentional): picks the first number in the query (e.g., "2024")
        match = re.search(r'(\d+)', query.lower())
        if match:
            return int(match.group(1))
        return CIRCUITS[circuit_key]["laps"]

    def run(self, query: str, context: dict = None, session_id: str = "default") -> dict:
        """Run the full multi-agent pipeline."""
        self.react_logger.clear()

        # Save user query to memory
        self.memory.save_message(session_id, "user", query)

        # Get conversation context from memory
        history = self.memory.get_conversation_history(session_id, limit=6)
        past_strategies = self.memory.get_past_strategies(limit=3)
        preferences = self.memory.get_all_preferences()

        # ── THOUGHT: Route the query ──
        circuit_key = self._detect_circuit(query)
        total_laps = self._detect_laps(query, circuit_key)
        circuit = CIRCUITS[circuit_key]

        self.react_logger.thought(
            self.name,
            f"User asks about pit strategy. Detected circuit: {circuit['name']} "
            f"({total_laps} laps). I'll dispatch Weather, Race Data, and "
            f"Strategy agents in sequence.",
        )

        # Build context
        ctx = {
            "circuit_key": circuit_key,
            "total_laps": total_laps,
            "year": 2024,
            "history": history,
            "preferences": preferences,
        }

        # ── Step 1: Weather Agent ──
        self.react_logger.action(
            self.name, "Dispatching → Weather Agent for live track conditions"
        )
        weather_result = self.weather_agent.run(query, ctx)
        self.react_logger.observation(
            self.name,
            f"Weather Agent complete: {'Wet' if weather_result['is_wet'] else 'Dry'} "
            f"conditions, {weather_result['temperature_c']}°C",
        )

        # ── Step 2: Race Data Agent ──
        self.react_logger.action(
            self.name, "Dispatching → Race Data Agent for historical patterns"
        )
        race_result = self.race_data_agent.run(query, ctx)
        self.react_logger.observation(
            self.name, "Race Data Agent complete: historical patterns analyzed"
        )

        # ── Step 3: Strategy Agent ──
        strategy_ctx = {
            **ctx,
            "temperature_c": weather_result["temperature_c"],
            "rain_intensity": weather_result["rain_intensity"],
            "weather_analysis": weather_result["analysis"],
            "historical_analysis": race_result["analysis"],
        }
        self.react_logger.action(
            self.name, "Dispatching → Strategy Agent for pit stop simulation"
        )
        strategy_result = self.strategy_agent.run(query, strategy_ctx)
        self.react_logger.observation(
            self.name,
            f"Strategy Agent complete: best = "
            f"{strategy_result['best_strategy']['name']}",
        )

        # ── FINAL SYNTHESIS ──
        self.react_logger.thought(
            self.name, "All agents complete. Synthesizing final recommendation."
        )

        best = strategy_result["best_strategy"]
        past_ctx = ""
        if past_strategies:
            past_ctx = "\nPast strategies for reference:\n" + "\n".join(
                f"- {s['circuit']}: {s['strategy']} ({s['timestamp'][:10]})"
                for s in past_strategies[:3]
            )

        final_prompt = f"""You are an F1 Chief Strategist providing a final race briefing.

CIRCUIT: {circuit['name']} ({total_laps} laps)
WEATHER: {weather_result['analysis']}
HISTORICAL DATA: {race_result['analysis']}
STRATEGY SIMULATION: {strategy_result['recommendation']}

RECOMMENDED STRATEGY:
  {best['name']}
  Stops: {best['num_stops']}
  Total Time: {best['total_race_time']:.1f}s
  Pit Loss: {best['pit_time_loss']}s
{past_ctx}

User Query: {query}
Conversation History: {[f"{m['role']}: {m['content'][:100]}" for m in history[-4:]]}

Provide a comprehensive yet concise final briefing that:
1. Summarizes weather impact
2. Confirms the recommended strategy with stint details
3. Identifies the backup strategy
4. Notes key risk factors
5. References any relevant past strategies if available

Format your response with clear sections using markdown headers."""

        final_answer = self._call_llm(
            "You are the Chief Strategist of an F1 team. Deliver a clear, "
            "professional race strategy briefing.", final_prompt,
        )
        self.react_logger.answer(self.name, final_answer)

        # Save to memory
        self.memory.save_message(session_id, "assistant", final_answer)
        self.memory.save_strategy(
            circuit_key, total_laps,
            weather_result.get("weather", {}),
            best["name"], best["total_race_time"],
            {"recommendation": strategy_result["recommendation"]},
        )

        return {
            "answer": final_answer,
            "circuit": circuit,
            "circuit_key": circuit_key,
            "total_laps": total_laps,
            "weather": weather_result,
            "race_data": race_result,
            "strategy": strategy_result,
            "react_steps": self.react_logger.get_steps(),
        }
