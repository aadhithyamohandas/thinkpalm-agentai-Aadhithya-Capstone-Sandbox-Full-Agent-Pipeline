"""Race Data Agent — Fetches and analyzes historical F1 race data."""

from agents.base_agent import BaseAgent
from tools.f1_data_tool import get_race_results, get_pit_stops
from core.react_loop import ReActLogger


class RaceDataAgent(BaseAgent):
    """Fetches historical race results and pit stop patterns for strategy insights."""

    def __init__(self, react_logger: ReActLogger = None):
        super().__init__(
            name="Race Data Agent",
            role="Fetches historical F1 race data and pit stop patterns "
                 "to identify optimal strategy windows.",
            react_logger=react_logger,
        )

    def run(self, query: str, context: dict = None) -> dict:
        ctx = context or {}
        circuit_key = ctx.get("circuit_key", "silverstone")
        year = ctx.get("year", 2024)

        # ── THOUGHT ──
        self.react_logger.thought(
            self.name,
            f"I need historical race data and pit stop patterns for "
            f"{circuit_key} ({year}) to inform our strategy recommendation.",
        )

        # ── ACTION 1: Race Results ──
        self.react_logger.action(
            self.name,
            f"Calling Jolpica F1 API — fetching {year} race results for {circuit_key}",
        )
        results = get_race_results(circuit_key, year)

        if results.get("status") != "error":
            top3 = results.get("results", [])[:3]
            top3_str = ", ".join(
                f"P{r['position']}: {r['driver']} ({r['constructor']})" for r in top3
            )
            self.react_logger.observation(
                self.name,
                f"Race: {results.get('race_name', 'N/A')} | Top 3: {top3_str}",
            )
        else:
            self.react_logger.observation(
                self.name, "Race results unavailable, using fallback data."
            )

        # ── ACTION 2: Pit Stop Data ──
        self.react_logger.action(
            self.name,
            f"Calling Jolpica F1 API — fetching {year} pit stop data for {circuit_key}",
        )
        pit_data = get_pit_stops(circuit_key, year)

        pit_obs = (
            f"Avg stops/driver: {pit_data.get('avg_stops_per_driver', 'N/A')} | "
            f"First pit window: ~Lap {pit_data.get('first_pit_window_avg_lap', 'N/A')} | "
            f"Second pit window: ~Lap {pit_data.get('second_pit_window_avg_lap', 'N/A')} | "
            f"Earliest stop: Lap {pit_data.get('earliest_stop_lap', 'N/A')}"
        )
        self.react_logger.observation(self.name, pit_obs)

        # ── LLM ANALYSIS ──
        self.react_logger.thought(
            self.name,
            "Synthesizing historical data to identify strategy patterns for this circuit.",
        )

        prompt = f"""You are an F1 race data analyst. Based on this historical data, provide strategic insights:

Circuit: {circuit_key.replace('_', ' ').title()}
Year: {year}
Race: {results.get('race_name', 'N/A')}
Top Finishers: {top3_str if results.get('status') != 'error' else 'N/A'}
Average pit stops per driver: {pit_data.get('avg_stops_per_driver', 'N/A')}
First pit window (avg lap): {pit_data.get('first_pit_window_avg_lap', 'N/A')}
Second pit window (avg lap): {pit_data.get('second_pit_window_avg_lap', 'N/A')}
Earliest stop: Lap {pit_data.get('earliest_stop_lap', 'N/A')}
Latest stop: Lap {pit_data.get('latest_stop_lap', 'N/A')}

Provide a concise analysis (3-4 sentences):
1. What strategy (1-stop vs 2-stop) dominated?
2. Typical pit stop windows?
3. Any notable strategic patterns?"""

        analysis = self._call_llm("You are an expert F1 data analyst.", prompt)
        self.react_logger.answer(self.name, analysis)

        return {
            "race_results": results,
            "pit_data": pit_data,
            "analysis": analysis,
        }
