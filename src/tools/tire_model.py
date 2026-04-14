"""Tire Degradation Model — Physics-based F1 tire performance simulator.

Models 5 tire compounds with non-linear degradation curves,
temperature effects, track abrasiveness, and fuel load impact.
"""

# ── Tire Compound Characteristics ──────────────────────────────────
TIRE_COMPOUNDS = {
    "soft": {
        "name": "Soft", "color": "#FF3333",
        "base_pace_delta": 0.0,       # fastest compound (baseline)
        "degradation_rate": 0.08,     # seconds/lap base degradation
        "cliff_lap": 18,              # lap where degradation spikes
        "optimal_life": 15,           # ideal stint length
        "max_life": 25,
    },
    "medium": {
        "name": "Medium", "color": "#FFD700",
        "base_pace_delta": 0.6,
        "degradation_rate": 0.04,
        "cliff_lap": 32,
        "optimal_life": 28,
        "max_life": 40,
    },
    "hard": {
        "name": "Hard", "color": "#EEEEEE",
        "base_pace_delta": 1.1,
        "degradation_rate": 0.025,
        "cliff_lap": 45,
        "optimal_life": 40,
        "max_life": 55,
    },
    "intermediate": {
        "name": "Intermediate", "color": "#00CC00",
        "base_pace_delta": 5.0,
        "degradation_rate": 0.05,
        "cliff_lap": 35,
        "optimal_life": 30,
        "max_life": 45,
        "rain_bonus": -8.0,
    },
    "wet": {
        "name": "Wet", "color": "#0066FF",
        "base_pace_delta": 10.0,
        "degradation_rate": 0.06,
        "cliff_lap": 30,
        "optimal_life": 25,
        "max_life": 40,
        "rain_bonus": -12.0,
    },
}


def calculate_degradation(compound: str, tire_age: int, track_abrasiveness: float = 0.6) -> float:
    """Calculate tire degradation in seconds for a given tire age.

    Uses non-linear model: linear degradation up to the cliff lap,
    then sharply accelerating degradation beyond it.
    """
    tire = TIRE_COMPOUNDS.get(compound, TIRE_COMPOUNDS["medium"])
    deg_rate = tire["degradation_rate"] * (track_abrasiveness / 0.6)

    if tire_age <= tire["cliff_lap"]:
        return deg_rate * tire_age + 0.002 * (tire_age ** 1.5)
    else:
        over = tire_age - tire["cliff_lap"]
        base_deg = deg_rate * tire["cliff_lap"] + 0.002 * (tire["cliff_lap"] ** 1.5)
        cliff_deg = deg_rate * over * 2.5 + 0.01 * (over ** 2)
        return base_deg + cliff_deg


def calculate_lap_time(
    compound: str,
    tire_age: int,
    lap_number: int,
    total_laps: int,
    base_lap_time: float,
    track_abrasiveness: float = 0.6,
    temperature_c: float = 25.0,
    rain_intensity: float = 0.0,
) -> float:
    """Predict lap time considering tire, fuel, weather, and track factors.

    Args:
        compound:          tire compound key (soft/medium/hard/intermediate/wet)
        tire_age:          laps completed on the current set
        lap_number:        current lap in the race (1-indexed)
        total_laps:        total race laps
        base_lap_time:     circuit's fastest theoretical lap time in seconds
        track_abrasiveness: 0.0-1.0 scale for surface roughness
        temperature_c:     ambient temperature in Celsius
        rain_intensity:    0.0 (dry) to 1.0 (heavy rain)
    """
    tire = TIRE_COMPOUNDS.get(compound, TIRE_COMPOUNDS["medium"])

    lap_time = base_lap_time + tire["base_pace_delta"]

    # Tire degradation (non-linear)
    lap_time += calculate_degradation(compound, tire_age, track_abrasiveness)

    # Fuel burn-off effect (~0.035s/lap faster as fuel decreases)
    fuel_burned_pct = min(1.0, lap_number / total_laps)
    lap_time -= 0.035 * fuel_burned_pct * total_laps * 0.5

    # Temperature effect
    if temperature_c > 35:
        lap_time += (temperature_c - 35) * 0.03
    elif temperature_c < 15:
        lap_time += (15 - temperature_c) * 0.02

    # Rain effect
    if rain_intensity > 0:
        if compound in ("intermediate", "wet"):
            lap_time += tire.get("rain_bonus", 0) * min(rain_intensity, 1.0)
        else:
            lap_time += rain_intensity * 15.0  # slicks in rain = disaster

    return round(lap_time, 3)


