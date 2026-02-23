import random
import textwrap

# -----------------------------
# Text-Based Game: "Midnight at the Library"
# Carter-friendly: readable, structured, and easy to expand
# -----------------------------

WRAP_WIDTH = 78


def say(text: str) -> None:
    """Print wrapped text for clean terminal formatting."""
    print("\n" + "\n".join(textwrap.wrap(text, width=WRAP_WIDTH)))


def ask_choice(prompt: str, choices: dict) -> str:
    """
    Ask the player for a choice until they enter a valid option.

    choices format example:
    {
        "1": "Search the desk",
        "2": "Check the door"
    }
    Returns the key chosen (e.g., "1").
    """
    while True:
        print("\n" + prompt)
        for k, v in choices.items():
            print(f"  {k}) {v}")
        ans = input("\nEnter choice: ").strip().lower()
        if ans in choices:
            return ans
        say("Not a valid choice. Try again.")


def add_item(state: dict, item: str) -> None:
    if item not in state["inventory"]:
        state["inventory"].append(item)
        say(f"You got: {item}.")


def has_item(state: dict, item: str) -> bool:
    return item in state["inventory"]


def change_health(state: dict, amount: int) -> None:
    state["health"] = max(0, min(100, state["health"] + amount))
    if amount < 0:
        say(f"You took {-amount} damage. Health: {state['health']}/100")
    elif amount > 0:
        say(f"You recovered {amount} health. Health: {state['health']}/100")


def show_status(state: dict) -> None:
    inv = ", ".join(state["inventory"]) if state["inventory"] else "Nothing"
    print("\n" + "-" * 60)
    print(f"Health: {state['health']}/100")
    print(f"Inventory: {inv}")
    print("-" * 60)


def intro(state: dict) -> None:
    say(
        "MIDNIGHT AT THE LIBRARY\n"
        "You stayed late to finish studying. The campus library is empty—"
        "or at least it should be. The lights flicker. A security announcement "
        "plays: 'Building is now closed.'\n"
        "But the doors don’t unlock.\n"
        "A note slides out from under the front desk."
    )
    add_item(state, "mysterious note")
    say("The note reads: 'Find the three stamps. Then you may leave.'")


def room_front_desk(state: dict) -> None:
    say(
        "You are at the FRONT DESK. There's a dusty guestbook, a locked drawer, "
        "and a hallway leading deeper into the library."
    )
    while True:
        show_status(state)
        choice = ask_choice(
            "What do you do?",
            {
                "1": "Read the guestbook",
                "2": "Try the locked drawer",
                "3": "Go down the hallway",
                "4": "Check the exit doors",
            },
        )

        if choice == "1":
            say(
                "The guestbook has one entry circled in red: "
                "'E. Caldwell — Special Collections.' The ink smells fresh."
            )

        elif choice == "2":
            if has_item(state, "brass key"):
                if not has_item(state, "stamp: owl"):
                    say("You use the brass key. The drawer clicks open.")
                    add_item(state, "stamp: owl")
                    say("You pocket a small stamp shaped like an owl.")
                else:
                    say("The drawer is already open. Nothing else inside.")
            else:
                say("It’s locked tight. You’ll need a key.")

        elif choice == "3":
            return  # leave room

        elif choice == "4":
            if all(has_item(state, s) for s in ["stamp: owl", "stamp: mountain", "stamp: river"]):
                ending_escape(state)
                return
            else:
                say("The doors won’t budge. A cold draft whispers: 'Three stamps...'")

        # If health drops to 0, game ends
        if state["health"] <= 0:
            ending_fail(state)
            return


def room_hallway(state: dict) -> None:
    say(
        "You step into a long HALLWAY. There are three doors:\n"
        "1) Study Rooms\n"
        "2) Computer Lab\n"
        "3) Special Collections\n"
        "Something scurries behind the ceiling tiles."
    )
    while True:
        show_status(state)
        choice = ask_choice(
            "Which door do you enter?",
            {
                "1": "Study Rooms",
                "2": "Computer Lab",
                "3": "Special Collections",
                "4": "Return to Front Desk",
            },
        )

        if choice == "1":
            room_study_rooms(state)
        elif choice == "2":
            room_computer_lab(state)
        elif choice == "3":
            room_special_collections(state)
        elif choice == "4":
            return

        if state["health"] <= 0:
            ending_fail(state)
            return


def random_fear_event(state: dict) -> None:
    """Small random event to add tension."""
    roll = random.random()
    if roll < 0.25:
        say("A fluorescent light pops overhead. Your heart jumps.")
        change_health(state, -5)
    elif roll < 0.40:
        say("You find a half-full bottle of water left behind.")
        change_health(state, +5)
    # else: no event


