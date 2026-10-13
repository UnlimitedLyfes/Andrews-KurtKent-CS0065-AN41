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


class RuleBasedAgent:
    def __init__(self, start_location="A"):
        self.location = start_location

    def perceive_and_act(self, environment):
        if is_room_dirty(environment, self.location):
            clean_room(environment, self.location)
            return f"Room {self.location} has been cleaned."

        return self.move()

    def move(self):
        if self.location == "A":
            self.location = "B"
        else:
            self.location = "A"

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
        "A": ask_room_state("A"),
        "B": ask_room_state("B"),
    }

    agent = RuleBasedAgent()
    steps = ask_steps()

    print(f"\nInitial Environment State: {environment}")
    for step in range(1, steps + 1):
        print(f"\nStep {step}: Agent is in room {agent.location}")
        action = agent.perceive_and_act(environment)
        print(action)
        print(f"Environment state: {environment}")


if __name__ == "__main__":
    main()
