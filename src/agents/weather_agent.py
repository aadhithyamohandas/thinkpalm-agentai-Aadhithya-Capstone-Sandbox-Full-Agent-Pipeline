"""Weather Agent — Analyzes real-time weather and its impact on race strategy."""

from agents.base_agent import BaseAgent
from tools.weather_tool import get_weather
from core.react_loop import ReActLogger


class WeatherAgent(BaseAgent):
    """Fetches live weather data and assesses impact on tire/strategy choices."""

    def __init__(self, react_logger: ReActLogger = None):
        super().__init__(
            name="Weather Agent",
            role="Analyzes real-time weather at F1 circuits and assesses "
                 "impact on tire choice and race strategy.",
            react_logger=react_logger,
        )

    def run(self, query: str, context: dict = None) -> dict:
        circuit_key = (context or {}).get("circuit_key", "silverstone")

        # ── THOUGHT ──
        self.react_logger.thought(
            self.name,
            f"I need to check current weather conditions at {circuit_key} "
            f"to assess their impact on tire strategy.",
        )

        # ── ACTION ──
        self.react_logger.action(
            self.name,
            f"Calling Open-Meteo Weather API for {circuit_key} GPS coordinates",
        )
        weather = get_weather(circuit_key)

        # ── OBSERVATION ──
        if weather.get("status") == "error":
            self.react_logger.observation(
                self.name, f"Weather API error: {weather.get('error')}"
            )
            return {
                "weather": None, "analysis": "Weather data unavailable.",
                "rain_intensity": 0.0, "is_wet": False, "temperature_c": 25.0,
            }

        obs = (
            f"Temperature: {weather['temperature_c']}°C | "
            f"Rain probability: {weather['rain_probability_pct']}% | "
            f"Wind: {weather['wind_speed_kmh']} km/h | "
            f"Humidity: {weather['humidity_pct']}% | "
            f"Conditions: {weather['conditions']}"
        )
        self.react_logger.observation(self.name, obs)

        # ── LLM ANALYSIS ──
        self.react_logger.thought(
            self.name,
            "Analyzing how these conditions affect tire choice and pit strategy.",
        )

        prompt = f"""You are an expert F1 weather strategist. Analyze these conditions:

Circuit: {weather['circuit']} ({weather['location']}, {weather['country']})
Temperature: {weather['temperature_c']}°C
Humidity: {weather['humidity_pct']}%
Wind: {weather['wind_speed_kmh']} km/h
Rain Probability: {weather['rain_probability_pct']}%
Current Rain: {weather['current_rain_mm']} mm
Conditions: {weather['conditions']}

Provide a concise analysis (3-4 sentences):
1. Dry, mixed, or wet race scenario?
2. How does temperature affect tire degradation?
3. Recommended tire compounds?
4. Risk of mid-race weather change?"""

        analysis = self._call_llm("You are an expert F1 weather strategist.", prompt)
        self.react_logger.answer(self.name, analysis)

        # Compute rain intensity for strategy engine
        rain_prob = weather["rain_probability_pct"]
        if rain_prob > 70 or weather["current_rain_mm"] > 1:
            rain_intensity = 0.8
        elif rain_prob > 40:
            rain_intensity = 0.3
        else:
            rain_intensity = 0.0

        return {
            "weather": weather,
            "analysis": analysis,
            "rain_intensity": rain_intensity,
            "is_wet": rain_intensity > 0.5,
            "temperature_c": weather["temperature_c"],
        }
