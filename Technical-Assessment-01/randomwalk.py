
import csv
import random
from collections import Counter
from types import SimpleNamespace
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.collections import LineCollection
from matplotlib.widgets import Slider, RangeSlider

try:
    import agentpy as ap
except ModuleNotFoundError:
    ap = None

# -------- Get user input from console --------
num_agents = int(input("Enter number of agents: "))
grid_size = int(input("Enter grid size (e.g., 10 for 10x10): "))
num_steps = int(input("Enter number of steps: "))
movement_mode = input("Movement mode (random/avoid/preferred/nooverlap): ").strip().lower() or "random"

preferred_direction = None
if movement_mode == "preferred":
    preferred_direction = input("Preferred direction (right/left/up/down): ").strip().lower()

if num_agents < 1:
    raise ValueError("Number of agents must be at least 1.")
if grid_size < 1:
    raise ValueError("Grid size must be at least 1.")
if num_steps < 0:
    raise ValueError("Number of steps cannot be negative.")
if movement_mode not in {"random", "avoid", "preferred", "nooverlap"}:
    raise ValueError("Movement mode must be random, avoid, preferred, or nooverlap.")
if movement_mode == "preferred" and preferred_direction not in {"right", "left", "up", "down"}:
    raise ValueError("Preferred direction must be right, left, up, or down.")
DIRECTIONS = {
    "right": (1, 0),
    "left": (-1, 0),
    "up": (0, 1),
    "down": (0, -1),
}
RANDOM_DIRECTIONS = list(DIRECTIONS.values())


def balanced_initial_positions(agent_count, grid_dimensions):
    cells = [
        (x, y)
        for x in range(grid_dimensions[0])
        for y in range(grid_dimensions[1])
    ]
    random.shuffle(cells)

    full_rounds, remainder = divmod(agent_count, len(cells))
    positions = cells * full_rounds + random.sample(cells, remainder)
    random.shuffle(positions)
    return positions

# -------- Agent Definition -----------
AgentBase = ap.Agent if ap else object
ModelBase = ap.Model if ap else object


class RandomWalker(AgentBase):
    def __init__(self, model=None):
        if model is not None:
            self.model = model

    def bounded_position(self, direction):
        x, y = self.position
        x = max(0, min(self.model.p.grid_size[0]-1, x + direction[0]))
        y = max(0, min(self.model.p.grid_size[1]-1, y + direction[1]))
        return x, y

    def choose_random_position(self):
        return self.bounded_position(random.choice(RANDOM_DIRECTIONS))

    def choose_preferred_position(self):
        preferred_move = DIRECTIONS[self.model.p.preferred_direction]
        direction_weights = [6 if direction == preferred_move else 1 for direction in RANDOM_DIRECTIONS]
        direction = random.choices(RANDOM_DIRECTIONS, weights=direction_weights, k=1)[0]
        return self.bounded_position(direction)

    def choose_avoidance_position(self, occupied_positions):
        candidates = [self.bounded_position(direction) for direction in RANDOM_DIRECTIONS]
        candidates.append(self.position)
        other_positions = [position for position in occupied_positions if position != self.position]

        if not other_positions:
            return random.choice(candidates)

        best_score = None
        best_candidates = []
        for candidate in candidates:
            nearest_distance = min(
                abs(candidate[0] - other[0]) + abs(candidate[1] - other[1])
                for other in other_positions
            )
            collision_penalty = occupied_positions.count(candidate)
            score = nearest_distance - (collision_penalty * self.model.p.grid_size[0])

            if best_score is None or score > best_score:
                best_score = score
                best_candidates = [candidate]
            elif score == best_score:
                best_candidates.append(candidate)

        return random.choice(best_candidates)

    def choose_nooverlap_position(self, occupied_positions, reserved_positions):
        other_positions = set(occupied_positions)
        other_positions.discard(self.position)
        blocked_positions = other_positions | reserved_positions
        candidates = [self.bounded_position(direction) for direction in RANDOM_DIRECTIONS]
        random.shuffle(candidates)
        candidates.append(self.position)

        for candidate in candidates:
            if candidate not in blocked_positions:
                return candidate

        return self.position

    def choose_next_position(self, occupied_positions):
        if self.model.p.movement_mode == "avoid":
            return self.choose_avoidance_position(occupied_positions)
        if self.model.p.movement_mode == "preferred":
            return self.choose_preferred_position()
        return self.choose_random_position()

