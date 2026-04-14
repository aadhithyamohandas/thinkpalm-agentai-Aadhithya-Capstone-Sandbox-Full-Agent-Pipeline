"""Lap Time Estimator — Quick estimation tool for F1 lap times.

Provides simplified lap-time estimates for strategy comparison,
factoring in tire compound, age, fuel, and conditions.
"""

from tools.tire_model import calculate_lap_time, TIRE_COMPOUNDS


def estimate_stint_time(
    compound: str,
    stint_length: int,
    start_lap: int,
    total_laps: int,
    base_lap_time: float,
    track_abrasiveness: float = 0.6,
    temperature_c: float = 25.0,
    rain_intensity: float = 0.0,
) -> dict:
    """Estimate total time for a stint without full lap-by-lap simulation.

    Returns a quick summary with estimated total stint time and averages.
    """
    total = 0.0
    fastest = float("inf")
    slowest = 0.0

    for i in range(stint_length):
        lap = start_lap + i
        tire_age = i + 1
        lt = calculate_lap_time(
            compound, tire_age, lap, total_laps,
            base_lap_time, track_abrasiveness, temperature_c, rain_intensity,
        )
        total += lt
        fastest = min(fastest, lt)
        slowest = max(slowest, lt)

    return {
        "compound": compound,
        "compound_name": TIRE_COMPOUNDS.get(compound, {}).get("name", compound),
        "stint_length": stint_length,
        "total_time": round(total, 3),
        "average_lap": round(total / stint_length, 3) if stint_length else 0,
        "fastest_lap": round(fastest, 3),
        "slowest_lap": round(slowest, 3),
        "pace_drop": round(slowest - fastest, 3),
    }


def compare_compounds(
    total_laps: int,
    base_lap_time: float,
    track_abrasiveness: float = 0.6,
    temperature_c: float = 25.0,
) -> list:
    """Compare all dry compounds over a 15-lap sample stint."""
    results = []
    for key in ["soft", "medium", "hard"]:
        est = estimate_stint_time(
            key, 15, 1, total_laps, base_lap_time,
            track_abrasiveness, temperature_c,
        )
        results.append(est)
    return results
