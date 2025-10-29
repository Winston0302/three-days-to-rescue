# Three Days to Rescue

A replayable **command-line survival story** for COMP9001.  
You are **Winston**, trapped in **Valkyrie** after an alien war. Survive **3 in-game days** until the rescue arrives. Each day one **random, non-repeating event** appears; your choices change resources and endings.

## How to Run
```bash
python3 main.py
# Optional: when prompted, enter an integer seed to reproduce a run,
# or press Enter to use a random seed.
```

## Core Rules
- Resources are tracked in **thirds (0..3)**:
  - **Water**: 3/3 = one full bottle
  - **Food**: 3/3 = one full can
- **Daily consumption** after each event: **1/3 water + 1/3 food**.
- If either resource is missing when required, the game ends with a custom **Death** message.
- Survive through the end of **Day 3** to reach the **Rescued** ending.

## Event Pool (sampled without replacement; one per day)
1. **Neighbor asks for water** — Give **1/3 water** (50% chance to get **+2/3 food** at night) or refuse.  
2. **Neighbor asks for food** — Give **1/3 food** (50% chance to get **+2/3 water** at night) or refuse.  
3. **Trade for a weapon** — Give **1/3 water + 1/3 food**; **45%** chance to receive a handgun. **Refusing** triggers a night raid (instant death).  
4. **Shelter a stranger** — 50% human → **+1/3 water +1/3 food**; 50% alien disguise → **weapon required** to survive (weapon is then lost), otherwise death.

## Features
- **File I/O:** every run appended to `runs.jsonl` with UTC time, seed, ending, and a short log.  
- **Exceptions:** robust input loop; fatal outcomes raise a custom `Death` exception.  
- **Reproducibility:** optional integer seed to replay the same RNG path.  
- **Single-file, no third-party libraries.**

## Files
- `main.py` — single-file CLI game. Contains:
  - `State` model (water/food in thirds, weapon flag), event functions
    (`ev_share_water`, `ev_share_food`, `ev_trade_weapon`, `ev_shelter_stranger`),
    daily consumption, and the main loop.
- `runs.jsonl` — append-only play log **created after the first run**.
  Each line is one JSON record with:
  - `time_utc` (ISO 8601), `seed` (optional int),
  - `final` (day/water/food/weapon/alive/ending),
  - `log` (short textual trace of key steps).

## Example
```bash
python3 main.py
# Optional: enter an integer seed at the prompt to reproduce a run
— Three Days to Rescue —
You are Winston, trapped in Valkyrie. Survive 3 days. Each day requires at least 1/3 water and 1/3 food.
Initial supplies: 1 bottle of water (3/3), 1 can of food (3/3).
(Optional) Enter a random seed to reproduce a run (or press Enter for random): 42

=== Day 1 ===
DAWN — A weak voice through the wall: "Can you spare 1/3 bottle of water? I’ll repay with food tonight."
[1] Give 1/3 bottle of water
[2] Refuse / ignore
Choose an option by number: 1
Night falls. The neighbor keeps the promise: +2/3 can of food.
Daily consumption: water -1/3, food -1/3. Remaining — Water 2/3, Food 3/3.

=== Day 2 ===
DUSK — A hard voice at the door: "Give me 1/3 water and 1/3 food. I’ll give you a weapon."
[1] Give (1/3 water + 1/3 food)   [2] Refuse
Choose an option by number: 1
A handgun slides under the door. You have a weapon.
Daily consumption: water -1/3, food -1/3. Remaining — Water 1/3, Food 1/3.

=== Day 3 ===
DAWN — A man pleads: "Please shelter me. I carry supplies."
[1] Shelter him   [2] Refuse to shelter
Choose an option by number: 1
He is a real survivor. +1/3 water and +1/3 food.
Daily consumption: water -1/3, food -1/3. Remaining — Water 0/3, Food 0/3.

You held on through the end of Day 3. The rescue team arrives. You are saved!
(Log appended to runs.jsonl)
