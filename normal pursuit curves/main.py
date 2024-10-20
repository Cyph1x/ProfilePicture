import math
from typing import List
import random
from copy import deepcopy
import drawsvg as draw
from drawsvg import Lines, Group

debug_figures = False
# Mice starting circle
debug_figures_starting_circle = True
debug_figures_position_group_dot = True
remove_duplicate_lines = False
# Mice
mice_count = 3 # How many mice
#step_size = 10 # How much each mouse moves in each step
target_distance_scale = 0.035 # How much each mouse moves towards the target
distance = 2000 # Distance between the mice and 0,0
step_count = 50 # Number of steps
rotation = 0 # Rotation offset for mice positioning
mice_group_count = 5 # Number of mice groups

# defining the offset required to place the corner of a group at 0,0
angle =  2 * math.pi / mice_count
start_x = -distance * math.cos(angle)
start_y = -distance * math.sin(angle)
# find the distance between two corners of the group
corner1_x = distance * math.cos(angle)
corner1_y = distance * math.sin(angle)
angle =  0 * 2 * math.pi / mice_count
corner2_x = distance * math.cos(angle)
corner2_y = distance * math.sin(angle)
group_distance = math.sqrt((corner1_x - corner2_x) ** 2 + (corner1_y - corner2_y) ** 2)

# Animation
enable_animation = False# Enable or disable the animation
animation_duration_ms = 1000 # Duration of the animation in milliseconds
begin_ms = 0 # Start time of the animation in milliseconds
duration_ms = 1 # Duration of each step in milliseconds
infinite_repeat = True # Repeat the animation infinitely
fill = 'freeze' # Fill the final state of the animation

# Canvas
#resolution = 5000
resolution = group_distance * 2
canvas = draw.Drawing(resolution, resolution, origin="center")

#set the background color
canvas.append(draw.Rectangle(-resolution/2, -resolution/2, resolution, resolution, fill='None'))

class Mouse:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.new_x = x
        self.new_y = y

    def set_target(self, target):
        self.target = target

    def get_target(self):
        return self.target

    def get_position(self):
        return (self.x, self.y)

    def get_target_distance(self):
        # move towards the target by step_size
        target = self.get_target()
        if target is None:
            return
        target_x, target_y = target.get_position()
        distance = math.sqrt((self.x - target_x) ** 2 + (self.y - target_y) ** 2)
        return distance

    def move(self, step_size):
        distance = self.get_target_distance()
        target_x,target_y = self.get_target().get_position()
        if distance < step_size:
            # If the distance is less than the step_size, the mouse reaches the target
            self.x = target_x
            self.y = target_y
            self.new_x = target_x
            self.new_y = target_y
            return
        # Calculate the angle between the mouse and the target
        angle = math.atan2(target_y - self.y, target_x - self.x)
        # Calculate the new position of the mouse
        self.new_x = self.x + step_size * math.cos(angle)
        self.new_y = self.y + step_size * math.sin(angle)
        #print(f"({self.x:.2f}, {self.y:.2f}) -> ({self.new_x:.2f}, {self.new_y:.2f})")

    def update_position(self):
        self.x = self.new_x
        self.y = self.new_y

def generate_mice_lines(n: int, n_steps: int, distance: float, rotation: float, reverse: bool) -> Group:
    new_mice = []
    g = draw.Group()
    if debug_figures and debug_figures_starting_circle:
        # Define the circle radius
        g.append(draw.Circle(0, 0, distance, fill='none', stroke='black'))
    for i in range(n):
        angle = rotation + i * 2 * math.pi / n
        #angle = random.uniform(0, 2 * math.pi)
        x = 0 + distance * math.cos(angle)
        y = 0 + distance * math.sin(angle)
        new_mice.append(Mouse(x, y))
    if reverse:
        new_mice.reverse()
    for i in range(n):
        print(f"Mouse {i}: ({new_mice[i].x:.2f}, {new_mice[i].y:.2f})")
        new_mice[i].set_target(new_mice[(i + 1) % n])

    for i in range(n_steps):
        for mouse in new_mice:
            step_size = mouse.get_target_distance() * target_distance_scale
            mouse.move(step_size)

        mouse_lines = []
        target_lines = []
        for mouse in new_mice:
            x1, y1 = mouse.get_position()
            x2, y2 = mouse.get_target().get_position()
            x3, y3 = mouse.new_x, mouse.new_y
            x4, y4 = mouse.get_target().new_x, mouse.get_target().new_y
            mouse_lines.extend([x1, y1, x2, y2])
            target_lines.extend([x3, y3, x4, y4])

        mouse_lines_background = draw.Lines(*mouse_lines, close=True, fill='none', stroke='black', stroke_width=2,opacity=0.5)
        target_lines_background = draw.Lines(*target_lines, close=True, fill='none', stroke='black', stroke_width=2,opacity=0.5)
        mouse_lines_foreground = draw.Lines(*mouse_lines, close=True, fill='none', stroke='white', stroke_width=2,opacity=0.5)
        target_lines_foreground = draw.Lines(*target_lines, close=True, fill='none', stroke='white', stroke_width=2,opacity=0.5)

        if reverse:
            if enable_animation:
                mouse_lines_background.append_anim(draw.Animate(attributeName='d', to=target_lines_background.args["d"], begin=f"{begin_ms}ms", dur=f"{animation_duration_ms}ms",repeatCount='indefinite'))
                mouse_lines_foreground.append_anim(draw.Animate(attributeName='d', to=target_lines_foreground.args["d"], begin=f"{begin_ms}ms", dur=f"{animation_duration_ms}ms",repeatCount='indefinite'))
                #mouse_lines.add_key_frame(0, d=target_lines.args["d"])
                #mouse_lines.add_key_frame(animation_duration_ms/1000, d=mouse_lines.args["d"])
            lines_foreground=mouse_lines_foreground
            lines_background=target_lines_background
        else:
            if enable_animation:
                target_lines_background.append_anim(draw.Animate(attributeName='d', to=mouse_lines_background.args["d"], begin=f"{begin_ms}ms", dur=f"{animation_duration_ms}ms",repeatCount='indefinite'))
                target_lines_foreground.append_anim(draw.Animate(attributeName='d', to=mouse_lines_foreground.args["d"], begin=f"{begin_ms}ms", dur=f"{animation_duration_ms}ms",repeatCount='indefinite'))
                #target_lines.add_key_frame(0, d=mouse_lines.args["d"])
                #target_lines.add_key_frame(animation_duration_ms/1000, d=target_lines.args["d"])
            lines_foreground=target_lines_foreground
            lines_background=mouse_lines_background

        g.append(lines_background)
        g.append(lines_foreground)
        for mouse in new_mice:
            mouse.update_position()
    return g

