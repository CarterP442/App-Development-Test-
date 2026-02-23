"""
Study Strategy Simulator (CLI prototype)
--------------------------------------
A runnable sample that lets a user:
1) Create "study strategy" scenarios (method, duration, frequency, environment, breaks, difficulty)
2) Run a rule-based simulation to score each scenario
3) Compare scenarios side-by-side
4) See recommendations

Run: python study_simulator.py
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
import random
from typing import List, Dict, Tuple
import math
import textwrap


WRAP = 78


def say(msg: str) -> None:
    print("\n" + "\n".join(textwrap.wrap(msg, width=WRAP)))


def ask(prompt: str) -> str:
    return input(prompt).strip()


def ask_int(prompt: str, min_v: int, max_v: int) -> int:
    while True:
        raw = ask(prompt)
        try:
            val = int(raw)
        except ValueError:
            say(f"Please enter an integer between {min_v} and {max_v}.")
            continue
        if min_v <= val <= max_v:
            return val
        say(f"Value must be between {min_v} and {max_v}.")


def ask_choice(prompt: str, options: Dict[str, str]) -> str:
    while True:
        print("\n" + prompt)
        for k, v in options.items():
            print(f"  {k}) {v}")
        pick = ask("Choose: ").lower()
        if pick in options:
            return pick
        say("Invalid choice. Try again.")


@dataclass
class Strategy:
    name: str
    method: str                 # e.g., "practice_problems"
    session_minutes: int        # e.g., 45
    sessions_per_week: int      # e.g., 4
    environment: str            # e.g., "library"
    break_style: str            # e.g., "pomodoro"
    course_difficulty: int      # 1 (easy) to 5 (hard)
    distraction_risk: int       # 1 (low) to 5 (high)


@dataclass
class Result:
    effectiveness: float        # 0-100
    sustainability: float       # 0-100
    efficiency: float           # 0-100
    burnout_risk: float         # 0-100 (higher = worse)
    predicted_improvement: float  # e.g., +6.5 points
    notes: List[str]


# ---------- Simulation logic (rule-based, explainable) ----------

METHOD_WEIGHTS = {
    # Active learning tends to score higher than passive methods.
    "practice_problems": 1.00,
    "flashcards": 0.90,
    "teaching_someone": 0.95,
    "summarizing": 0.70,
    "rereading": 0.45,
    "highlighting": 0.40,
    "group_study": 0.75,
}

ENVIRONMENT_WEIGHTS = {
    "library": 1.00,
    "quiet_room": 0.95,
    "coffee_shop": 0.85,
    "dorm_room": 0.80,
}

BREAK_WEIGHTS = {
    "pomodoro": 1.00,   # 25/5 style
    "structured": 0.92, # you set break times intentionally
    "none": 0.75,
    "random": 0.80,
}


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def logistic(x: float) -> float:
    # Smooth curve between 0 and 1
    return 1.0 / (1.0 + math.exp(-x))


def simulate(strategy: Strategy) -> Result:
    notes: List[str] = []

    method_w = METHOD_WEIGHTS.get(strategy.method, 0.60)
    env_w = ENVIRONMENT_WEIGHTS.get(strategy.environment, 0.85)
    break_w = BREAK_WEIGHTS.get(strategy.break_style, 0.85)

    # Total study time
    total_minutes = strategy.session_minutes * strategy.sessions_per_week

    # Focus factor: longer sessions tend to reduce focus (especially without good breaks)
    # Sweet spot around 35-60 minutes for many people.
    if strategy.session_minutes <= 60:
        session_focus = 1.0
    elif strategy.session_minutes <= 90:
        session_focus = 0.88
        notes.append("Session length is long; focus may drop after ~60 minutes.")
    else:
        session_focus = 0.75
        notes.append("Very long sessions increase diminishing returns and fatigue.")

    # Distraction penalty: higher risk reduces effectiveness; good environment helps.
    distraction_penalty = 1.0 - (strategy.distraction_risk - 1) * 0.06  # risk 1..5 -> 1.00..0.76

    # Difficulty: harder courses reduce gains per hour unless method is strong.
    difficulty_penalty = 1.0 - (strategy.course_difficulty - 1) * 0.05  # 1..5 -> 1.00..0.80

    # Base effectiveness (0-100) from method + environment + breaks + focus
    base_eff = 85.0 * method_w * env_w * break_w * session_focus * distraction_penalty * difficulty_penalty
    effectiveness = clamp(base_eff, 0, 100)

    # Sustainability: too much time + long sessions + poor breaks increases burnout risk
    time_load = total_minutes / 300.0  # 300 minutes/week (~5h) = 1.0 load
    # Burnout risk grows when load is high, breaks poor, difficulty high.
    burnout_raw = (time_load - 1.0) + (1.0 - break_w) + (strategy.course_difficulty - 3) * 0.15
    burnout_risk = clamp(100.0 * logistic(burnout_raw), 0, 100)

    sustainability = clamp(100.0 - burnout_risk + (break_w - 0.8) * 10.0, 0, 100)

    # Efficiency: effectiveness per hour, penalize very high time that doesn't scale.
    hours = total_minutes / 60.0
    if hours <= 0:
        efficiency = 0.0
    else:
        diminishing = 1.0 / (1.0 + 0.12 * max(0.0, hours - 5.0))  # beyond ~5h/week, returns reduce
        efficiency = clamp((effectiveness * diminishing) / (hours / 5.0) , 0, 100)

    # Predicted improvement: simple estimate; not "true prediction"—just a planning indicator.
    # More time helps, but with diminishing returns; active methods give a boost.
    time_gain = 12.0 * (1.0 - math.exp(-hours / 4.5))  # saturates near 12
    method_bonus = 3.0 * (method_w - 0.6)  # passive methods ~0 bonus
    penalty = 4.0 * (burnout_risk / 100.0)
    predicted_improvement = clamp(time_gain + method_bonus - penalty, 0, 15)

    # Add recommendation-style notes
    if strategy.method in {"rereading", "highlighting"}:
        notes.append("Consider adding active recall (practice problems or flashcards) for stronger retention.")
    if strategy.break_style in {"none", "random"}:
        notes.append("Structured breaks can improve endurance and reduce burnout risk.")
    if strategy.environment in {"dorm_room", "coffee_shop"} and strategy.distraction_risk >= 4:
        notes.append("High distraction risk: switching to a quieter environment may help.")
    if strategy.sessions_per_week <= 2:
        notes.append("Low weekly frequency: shorter, more frequent sessions often improve consistency.")
    if total_minutes > 600:
        notes.append("High weekly study load: consider reducing duration or adding recovery time to avoid burnout.")

    return Result(
        effectiveness=round(effectiveness, 1),
        sustainability=round(sustainability, 1),
        efficiency=round(efficiency, 1),
        burnout_risk=round(burnout_risk, 1),
        predicted_improvement=round(predicted_improvement, 1),
        notes=notes,
    )


# ---------- UI / Interaction (CLI) ----------

METHOD_OPTIONS = {
    "1": "practice_problems",
    "2": "flashcards",
    "3": "teaching_someone",
    "4": "summarizing",
    "5": "rereading",
    "6": "highlighting",
    "7": "group_study",
}

ENV_OPTIONS = {
    "1": "library",
    "2": "quiet_room",
    "3": "coffee_shop",
    "4": "dorm_room",
}

BREAK_OPTIONS = {
    "1": "pomodoro",
    "2": "structured",
    "3": "random",
    "4": "none",
}


def pretty_method(m: str) -> str:
    return m.replace("_", " ").title()


def pretty(s: Strategy) -> str:
    return (
        f"{s.name} — {pretty_method(s.method)} | {s.session_minutes} min x "
        f"{s.sessions_per_week}/wk | {pretty_method(s.environment)} | "
        f"{pretty_method(s.break_style)} | diff {s.course_difficulty}/5 | "
        f"distraction {s.distraction_risk}/5"
    )


def print_result(strategy: Strategy, result: Result) -> None:
    print("\n" + "=" * 72)
    print(pretty(strategy))
    print("-" * 72)
    print(f"Effectiveness:         {result.effectiveness:>5} / 100")
    print(f"Sustainability:        {result.sustainability:>5} / 100")
    print(f"Efficiency:            {result.efficiency:>5} / 100")
    print(f"Burnout risk:          {result.burnout_risk:>5} / 100  (higher = worse)")
    print(f"Predicted improvement: +{result.predicted_improvement:>4} points (planning indicator)")
    if result.notes:
        print("\nNotes / Recommendations:")
        for n in result.notes[:6]:
            print(f"  - {n}")
    print("=" * 72)


def compare(results: List[Tuple[Strategy, Result]]) -> None:
    if len(results) < 2:
        say("Create at least two scenarios to compare.")
        return

    print("\n" + "=" * 72)
    print("Scenario Comparison")
    print("=" * 72)
    headers = ["Scenario", "Eff", "Sus", "Efy", "Burn", "+Improve"]
    print(f"{headers[0]:<26} {headers[1]:>5} {headers[2]:>5} {headers[3]:>5} {headers[4]:>6} {headers[5]:>8}")
    print("-" * 72)

    for s, r in results:
        name = (s.name[:24] + "…") if len(s.name) > 25 else s.name
        print(f"{name:<26} {r.effectiveness:>5.1f} {r.sustainability:>5.1f} {r.efficiency:>5.1f} {r.burnout_risk:>6.1f} {r.predicted_improvement:>8.1f}")

    # Quick "winner" summary
    best_eff = max(results, key=lambda x: x[1].effectiveness)
    best_sus = max(results, key=lambda x: x[1].sustainability)
    best_efy = max(results, key=lambda x: x[1].efficiency)
    lowest_burn = min(results, key=lambda x: x[1].burnout_risk)

    say(f"Highest effectiveness: {best_eff[0].name}")
    say(f"Best sustainability: {best_sus[0].name}")
    say(f"Best efficiency: {best_efy[0].name}")
    say(f"Lowest burnout risk: {lowest_burn[0].name}")


def create_strategy() -> Strategy:
    say("Create a new study strategy scenario.")
    name = ask("Scenario name (e.g., 'Exam Week Plan A'): ")
    if not name:
        name = f"Scenario {random.randint(100, 999)}"

    m_key = ask_choice("Pick a study method:", {k: pretty_method(v) for k, v in METHOD_OPTIONS.items()})
    e_key = ask_choice("Pick an environment:", {k: pretty_method(v) for k, v in ENV_OPTIONS.items()})
    b_key = ask_choice("Pick a break style:", {k: pretty_method(v) for k, v in BREAK_OPTIONS.items()})

    session_minutes = ask_int("Session length in minutes (10-180): ", 10, 180)
    sessions_per_week = ask_int("Sessions per week (1-14): ", 1, 14)
    course_difficulty = ask_int("Course difficulty (1=easy, 5=hard): ", 1, 5)
    distraction_risk = ask_int("Distraction risk (1=low, 5=high): ", 1, 5)

    return Strategy(
        name=name,
        method=METHOD_OPTIONS[m_key],
        session_minutes=session_minutes,
        sessions_per_week=sessions_per_week,
        environment=ENV_OPTIONS[e_key],
        break_style=BREAK_OPTIONS[b_key],
        course_difficulty=course_difficulty,
        distraction_risk=distraction_risk,
    )


def main() -> None:
    say(
        "Study Strategy Simulator (Prototype)\n"
        "Build study-plan scenarios and see explainable scores for effectiveness, "
        "sustainability, efficiency, and burnout risk."
    )

    scenarios: List[Strategy] = []
    results_cache: List[Tuple[Strategy, Result]] = []

    while True:
        print("\n" + "-" * 72)
        choice = ask_choice(
            "Main menu:",
            {
                "1": "Create a new scenario",
                "2": "Run simulation for a scenario",
                "3": "Compare all simulated scenarios",
                "4": "List scenarios",
                "5": "Quit",
            },
        )

        if choice == "1":
            s = create_strategy()
            scenarios.append(s)
            say(f"Saved scenario: {s.name}")

        elif choice == "2":
            if not scenarios:
                say("No scenarios yet. Create one first.")
                continue

            print("\nYour scenarios:")
            for i, s in enumerate(scenarios, start=1):
                print(f"  {i}) {pretty(s)}")

            idx = ask_int("Which scenario number? ", 1, len(scenarios)) - 1
            s = scenarios[idx]
            r = simulate(s)

            # Update cache (replace if already simulated)
            results_cache = [(ss, rr) for (ss, rr) in results_cache if ss.name != s.name]
            results_cache.append((s, r))

            print_result(s, r)

        elif choice == "3":
            if not results_cache:
                say("Run at least one simulation first.")
                continue
            compare(results_cache)

        elif choice == "4":
            if not scenarios:
                say("No scenarios created yet.")
            else:
                say("Current scenarios:")
                for s in scenarios:
                    print(f"  - {pretty(s)}")

        elif choice == "5":
            say("Goodbye!")
            break


if __name__ == "__main__":
    main()