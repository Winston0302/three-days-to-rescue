"""
Three Days to Rescue — COMP9001 Final Project (single-file edition)

Author: <your name / SID>
Course: COMP9001 Introduction to Programming

What this program is:
    A small CLI survival story. You are Winston, trapped in Valkyrie after an
    alien war. Survive 3 in-game days until the rescue arrives. Each day one
    random event appears; your choices affect resources and endings.

How to run:
    python3 main.py
    # (Optional) enter a seed at the prompt to make runs reproducible.

Advanced concepts demonstrated (for marking):
    • File I/O  — every run is appended to 'runs.jsonl' as one JSON line.
    • Exceptions — robust input validation loop; a custom Death exception is
      raised to short-circuit the game on fatal outcomes.

Notes:
    • Water and food are represented as "thirds" (0..3). Each day consumes
      1/3 of water and 1/3 of food. If either is missing for the day, you die.
    • No third-party libraries; standard library only; single source file.
"""

import random, json, datetime

# --------------------------- Game state & helpers ----------------------------

class State:
    """Game state; water/food measured in 'thirds' (0..3)."""
    def __init__(self):
        self.day = 1
        self.water = 3   # 3/3 = 1 full bottle
        self.food  = 3   # 3/3 = 1 full can
        self.weapon = False
        self.alive = True
        self.ending = None
        self.log = []    # short text log of key steps

    def snapshot(self) -> dict:
        return {
            "day": self.day,
            "water_thirds": self.water,
            "food_thirds": self.food,
            "weapon": self.weapon,
            "alive": self.alive,
            "ending": self.ending,
        }

class Death(Exception):
    """Raised to immediately end the game with a reason."""

def clamp03(x: int) -> int:
    return 0 if x < 0 else (3 if x > 3 else x)

def show_status(st: "State") -> None:
    print(f"[Status] Water {st.water}/3 | Food {st.food}/3 | Weapon {'Yes' if st.weapon else 'No'}")

def ask(prompt: str, options: list[str]) -> int:
    """Ask until the user enters a valid number 1..n."""
    while True:
        print(prompt)
        for i, text in enumerate(options, 1):
            print(f"[{i}] {text}")
        s = input("Choose an option by number: ").strip()
        if s.isdigit():
            k = int(s)
            if 1 <= k <= len(options):
                return k
        print("Invalid input. Please type a number shown above.\n")

# ------------------------------- Events -------------------------------------

def ev_share_water(st: State, rng: random.Random):
    st.log.append("Event: neighbor asks for water")
    print("DAWN — A weak voice through the wall: \"Can you spare 1/3 bottle of water? I’ll repay with food tonight.\"")
    show_status(st)
    k = ask("Your decision?", ["Give 1/3 bottle of water", "Refuse / ignore"])
    if k == 1:
        if st.water <= 0:
            print("You feel the empty bottle. There is no water to share.")
        else:
            st.water -= 1
            print("You pass roughly a third of your water through the crack.")
        # 50% chance to get 2/3 can of food at night
        if rng.random() < 0.5:
            st.food = clamp03(st.food + 2)
            print("Night falls. The neighbor keeps the promise: +2/3 can of food.")
        else:
            print("You wait into the night. No one returns. The promise was empty.")
    else:
        print("You stay silent. Nothing else happens.")

def ev_share_food(st: State, rng: random.Random):
    st.log.append("Event: neighbor asks for food")
    print("DAY — Someone knocks softly: \"Could you spare 1/3 of a can? I’ll bring water later.\"")
    show_status(st)
    k = ask("Your decision?", ["Give 1/3 of a can", "Refuse / ignore"])
    if k == 1:
        if st.food <= 0:
            print("There’s no food left to share.")
        else:
            st.food -= 1
            print("You hand out about a third of your can.")
        # 50% chance to get 2/3 bottle of water at night
        if rng.random() < 0.5:
            st.water = clamp03(st.water + 2)
            print("That night they keep the promise: +2/3 bottle of water.")
        else:
            print("No repayment arrives. Only the wind moves through the cracks.")
    else:
        print("You refuse. Footsteps fade away.")