forward_animation = generate_mice_lines(mice_count, step_count, distance, rotation,reverse=False)
reverse_animation = generate_mice_lines(mice_count, step_count, distance, rotation,reverse=True)

group_positions = [(start_x, start_y, rotation)]

def make_group_positions(group_positions: List[tuple[float, float, float]], distance: float) -> List[tuple]:
    new_group_positions = []

    for x, y, rotation in group_positions:
        new_mice = []
        for i in range(mice_count):
            angle = rotation + i * 2 * math.pi / mice_count
            mouse_x = x + distance * math.cos(angle)
            mouse_y = y + distance * math.sin(angle)
            new_mice.append(Mouse(mouse_x, mouse_y))

        new_mice.reverse()

        for i in range(mice_count):
            new_mice[i].set_target(new_mice[(i + 1) % mice_count])


        if debug_figures and debug_figures_position_group_dot:
            # draw the centre point
            canvas.append(draw.Circle(x, y, 5, fill='green'))
        # existing circle center
        for mouse in new_mice:
            mouse_x, mouse_y = mouse.get_position()
            target_x, target_y = mouse.get_target().get_position()

            middle_x = (mouse_x + target_x) / 2
            middle_y = (mouse_y + target_y) / 2

            # calculate the distance between the mouse and the target
            d = mouse.get_target_distance()

            # calculate the distance between the middle point to the centre of the next group
            h = math.sqrt(distance ** 2 - (d / 2) ** 2)

            # Calculate the angle between the average point and the middle point
            external_angle = math.atan2(middle_y - y, middle_x - x)
            external_angle_deg = math.degrees(external_angle)

            # Calculate the new position of the mouse using the h distance
            new_mouse_group_x = middle_x + h * math.cos(external_angle)
            new_mouse_group_y = middle_y + h * math.sin(external_angle)

            middle_centre_distance = math.sqrt((start_x - middle_x) ** 2 + (start_y - middle_y) ** 2)
            new_mouse_group_to_centre_distance = math.sqrt(
                (start_x - new_mouse_group_x) ** 2 + (start_y - new_mouse_group_y) ** 2)

            # if the new group is closer to the centre than the middle point, skip it
            if middle_centre_distance > new_mouse_group_to_centre_distance:
                continue

            # using the external angle as the rotation angle
            flat_angle = 180 - (180 / mice_count)
            new_mouse_group_rotation = math.radians(flat_angle)

            new_group_positions.append((new_mouse_group_x, new_mouse_group_y,external_angle-new_mouse_group_rotation))
    return new_group_positions


prev_positions = group_positions
group_position_layers = [group_positions]
for i in range(mice_group_count):
    new_positions = make_group_positions(prev_positions, distance)
    group_position_layers.append(new_positions)
    prev_positions = new_positions

reverse = False
#occupied_positions = set()
reverse_positions = set()
forward_positions = set()
for i, group_positions in enumerate(group_position_layers):
    for group_position in group_positions:
        #if (round(group_position[0],2), round(group_position[1],2)) in occupied_positions:
        #    continue
        #occupied_positions.add((round(group_position[0],2), round(group_position[1],2)))
        if reverse:
            reverse_positions.add(group_position)
        else:
            forward_positions.add(group_position)
    reverse = not reverse
for x, y, rotation in forward_positions:
    canvas.append(draw.Use(forward_animation, x=x, y=y, transform=f"rotate({math.degrees(rotation)} {x} {y})"))
for x, y, rotation in reverse_positions:
    canvas.append(draw.Use(reverse_animation, x=x, y=y, transform=f"rotate({math.degrees(rotation)} {x} {y})"))


#canvas.append(draw.Circle(0, 0, 50, fill='red'))
#canvas.append(draw.Circle(0, 0, group_distance, fill='none', stroke='red'))

canvas.save_svg('mice.svg')
#canvas.save_html('mice.html')



