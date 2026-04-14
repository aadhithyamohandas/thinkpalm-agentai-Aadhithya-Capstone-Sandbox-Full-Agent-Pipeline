"""Strategy Agent — Computes optimal pit stop strategies using tire simulation."""

from agents.base_agent import BaseAgent
from tools.tire_model import generate_strategies, TIRE_COMPOUNDS
from tools.lap_time_tool import compare_compounds
from config import CIRCUITS, PIT_STOP_TIME_LOSS
from core.react_loop import ReActLogger


class StrategyAgent(BaseAgent):
    """Simulates multiple pit strategies and recommends the optimal one."""

    def __init__(self, react_logger: ReActLogger = None):
        super().__init__(
            name="Strategy Agent",
            role="Computes and compares pit stop strategies using tire "
                 "degradation modeling and lap time simulation.",
            react_logger=react_logger,
        )

    def run(self, query: str, context: dict = None) -> dict:
        ctx = context or {}
        circuit_key = ctx.get("circuit_key", "silverstone")
        circuit = CIRCUITS.get(circuit_key, CIRCUITS["silverstone"])
        total_laps = ctx.get("total_laps", circuit["laps"])
        temperature = ctx.get("temperature_c", 25.0)
        rain_intensity = ctx.get("rain_intensity", 0.0)

        # ── THOUGHT ──
        self.react_logger.thought(
            self.name,
            f"I need to simulate multiple pit strategies for {circuit['name']} "
            f"({total_laps} laps) with temp={temperature}°C, rain={rain_intensity}.",
        )

        # ── ACTION 1: Compare compound pace ──
        self.react_logger.action(
            self.name,
            "Running tire compound comparison — estimating pace for Soft/Medium/Hard "
            "over 15-lap sample stints.",
        )
        compound_comparison = compare_compounds(
            total_laps, circuit["base_lap_time"],
            circuit["abrasiveness"], temperature,
        )
        comp_obs = " | ".join(
            f"{c['compound_name']}: avg {c['average_lap']}s, drop {c['pace_drop']}s"
            for c in compound_comparison
        )
        self.react_logger.observation(self.name, f"Compound pace: {comp_obs}")

        # ── ACTION 2: Generate full strategies ──
        self.react_logger.action(
            self.name,
            f"Simulating 8 different pit strategies (1-stop, 2-stop, 3-stop) "
            f"with full lap-by-lap tire degradation modeling.",
        )
        strategies = generate_strategies(
            total_laps, circuit["base_lap_time"],
            circuit["abrasiveness"], temperature,
            rain_intensity, PIT_STOP_TIME_LOSS,
        )

        # ── OBSERVATION ──
        top3 = strategies[:3]
        top3_obs = " | ".join(
            f"#{s['rank']} {s['name']} ({s['num_stops']}-stop): "
            f"{s['total_race_time']:.1f}s (+{s['delta_to_best']:.1f}s)"
            for s in top3
        )
        self.react_logger.observation(self.name, f"Top strategies: {top3_obs}")

        # ── LLM ANALYSIS ──
        self.react_logger.thought(
            self.name,
            "Analyzing simulation results to formulate final recommendation.",
        )

        best = strategies[0]
        stints_detail = "\n".join(
            f"  Stint {i+1}: {TIRE_COMPOUNDS[s['compound']]['name']} "
            f"(Lap {s['start_lap']}-{s['end_lap']}, {s['stint_length']} laps, "
            f"avg {s['average_lap_time']}s/lap)"
            for i, s in enumerate(best["stints"])
        )

        weather_ctx = ctx.get("weather_analysis", "No weather data")
        history_ctx = ctx.get("historical_analysis", "No historical data")

        prompt = f"""You are an F1 chief strategist. Based on simulation results, provide your recommendation.

Circuit: {circuit['name']} ({total_laps} laps)
Temperature: {temperature}°C
Rain Intensity: {rain_intensity}
Pit Stop Time Loss: {PIT_STOP_TIME_LOSS}s

Weather Analysis: {weather_ctx}
Historical Analysis: {history_ctx}

OPTIMAL STRATEGY (by simulation):
{best['name']}
- {best['num_stops']}-stop strategy
- Total Race Time: {best['total_race_time']:.1f}s
- Pit Time Loss: {best['pit_time_loss']}s
{stints_detail}

Runner-up: {strategies[1]['name']} (+{strategies[1]['delta_to_best']:.1f}s)
Third: {strategies[2]['name']} (+{strategies[2]['delta_to_best']:.1f}s)

Provide your recommendation (4-5 sentences):
1. Confirm or challenge the optimal strategy
2. Explain why this strategy works for this circuit
3. Note key risk factors (safety cars, weather changes)
4. Suggest when to consider switching to the backup strategy"""

        recommendation = self._call_llm(
            "You are the chief strategist of an F1 team. Give clear, "
            "actionable pit strategy recommendations.", prompt,
        )
        self.react_logger.answer(self.name, recommendation)

        return {
            "strategies": strategies,
            "best_strategy": best,
            "compound_comparison": compound_comparison,
            "recommendation": recommendation,
        }
