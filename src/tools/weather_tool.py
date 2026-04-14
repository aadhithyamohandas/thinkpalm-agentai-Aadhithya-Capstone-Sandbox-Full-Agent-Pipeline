"""Weather Tool — Open-Meteo API wrapper for real-time F1 track weather data."""

import requests
from config import CIRCUITS

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail",
}


def get_weather(circuit_key: str) -> dict:
    """Fetch real-time weather data for an F1 circuit from Open-Meteo API.

    Args:
        circuit_key: Key from CIRCUITS dict (e.g. 'silverstone', 'monza').

    Returns:
        Dict with temperature, rain probability, wind, humidity, conditions.
    """
    circuit = CIRCUITS.get(circuit_key)
    if not circuit:
        return {"error": f"Unknown circuit: {circuit_key}", "status": "error"}

    params = {
        "latitude": circuit["lat"],
        "longitude": circuit["lon"],
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,rain,weather_code",
        "hourly": "temperature_2m,precipitation_probability,rain",
        "forecast_days": 1,
        "timezone": "auto",
    }

    try:
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})

        # Average rain probability over next 6 hours
        precip_probs = hourly.get("precipitation_probability", [0])[:6]
        avg_rain_prob = sum(precip_probs) / len(precip_probs) if precip_probs else 0

        weather_code = current.get("weather_code", 0)

        return {
            "circuit": circuit["name"],
            "location": circuit["location"],
            "country": circuit["country"],
            "temperature_c": current.get("temperature_2m", 25),
            "humidity_pct": current.get("relative_humidity_2m", 50),
            "wind_speed_kmh": current.get("wind_speed_10m", 10),
            "current_rain_mm": current.get("rain", 0),
            "rain_probability_pct": round(avg_rain_prob, 1),
            "weather_code": weather_code,
            "conditions": WEATHER_CODES.get(weather_code, "Unknown"),
            "status": "success",
        }
    except requests.RequestException as e:
        return {"error": str(e), "status": "error"}