def ev_trade_weapon(st: State, rng: random.Random):
    st.log.append("Event: trade food+water for weapon")
    print("DUSK — A hard voice at the door: \"Give me 1/3 water and 1/3 food. I’ll give you a weapon. Fair trade.\"")
    show_status(st)
    k = ask("Your decision?", ["Give (1/3 water + 1/3 food)", "Refuse"])
    if k == 1:
        if st.water > 0: st.water -= 1
        if st.food  > 0: st.food  -= 1
        print("You hand over the rations.")
        # 45% chance they deliver a weapon
        if rng.random() < 0.45:
            st.weapon = True
            print("Late at night, a cold object slides under the door: a handgun. You have a weapon.")
        else:
            print("They vanish with your supplies. No weapon arrives.")
    else:
        raise Death("You refused the extortion. At night they break in and shoot you.")

def ev_shelter_stranger(st: State, rng: random.Random):
    st.log.append("Event: shelter a stranger")
    print("DAWN — A man pleads: \"Please shelter me. I carry two bottles of water and two cans. I just need a safe place.\"")
    show_status(st)
    k = ask("Your decision?", ["Shelter him", "Refuse to shelter"])
    if k == 1:
        # 50% human / 50% alien in disguise
        if rng.random() < 0.5:
            print("He is a real survivor. Grateful, he shares supplies: +1/3 water, +1/3 food.")
            st.water = clamp03(st.water + 1)
            st.food  = clamp03(st.food + 1)
        else:
            print("His skin ripples; an alien form bursts forth and attacks!")
            if st.weapon:
                print("You fire the handgun and drop the creature, but the weapon is ruined in the struggle.")
                st.weapon = False
            else:
                raise Death("You were killed by an alien disguised as a human.")
    else:
        print("You keep the door barred. The stranger leaves into the ruins.")

EVENTS = [ev_share_water, ev_share_food, ev_trade_weapon, ev_shelter_stranger]

# --------------------------- Daily consumption ------------------------------

def consume_daily(st: State):
    """Consume 1/3 water and 1/3 food. Die if you cannot meet the minimum."""
    st.log.append("Consume daily rations")
    if st.water <= 0 or st.food <= 0:
        raise Death("You lacked the minimum daily intake (food or water).")
    st.water -= 1
    st.food  -= 1
    print(f"Daily consumption: water -1/3, food -1/3. Remaining — Water {st.water}/3, Food {st.food}/3.")

# --------------------------------- Main -------------------------------------

def main():
    print("— Three Days to Rescue —")
    print("You are Winston, trapped in Valkyrie. Survive 3 days. Each day requires at least 1/3 water and 1/3 food.")
    print("Initial supplies: 1 bottle of water (3/3), 1 can of food (3/3).")
    def read_seed(prompt: str) -> int | None:
        s = input(prompt).strip()
        if s == "":        
            return None
        try:
            return int(s)    
        except ValueError:
            print("Invalid seed. Proceeding with a random seed.\n")
            return None

    seed = read_seed("(Optional) Enter a random seed to reproduce a run (or press Enter for random): ")
    rng = random.Random(seed)

    st = State()
    start_utc = datetime.datetime.utcnow().isoformat()

    # pick 3 distinct events in random order
    day_events = rng.sample(EVENTS, 3)

    try:
        for day, ev in enumerate(day_events, start=1):
            st.day = day
            print(f"\n=== Day {day} ===")
            ev(st, rng)          # run the day's event
            consume_daily(st)    # then apply the daily cost
        st.ending = "Rescued"
        print("\nYou held on through the end of Day 3. The rescue team arrives. You are saved!")
    except Death as d:
        st.alive = False
        st.ending = f"Death: {d}"
        print(f"\n[DEATH] {d}")
    finally:
        # Append one JSON line to a local log file (File I/O for marking)
        rec = {"time_utc": start_utc, "seed": seed, "final": st.snapshot(), "log": st.log}
        with open("runs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print("\n(Log appended to runs.jsonl)")

if __name__ == "__main__":
    main()
