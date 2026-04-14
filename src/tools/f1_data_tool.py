"""F1 Data Tool — Jolpica (Ergast-successor) API wrapper for historical race data."""

import requests

JOLPICA_BASE = "https://api.jolpi.ca/ergast/f1"

# Maps our circuit keys to Ergast-format circuit IDs
CIRCUIT_ID_MAP = {
    "bahrain": "bahrain", "jeddah": "jeddah", "melbourne": "albert_park",
    "suzuka": "suzuka", "shanghai": "shanghai", "miami": "miami",
    "imola": "imola", "monaco": "monaco", "montreal": "villeneuve",
    "barcelona": "catalunya", "spielberg": "red_bull_ring",
    "silverstone": "silverstone", "hungaroring": "hungaroring",
    "spa": "spa", "zandvoort": "zandvoort", "monza": "monza",
    "singapore": "marina_bay", "cota": "americas",
    "mexico": "rodriguez", "interlagos": "interlagos",
    "las_vegas": "vegas", "losail": "losail", "yas_marina": "yas_marina",
}


def get_race_results(circuit_key: str, year: int = 2024) -> dict:
    """Fetch race results for a circuit in a given year."""
    ergast_id = CIRCUIT_ID_MAP.get(circuit_key, circuit_key)

    try:
        url = f"{JOLPICA_BASE}/{year}/circuits/{ergast_id}/results.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        if not races:
            return _fallback_results(circuit_key, year)

        race = races[0]
        results = []
        for r in race.get("Results", [])[:10]:
            driver = r.get("Driver", {})
            results.append({
                "position": r.get("position"),
                "driver": f"{driver.get('givenName', '')} {driver.get('familyName', '')}",
                "constructor": r.get("Constructor", {}).get("name", ""),
                "status": r.get("status", ""),
                "laps": r.get("laps", ""),
            })

        return {
            "race_name": race.get("raceName", ""),
            "circuit": race.get("Circuit", {}).get("circuitName", ""),
            "date": race.get("date", ""),
            "results": results,
            "status": "success",
        }
    except requests.RequestException:
        return _fallback_results(circuit_key, year)


def get_pit_stops(circuit_key: str, year: int = 2024) -> dict:
    """Fetch pit stop data to analyze historical strategy patterns."""
    ergast_id = CIRCUIT_ID_MAP.get(circuit_key, circuit_key)

    try:
        url = f"{JOLPICA_BASE}/{year}/circuits/{ergast_id}/pitstops.json?limit=100"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        if not races:
            return _fallback_pit_data(circuit_key)

        pit_stops = races[0].get("PitStops", [])
        stop_laps = [int(ps.get("lap", 0)) for ps in pit_stops]
        unique_drivers = set(ps.get("driverId", "") for ps in pit_stops)
        total = len(pit_stops)
        n_drivers = len(unique_drivers) or 1
        avg_stops = total / n_drivers

        if stop_laps:
            avg_lap = sum(stop_laps) / len(stop_laps)
            first_w = [l for l in stop_laps if l < avg_lap]
            second_w = [l for l in stop_laps if l >= avg_lap]
            fw_avg = sum(first_w) / len(first_w) if first_w else 0
            sw_avg = sum(second_w) / len(second_w) if second_w else 0
        else:
            fw_avg = sw_avg = 0

        return {
            "race_name": races[0].get("raceName", ""),
            "total_pit_stops": total,
            "avg_stops_per_driver": round(avg_stops, 1),
            "first_pit_window_avg_lap": round(fw_avg),
            "second_pit_window_avg_lap": round(sw_avg),
            "earliest_stop_lap": min(stop_laps) if stop_laps else 0,
            "latest_stop_lap": max(stop_laps) if stop_laps else 0,
            "status": "success",
        }
    except requests.RequestException:
        return _fallback_pit_data(circuit_key)


def _fallback_results(circuit_key: str, year: int) -> dict:
    """Fallback when API is unavailable."""
    return {
        "race_name": f"{circuit_key.replace('_', ' ').title()} Grand Prix {year}",
        "circuit": circuit_key.title(),
        "date": f"{year}-01-01",
        "results": [
            {"position": "1", "driver": "Max Verstappen", "constructor": "Red Bull",
             "status": "Finished", "laps": "52"},
        ],
        "note": "Using fallback data (API unavailable)",
        "status": "fallback",
    }


def _fallback_pit_data(circuit_key: str) -> dict:
    """Fallback pit stop patterns based on typical strategies."""
    defaults = {
        "silverstone": (1.3, 20, 38), "monza": (1.1, 22, 40),
        "spa": (1.4, 15, 30), "monaco": (1.0, 30, 0),
        "bahrain": (1.3, 18, 35), "barcelona": (1.5, 18, 36),
    }
    avg_s, fw, sw = defaults.get(circuit_key, (1.2, 20, 35))
    return {
        "race_name": f"{circuit_key.replace('_', ' ').title()} Grand Prix",
        "total_pit_stops": 20,
        "avg_stops_per_driver": avg_s,
        "first_pit_window_avg_lap": fw,
        "second_pit_window_avg_lap": sw,
        "earliest_stop_lap": max(1, fw - 5),
        "latest_stop_lap": sw + 5 if sw else fw + 10,
        "note": "Using fallback data (API unavailable)",
        "status": "fallback",
    }
