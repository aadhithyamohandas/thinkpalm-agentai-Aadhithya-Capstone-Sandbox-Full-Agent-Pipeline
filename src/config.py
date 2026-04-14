"""Configuration — API keys, F1 circuit database, and constants."""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Configuration ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Racing Constants ───────────────────────────────────────────────
PIT_STOP_TIME_LOSS = 22.0  # seconds lost per pit stop (stationary + in/out lap delta)

# ── F1 Circuit Database ───────────────────────────────────────────
# Each circuit has GPS coords (for weather), race laps, base lap time,
# and track abrasiveness (affects tire degradation).
CIRCUITS = {
    "bahrain": {
        "name": "Bahrain International Circuit", "location": "Sakhir",
        "country": "Bahrain", "lat": 26.0325, "lon": 50.5106,
        "laps": 57, "base_lap_time": 93.0, "abrasiveness": 0.8,
    },
    "jeddah": {
        "name": "Jeddah Corniche Circuit", "location": "Jeddah",
        "country": "Saudi Arabia", "lat": 21.6319, "lon": 39.1044,
        "laps": 50, "base_lap_time": 90.0, "abrasiveness": 0.5,
    },
    "melbourne": {
        "name": "Albert Park Circuit", "location": "Melbourne",
        "country": "Australia", "lat": -37.8497, "lon": 144.968,
        "laps": 58, "base_lap_time": 79.0, "abrasiveness": 0.4,
    },
    "suzuka": {
        "name": "Suzuka International Racing Course", "location": "Suzuka",
        "country": "Japan", "lat": 34.8431, "lon": 136.5407,
        "laps": 53, "base_lap_time": 91.0, "abrasiveness": 0.6,
    },
    "miami": {
        "name": "Miami International Autodrome", "location": "Miami",
        "country": "USA", "lat": 25.9581, "lon": -80.2389,
        "laps": 57, "base_lap_time": 90.0, "abrasiveness": 0.6,
    },
    "imola": {
        "name": "Autodromo Enzo e Dino Ferrari", "location": "Imola",
        "country": "Italy", "lat": 44.3439, "lon": 11.7167,
        "laps": 63, "base_lap_time": 76.0, "abrasiveness": 0.5,
    },
    "monaco": {
        "name": "Circuit de Monaco", "location": "Monte Carlo",
        "country": "Monaco", "lat": 43.7347, "lon": 7.4206,
        "laps": 78, "base_lap_time": 73.0, "abrasiveness": 0.3,
    },
    "montreal": {
        "name": "Circuit Gilles Villeneuve", "location": "Montreal",
        "country": "Canada", "lat": 45.5, "lon": -73.5228,
        "laps": 70, "base_lap_time": 75.0, "abrasiveness": 0.6,
    },
    "barcelona": {
        "name": "Circuit de Barcelona-Catalunya", "location": "Barcelona",
        "country": "Spain", "lat": 41.57, "lon": 2.2611,
        "laps": 66, "base_lap_time": 78.0, "abrasiveness": 0.7,
    },
    "spielberg": {
        "name": "Red Bull Ring", "location": "Spielberg",
        "country": "Austria", "lat": 47.2197, "lon": 14.7647,
        "laps": 71, "base_lap_time": 66.0, "abrasiveness": 0.5,
    },
    "silverstone": {
        "name": "Silverstone Circuit", "location": "Silverstone",
        "country": "UK", "lat": 52.0786, "lon": -1.0169,
        "laps": 52, "base_lap_time": 88.0, "abrasiveness": 0.6,
    },
    "hungaroring": {
        "name": "Hungaroring", "location": "Budapest",
        "country": "Hungary", "lat": 47.5789, "lon": 19.2486,
        "laps": 70, "base_lap_time": 78.0, "abrasiveness": 0.5,
    },
    "spa": {
        "name": "Circuit de Spa-Francorchamps", "location": "Spa",
        "country": "Belgium", "lat": 50.4372, "lon": 5.9714,
        "laps": 44, "base_lap_time": 106.0, "abrasiveness": 0.5,
    },
    "zandvoort": {
        "name": "Circuit Zandvoort", "location": "Zandvoort",
        "country": "Netherlands", "lat": 52.3886, "lon": 4.5408,
        "laps": 72, "base_lap_time": 72.0, "abrasiveness": 0.5,
    },
    "monza": {
        "name": "Autodromo Nazionale Monza", "location": "Monza",
        "country": "Italy", "lat": 45.6156, "lon": 9.2811,
        "laps": 53, "base_lap_time": 82.0, "abrasiveness": 0.4,
    },
    "singapore": {
        "name": "Marina Bay Street Circuit", "location": "Singapore",
        "country": "Singapore", "lat": 1.2914, "lon": 103.8644,
        "laps": 62, "base_lap_time": 98.0, "abrasiveness": 0.6,
    },
    "cota": {
        "name": "Circuit of the Americas", "location": "Austin",
        "country": "USA", "lat": 30.1328, "lon": -97.6411,
        "laps": 56, "base_lap_time": 96.0, "abrasiveness": 0.7,
    },
    "mexico": {
        "name": "Autodromo Hermanos Rodriguez", "location": "Mexico City",
        "country": "Mexico", "lat": 19.4042, "lon": -99.0907,
        "laps": 71, "base_lap_time": 78.0, "abrasiveness": 0.6,
    },
    "interlagos": {
        "name": "Autodromo Jose Carlos Pace", "location": "Sao Paulo",
        "country": "Brazil", "lat": -23.7036, "lon": -46.6997,
        "laps": 71, "base_lap_time": 72.0, "abrasiveness": 0.7,
    },
    "las_vegas": {
        "name": "Las Vegas Strip Circuit", "location": "Las Vegas",
        "country": "USA", "lat": 36.1147, "lon": -115.1728,
        "laps": 50, "base_lap_time": 94.0, "abrasiveness": 0.5,
    },
    "losail": {
        "name": "Losail International Circuit", "location": "Lusail",
        "country": "Qatar", "lat": 25.49, "lon": 51.4542,
        "laps": 57, "base_lap_time": 87.0, "abrasiveness": 0.8,
    },
    "yas_marina": {
        "name": "Yas Marina Circuit", "location": "Abu Dhabi",
        "country": "UAE", "lat": 24.4672, "lon": 54.6031,
        "laps": 58, "base_lap_time": 87.0, "abrasiveness": 0.5,
    },
}