def simulate_stint(
    compound: str, start_lap: int, end_lap: int, total_laps: int,
    base_lap_time: float, track_abrasiveness: float = 0.6,
    temperature_c: float = 25.0, rain_intensity: float = 0.0,
) -> dict:
    """Simulate a full stint and return performance statistics."""
    lap_times = []
    for lap in range(start_lap, end_lap + 1):
        tire_age = lap - start_lap + 1
        lt = calculate_lap_time(
            compound, tire_age, lap, total_laps,
            base_lap_time, track_abrasiveness, temperature_c, rain_intensity,
        )
        lap_times.append({"lap": lap, "time": lt, "tire_age": tire_age})

    times_only = [lt["time"] for lt in lap_times]
    total = sum(times_only)

    return {
        "compound": compound,
        "start_lap": start_lap,
        "end_lap": end_lap,
        "stint_length": end_lap - start_lap + 1,
        "total_time": round(total, 3),
        "average_lap_time": round(total / len(times_only), 3) if times_only else 0,
        "fastest_lap": round(min(times_only), 3) if times_only else 0,
        "slowest_lap": round(max(times_only), 3) if times_only else 0,
        "lap_times": lap_times,
    }


def generate_strategies(
    total_laps: int,
    base_lap_time: float,
    track_abrasiveness: float = 0.6,
    temperature_c: float = 25.0,
    rain_intensity: float = 0.0,
    pit_stop_loss: float = 22.0,
) -> list:
    """Generate and rank multiple pit stop strategies by total race time."""
    is_wet = rain_intensity > 0.5
    half = total_laps // 2
    third = total_laps // 3

    if is_wet:
        options = [
            [("intermediate", 1, total_laps)],
            [("wet", 1, half), ("intermediate", half + 1, total_laps)],
            [("intermediate", 1, half), ("intermediate", half + 1, total_laps)],
        ]
    else:
        options = [
            # 1-stop strategies
            [("medium", 1, half), ("hard", half + 1, total_laps)],
            [("hard", 1, half + 5), ("medium", half + 6, total_laps)],
            [("soft", 1, int(total_laps * 0.3)), ("hard", int(total_laps * 0.3) + 1, total_laps)],
            [("medium", 1, int(total_laps * 0.55)), ("medium", int(total_laps * 0.55) + 1, total_laps)],
            # 2-stop strategies
            [("soft", 1, third), ("medium", third + 1, 2 * third), ("soft", 2 * third + 1, total_laps)],
            [("soft", 1, third), ("hard", third + 1, 2 * third + 5), ("medium", 2 * third + 6, total_laps)],
            [("medium", 1, third + 3), ("medium", third + 4, 2 * third + 3), ("soft", 2 * third + 4, total_laps)],
            # 3-stop (aggressive)
            [("soft", 1, int(total_laps * 0.22)),
             ("soft", int(total_laps * 0.22) + 1, int(total_laps * 0.44)),
             ("soft", int(total_laps * 0.44) + 1, int(total_laps * 0.7)),
             ("medium", int(total_laps * 0.7) + 1, total_laps)],
        ]

    strategies = []
    for stints_cfg in options:
        stints, total_time, all_laps = [], 0.0, []
        for compound, start, end in stints_cfg:
            stint = simulate_stint(
                compound, start, end, total_laps,
                base_lap_time, track_abrasiveness, temperature_c, rain_intensity,
            )
            stints.append(stint)
            total_time += stint["total_time"]
            all_laps.extend(stint["lap_times"])

        n_stops = len(stints_cfg) - 1
        total_time += n_stops * pit_stop_loss

        name = " → ".join(
            f"{TIRE_COMPOUNDS[c]['name']}(L{s}-L{e})" for c, s, e in stints_cfg
        )
        strategies.append({
            "name": name,
            "num_stops": n_stops,
            "stints": stints,
            "total_race_time": round(total_time, 3),
            "pit_time_loss": round(n_stops * pit_stop_loss, 1),
            "all_lap_times": all_laps,
        })

    strategies.sort(key=lambda s: s["total_race_time"])
    best = strategies[0]["total_race_time"]
    for i, s in enumerate(strategies):
        s["rank"] = i + 1
        s["delta_to_best"] = round(s["total_race_time"] - best, 3)

    return strategies
