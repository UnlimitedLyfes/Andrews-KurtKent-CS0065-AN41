import random


ROOMS = ["A", "B", "C"]


def normalize_room_state(state):
    state = state.strip().lower()

    if state == "dirty":
        return "Dirty"
    if state == "clean":
        return "Clean"

    return None


def ask_room_state(room):
    while True:
        state = input(f"Is room {room} Dirty or Clean? ")
        normalized_state = normalize_room_state(state)

        if normalized_state is not None:
            return normalized_state

        print("Please enter Dirty or Clean.")


def is_room_dirty(environment, room):
    return environment[room] == "Dirty"


def clean_room(environment, room):
    environment[room] = "Clean"


def show_grid(environment, agent_location):
    room_display = []

    for room in ROOMS:
        if room == agent_location:
            room_display.append(f"[{room}-Agent]")
        else:
            room_display.append(f"[{room}-{environment[room]}]")

    print(" ".join(room_display))


class RuleBasedAgent:
    def __init__(self, start_location="A"):
        self.location = start_location

    def perceive_and_act(self, environment):
        if is_room_dirty(environment, self.location):
            clean_room(environment, self.location)
            return f"Room {self.location} has been cleaned."

        dirty_rooms = [
            room for room in ROOMS
            if room != self.location and is_room_dirty(environment, room)
        ]

        if dirty_rooms:
            next_room = random.choice(dirty_rooms)
            return self.move(next_room)

        return "All rooms are clean. Agent is idle."

    def move(self, room):
        self.location = room
        return f"Moving to room {self.location}"


def ask_steps():
    while True:
        try:
            steps = int(input("\nHow many steps should the agent run? "))

            if steps > 0:
                return steps

            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    environment = {
        room: ask_room_state(room)
        for room in ROOMS
    }

    agent = RuleBasedAgent()
    steps = ask_steps()

    for step in range(1, steps + 1):
        print(f"\nStep {step}:")
        show_grid(environment, agent.location)
        action = agent.perceive_and_act(environment)
        print(action)
        show_grid(environment, agent.location)


if __name__ == "__main__":
    main()