def room_study_rooms(state: dict) -> None:
    say(
        "You enter the STUDY ROOMS. Whiteboards are filled with messy equations.\n"
        "On one table: a backpack, a sticky note, and a vending machine receipt."
    )
    random_fear_event(state)

    while True:
        show_status(state)
        choice = ask_choice(
            "What do you inspect?",
            {
                "1": "Open the backpack",
                "2": "Read the sticky note",
                "3": "Check the whiteboards",
                "4": "Go back to the hallway",
            },
        )

        if choice == "1":
            if not has_item(state, "brass key"):
                say("Inside the backpack you find a brass key attached to a lanyard.")
                add_item(state, "brass key")
            else:
                say("The backpack is empty now.")

        elif choice == "2":
            say("Sticky note: 'Mountain stamp hidden where the quiet is loud.'")

        elif choice == "3":
            say(
                "The equations form a strange map—almost like mountain ridges. "
                "One corner of the whiteboard peels up."
            )
            if not has_item(state, "stamp: mountain"):
                add_item(state, "stamp: mountain")
                say("Behind the board: a stamp with a mountain emblem.")
            else:
                say("Nothing else behind it.")

        elif choice == "4":
            return

        if state["health"] <= 0:
            return


def room_computer_lab(state: dict) -> None:
    say(
        "You enter the COMPUTER LAB. Screens are asleep. A printer hums softly.\n"
        "There’s a terminal that asks for a password, and a cabinet labeled 'SUPPLIES'."
    )
    random_fear_event(state)

    while True:
        show_status(state)
        choice = ask_choice(
            "What do you do?",
            {
                "1": "Try the terminal",
                "2": "Open the supplies cabinet",
                "3": "Search the printer area",
                "4": "Go back to the hallway",
            },
        )

        if choice == "1":
            say("The terminal blinks: 'PASSWORD:'")
            attempt = input("Type a password (or press Enter to cancel): ").strip().lower()
            if not attempt:
                say("You step away from the terminal.")
                continue

            # Simple password puzzle using earlier clue
            if attempt in {"caldwell", "e. caldwell", "ecaldwell"}:
                say("ACCESS GRANTED. The terminal prints a small ticket: 'RIVER'.")
                add_item(state, "password clue: river")
            else:
                say("ACCESS DENIED. A loud alarm chirps once—then stops.")
                change_health(state, -10)

        elif choice == "2":
            say("The cabinet squeaks open. You find a small snack bar.")
            change_health(state, +10)

        elif choice == "3":
            if has_item(state, "password clue: river") and not has_item(state, "stamp: river"):
                say(
                    "You check the printer tray. A printed page shows a river symbol—"
                    "and taped to the back is a stamp."
                )
                add_item(state, "stamp: river")
            else:
                say("Paper jams and old flyers. Nothing useful.")

        elif choice == "4":
            return

        if state["health"] <= 0:
            return


def room_special_collections(state: dict) -> None:
    say(
        "You enter SPECIAL COLLECTIONS. It's colder here. A glass case holds old "
        "yearbooks and a single plaque: 'E. Caldwell'.\n"
        "A motion sensor light clicks on."
    )
    random_fear_event(state)

    while True:
        show_status(state)
        choice = ask_choice(
            "What do you do?",
            {
                "1": "Inspect the plaque",
                "2": "Check the yearbooks",
                "3": "Search behind the glass case",
                "4": "Go back to the hallway",
            },
        )

        if choice == "1":
            say("The plaque reads: 'When you know the name, the door will open.'")

        elif choice == "2":
            say("Most pages are stuck together... except one, marked with a river doodle.")

        elif choice == "3":
            if not has_item(state, "flashlight"):
                say("You find a small flashlight taped under the case.")
                add_item(state, "flashlight")
            else:
                say("Nothing else behind the case.")

        elif choice == "4":
            return

        if state["health"] <= 0:
            return


def ending_escape(state: dict) -> None:
    say(
        "You return to the exit doors holding the three stamps.\n"
        "The stamps heat up in your palm, then cool.\n"
        "The locks click. The doors swing open.\n"
        "Outside, the night air feels unreal.\n"
        "Your phone buzzes with a final message: 'Class dismissed.'"
    )
    say("✅ YOU ESCAPED — Ending: The Three Stamps")
    state["game_over"] = True


def ending_fail(state: dict) -> None:
    say(
        "Your knees hit the floor. The lights blur into a tunnel.\n"
        "A voice whispers: 'Not tonight.'\n"
        "When you wake up, the library is open… and no one believes you."
    )
    say("💀 GAME OVER — Ending: Trapped in the Stacks")
    state["game_over"] = True


def main() -> None:
    state = {
        "health": 100,
        "inventory": [],
        "game_over": False,
    }

    intro(state)

    # Main navigation loop
    current = "front_desk"
    while not state["game_over"]:
        if current == "front_desk":
            room_front_desk(state)
            if state["game_over"]:
                break
            current = "hallway"
        else:
            room_hallway(state)
            if state["game_over"]:
                break
            current = "front_desk"

    say("Thanks for playing!")


if __name__ == "__main__":
    main()