# -------- Model Definition -----------
class RandomWalkModel(ModelBase):
    def __init__(self, parameters):
        if ap:
            super().__init__(parameters)
        else:
            self.p = SimpleNamespace(**parameters)

    def setup(self):
        # Create agents
        if ap:
            self.agents = ap.AgentList(self, self.p.agents, RandomWalker)
        else:
            self.agents = [RandomWalker(self) for _ in range(self.p.agents)]

        initial_positions = balanced_initial_positions(self.p.agents, self.p.grid_size)
        for agent, position in zip(self.agents, initial_positions):
            agent.position = position

        if ap:
            self.grid = ap.Grid(self, self.p.grid_size, torus=False)
            self.grid.add_agents(self.agents)

    def step(self):
        occupied_positions = [agent.position for agent in self.agents]

        if self.p.movement_mode == "nooverlap":
            next_positions = [agent.position for agent in self.agents]
            reserved_positions = set()
            agent_order = list(range(len(self.agents)))
            random.shuffle(agent_order)

            for index in agent_order:
                agent = self.agents[index]
                next_position = agent.choose_nooverlap_position(
                    occupied_positions,
                    reserved_positions
                )
                next_positions[index] = next_position
                reserved_positions.add(next_position)

            for agent, position in zip(self.agents, next_positions):
                agent.position = position
            return

        next_positions = [
            agent.choose_next_position(occupied_positions)
            for agent in self.agents
        ]

        for agent, position in zip(self.agents, next_positions):
            agent.position = position

# -------- Parameters from user input -----------
parameters = {
    'agents': num_agents,
    'grid_size': (grid_size, grid_size),
    'steps': num_steps,
    'movement_mode': movement_mode,
    'preferred_direction': preferred_direction
}

# -------- Run Model -----------
model = RandomWalkModel(parameters)
model.setup()

positions_by_frame = [[agent.position for agent in model.agents]]
for _ in range(model.p.steps):
    model.step()
    positions_by_frame.append([agent.position for agent in model.agents])

paths = [
    [positions_by_frame[frame][agent_index] for frame in range(len(positions_by_frame))]
    for agent_index in range(model.p.agents)
]

# -------- Interactive Animation -----------
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.22, right=0.86)
ax.set_xlim(0, model.p.grid_size[0])
ax.set_ylim(0, model.p.grid_size[1])
ax.set_xticks(range(model.p.grid_size[0]+1))
ax.set_yticks(range(model.p.grid_size[1]+1))
ax.grid(True)

agent_colors = [plt.cm.tab20(i % 20) for i in range(model.p.agents)]
trail_collection = LineCollection([], linewidths=2)
ax.add_collection(trail_collection)
scat = ax.scatter([], [], s=200)  # s = size of agents

path_slider_ax = fig.add_axes([0.18, 0.11, 0.70, 0.03])
agent_slider_ax = fig.add_axes([0.18, 0.05, 0.70, 0.03])
speed_slider_ax = fig.add_axes([0.91, 0.22, 0.03, 0.62])
current_frame = {"value": 0}
analysis_done = {"value": False}
frame_counter = fig.text(
    0.96,
    0.015,
    f"Frame: 0 / {model.p.steps}",
    ha="right",
    va="bottom",
)

last_paths_slider = Slider(
    ax=path_slider_ax,
    label="Last paths",
    valmin=0,
    valmax=max(1, model.p.steps),
    valinit=min(25, model.p.steps),
    valstep=1,
)

agent_range_slider = RangeSlider(
    ax=agent_slider_ax,
    label="Agents",
    valmin=1,
    valmax=max(2, model.p.agents),
    valinit=(1, max(1, model.p.agents)),
    valstep=1,
)

speed_slider = Slider(
    ax=speed_slider_ax,
    label="Speed",
    valmin=-10,
    valmax=10,
    valinit=1,
    valstep=1,
    orientation="vertical",
)

if model.p.agents == 1:
    agent_range_slider.set_active(False)

def selected_agent_indices():
    start, end = agent_range_slider.val
    start = max(1, min(model.p.agents, int(round(start))))
    end = max(1, min(model.p.agents, int(round(end))))
    if start > end:
        start, end = end, start
    return range(start - 1, end)

def redraw():
    selected_indices = list(selected_agent_indices())
    frame = current_frame["value"]
    current_positions = [positions_by_frame[frame][i] for i in selected_indices]

    if current_positions:
        scat.set_offsets(current_positions)
        scat.set_color([agent_colors[i] for i in selected_indices])
    else:
        scat.set_offsets([])

    last_paths = int(last_paths_slider.val)
    segments = []
    segment_colors = []

    if last_paths > 0:
        for index in selected_indices:
            start_frame = max(0, frame - last_paths)
            agent_path = paths[index][start_frame:frame + 1]
            path_segments = list(zip(agent_path[:-1], agent_path[1:]))
            segment_count = len(path_segments)

            for segment_index, segment in enumerate(path_segments):
                if segment_count <= 1:
                    alpha = 0.35
                else:
                    alpha = 0.08 + 0.32 * ((segment_index + 1) / segment_count)

                segments.append(segment)
                segment_colors.append(mcolors.to_rgba(agent_colors[index], alpha=alpha))

    trail_collection.set_segments(segments)
    trail_collection.set_color(segment_colors)
    frame_counter.set_text(f"Frame: {frame} / {model.p.steps}")
    fig.canvas.draw_idle()

def analyze_final_positions():
    final_positions = positions_by_frame[-1]
    position_counts = Counter(final_positions)
    x_values = [position[0] for position in final_positions]
    y_values = [position[1] for position in final_positions]
    mean_x = sum(x_values) / len(x_values)
    mean_y = sum(y_values) / len(y_values)

    if len(final_positions) > 1:
        variance_x = sum((x - mean_x) ** 2 for x in x_values) / (len(x_values) - 1)
        variance_y = sum((y - mean_y) ** 2 for y in y_values) / (len(y_values) - 1)
    else:
        variance_x = 0
        variance_y = 0

    occupied_cells = len(position_counts)
    collisions = sum(count - 1 for count in position_counts.values() if count > 1)
    densest_position, densest_count = position_counts.most_common(1)[0]

    with open("final_positions.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["agent", "x", "y"])
        for index, position in enumerate(final_positions, start=1):
            writer.writerow([index, position[0], position[1]])

    print("\nFinal position analysis")
    print("-----------------------")
    print(f"Movement mode: {model.p.movement_mode}")
    if model.p.preferred_direction:
        print(f"Preferred direction: {model.p.preferred_direction}")
    print(f"Agents: {len(final_positions)}")
    print(f"Occupied cells: {occupied_cells} / {model.p.grid_size[0] * model.p.grid_size[1]}")
    print(f"Agents sharing cells: {collisions}")
    print(f"Densest cell: {densest_position} with {densest_count} agent(s)")
    print(f"Mean final position: ({mean_x:.2f}, {mean_y:.2f})")
    print(f"Final position variance: x={variance_x:.2f}, y={variance_y:.2f}")
    print(f"X range: {min(x_values)} to {max(x_values)}")
    print(f"Y range: {min(y_values)} to {max(y_values)}")
    print("Saved final positions to final_positions.csv")

def speed_to_interval(speed):
    fps = abs(speed) * 2
    if fps == 0:
        return 250
    return max(1, int(1000 / fps))

def update_timer_interval(val=None):
    speed = int(speed_slider.val)
    timer.interval = speed_to_interval(speed)

def tick():
    speed = int(speed_slider.val)
    if speed == 0:
        return True

    direction = 1 if speed > 0 else -1
    next_frame = max(0, min(model.p.steps, current_frame["value"] + direction))

    if next_frame != current_frame["value"]:
        current_frame["value"] = next_frame
        redraw()

    if current_frame["value"] == model.p.steps and not analysis_done["value"]:
        analysis_done["value"] = True
        analyze_final_positions()

    return True

last_paths_slider.on_changed(lambda val: redraw())
agent_range_slider.on_changed(lambda val: redraw())
speed_slider.on_changed(update_timer_interval)
redraw()

if model.p.steps == 0:
    analysis_done["value"] = True
    analyze_final_positions()

timer = fig.canvas.new_timer(interval=speed_to_interval(int(speed_slider.val)))
timer.add_callback(tick)
timer.start()
plt.show()
