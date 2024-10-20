import math
from typing import List

import drawsvg as draw

debug_figures = False
# Mice starting circle
debug_figures_starting_circle = False
remove_duplicate_lines = False
# Mice
mice_count = 9  # How many mice
# step_size = 10 # How much each mouse moves in each step
target_distance_scale = 0.05  # How much each mouse moves towards the target
distance = 500  # Distance between the mice and 0,0
n_steps = 10  # Number of steps
rotation = 0  # Rotation offset for mice positioning
mice_group_count = 5  # Number of mice groups
offset_x = 0
offset_y = 0

# Canvas
resolution = 4000
canvas = draw.Drawing(resolution, resolution, origin="center",
                      animation_config=draw.types.SyncedAnimationConfig(
                          # Animation configuration
                          duration=1)
                      )

# set the background color
canvas.append(draw.Rectangle(-resolution / 2, -resolution / 2, resolution, resolution, fill='white'))

# Animation
animation_duration_ms = 1000  # Duration of the animation in milliseconds
begin_ms = 0  # Start time of the animation in milliseconds
duration_ms = 1  # Duration of each step in milliseconds
infinite_repeat = True  # Repeat the animation infinitely
fill = 'freeze'  # Fill the final state of the animation


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
        target_x, target_y = self.get_target().get_position()
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
        # print(f"({self.x:.2f}, {self.y:.2f}) -> ({self.new_x:.2f}, {self.new_y:.2f})")

    def update_position(self):
        self.x = self.new_x
        self.y = self.new_y



def generate_mice_lines(canvas, mice: List[Mouse], begin_ms: float, dur_ms: float, reverse: bool) -> draw.Lines:
    mouse_lines = []
    target_lines = []
    for mouse in mice:
        x1, y1 = mouse.get_position()
        x2, y2 = mouse.get_target().get_position()
        x3, y3 = mouse.new_x, mouse.new_y
        x4, y4 = mouse.get_target().new_x, mouse.get_target().new_y
        mouse_lines.extend([x1, y1, x2, y2])
        target_lines.extend([x3, y3, x4, y4])

        # Fade in the lines
        # line1.append_anim(draw.Animate(attributeName='d', to=line2.args["d"], begin=f"{begin_ms}ms", dur=f"{1000}ms", fill='freeze',repeatCount='indefinite'))
        # canvas.append(line1)
        # canvas.append(line2)
    # Fade in the lines
    # lines = draw.Lines(*mouse_lines, close=True, fill='none', stroke='black',opacity=0.0)
    # lines = []
    # lines.append_anim(draw.Animate(attributeName='opacity', to='1.0', begin=f"{begin_ms}ms", dur=f"{dur_ms}ms", fill='freeze'))

    # Moving lines
    mouse_lines = draw.Lines(*mouse_lines, close=True, fill='none', stroke='black')
    target_lines = draw.Lines(*target_lines, close=True, fill='none', stroke='black')

    if reverse:
        # mouse_lines.append_anim(draw.Animate(attributeName='d', to=target_lines.args["d"], begin=f"{begin_ms}ms", dur=f"{animation_duration_ms}ms", fill='freeze',repeatCount='indefinite'))
        mouse_lines.add_key_frame(0, d=target_lines.args["d"])
        mouse_lines.add_key_frame(1, d=mouse_lines.args["d"])
        lines = mouse_lines
    else:
        # target_lines.append_anim(draw.Animate(attributeName='d', to=mouse_lines.args["d"], begin=f"{begin_ms}ms", dur=f"{animation_duration_ms}ms", fill='freeze',repeatCount='indefinite'))
        target_lines.add_key_frame(0, d=mouse_lines.args["d"])
        target_lines.add_key_frame(1, d=target_lines.args["d"])
        lines = target_lines

    # lines = draw.Lines(*mouse_lines, close=True, fill='none', stroke='black')
    # target_lines = draw.Lines(*target_lines, close=True, fill='none', stroke='black')
    # target_lines.append_anim(draw.AnimateTransform(path=lines.args["d"], begin=f"{1000}ms", dur=f"{1000}ms", fill='freeze',repeatCount='indefinite'))

    # target_lines.append_anim(draw.Animate(attributeName='d', to=lines.args["d"], begin=f"{begin_ms}ms", dur=f"{1000}ms", fill='freeze',repeatCount='indefinite'))
    # lines.add_key_frame(0,d=target_lines.args["d"])
    # lines.add_key_frame(1,d=lines.args["d"])
    # lines.append_anim(draw.Animate(attributeName='d', to=target_lines, begin=f"{begin_ms}ms", dur=f"{dur_ms}ms", fill='freeze'))
    # lines.append_anim(draw.AnimateTransform(attributeName='transform', type='rotate',from_or_values="0 85 85", to="360 85 85", begin=f"{begin_ms}ms", dur=f"{dur_ms}ms", fill='freeze', repeatCount='indefinite'))
    return lines


def create_mice(centre_xy: tuple[float, float], n: int, distance: float, rotation: float, reverse: bool = False) -> \
List[Mouse]:
    new_mice = []
    circle_centre_x, circle_centre_y = centre_xy
    if debug_figures:
        # draw cirlce
        canvas.append(draw.Circle(circle_centre_x, circle_centre_y, distance, fill='none', stroke='black'))
    for i in range(n):
        angle = rotation + i * 2 * math.pi / n
        x = circle_centre_x + distance * math.cos(angle)
        y = circle_centre_y + distance * math.sin(angle)
        new_mice.append(Mouse(x, y))
    if reverse:
        new_mice.reverse()
    for i in range(n):
        print(f"Mouse {i}: ({new_mice[i].x:.2f}, {new_mice[i].y:.2f})")
        new_mice[i].set_target(new_mice[(i + 1) % n])
    return new_mice


def create_mice_group_layer(mice_groups: tuple[List[List[Mouse]], bool], reverse: bool = False) -> tuple[
    List[List[Mouse]], bool]:
    new_mice_groups = []
    for mice_group, prev_reverse in mice_groups:
        average_x = 0
        average_y = 0
        for mouse in mice_group:
            x, y = mouse.get_position()
            average_x += x / len(mice_group)
            average_y += y / len(mice_group)
        if debug_figures:
            # draw the centre point
            canvas.append(draw.Circle(average_x, average_y, 5, fill='green'))
        for mouse in mice_group:
            # new_mice_group.append(Mouse(mouse.x, mouse.y))
            x, y = mouse.get_position()
            target_x, target_y = mouse.get_target().get_position()

            # calculate the middle point between the mouse and the target
            middle_x = (x + target_x) / 2
            middle_y = (y + target_y) / 2

            # calculate the distance between the mouse and the target
            d = mouse.get_target_distance()

            # calculate the distance between the middle point to the centre of the next group
            h = math.sqrt(distance ** 2 - (d / 2) ** 2)

            if debug_figures:
                # draw a circle at the middle point
                canvas.append(draw.Circle(middle_x, middle_y, distance, fill='none', stroke='blue'))

            if debug_figures:
                # draw a line from the average point to the middle point
                canvas.append(draw.Line(average_x, average_y, middle_x, middle_y, stroke='blue'))

            # Calculate the angle between the average point and the middle point
            external_angle = math.atan2(middle_y - average_y, middle_x - average_x)
            external_angle_deg = math.degrees(external_angle)

            # Calculate the new position of the mouse using the h distance
            new_mouse_group_x = middle_x + h * math.cos(external_angle)
            new_mouse_group_y = middle_y + h * math.sin(external_angle)

            middle_centre_distance = math.sqrt((offset_x - middle_x) ** 2 + (offset_y - middle_y) ** 2)
            new_mouse_group_to_centre_distance = math.sqrt(
                (offset_x - new_mouse_group_x) ** 2 + (offset_y - new_mouse_group_y) ** 2)

            # if the new group is closer to the centre than the middle point, skip it
            if middle_centre_distance > new_mouse_group_to_centre_distance:
                continue

            if debug_figures:
                # draw the centre point
                canvas.append(draw.Circle(new_mouse_group_x, new_mouse_group_y, 5, fill='red'))

            # using the external angle as the rotation angle
            flat_angle = 180 - (180 / mice_count)
            new_mouse_group_rotation = math.radians(flat_angle)
            print(f"Group: ({new_mouse_group_x:.2f}, {new_mouse_group_y:.2f})")
            new_mice_group = create_mice((new_mouse_group_x, new_mouse_group_y), mice_count, distance,
                                         external_angle - new_mouse_group_rotation, reverse=reverse)
            new_mice_groups.append((new_mice_group, reverse))

    return new_mice_groups


reverse_mice = True
# Calculate the offset angle required to make the shape flat
# flat_angle = abs(90 - (180 / mice_count))
# rotation += math.radians(flat_angle)
mice = create_mice((offset_x, offset_y), mice_count, distance, rotation, reverse=reverse_mice)
mice_groups = [(mice, reverse_mice)]
reverse_mice = not reverse_mice

# for each mouse get its xy and its targets xy

prev_layer = mice_groups
for i in range(mice_group_count):
    new_layer = create_mice_group_layer(prev_layer, reverse=reverse_mice)
    mice_groups.extend(new_layer)
    prev_layer = new_layer
    reverse_mice = not reverse_mice
step_delay = animation_duration_ms / n_steps
animation_frames = []
for i in range(n_steps):
    frame = []
    for mice_group, reverse in mice_groups:
        for mouse in mice_group:
            step_size = mouse.get_target_distance() * target_distance_scale
            mouse.move(step_size)

        frame.append(generate_mice_lines(canvas, mice_group, begin_ms, duration_ms, reverse=reverse))
        # frame.append(generate_mice_lines(canvas, mice_group,begin_ms + i * step_delay, duration_ms,reverse=reverse))
        for mouse in mice_group:
            mouse.update_position()
    animation_frames.append(frame)

# lines.append_anim(draw.Animate(attributeName='opacity', to='1.0', begin=f"{begin_ms}ms", dur=f"{duration_ms}ms", fill='freeze'))
# remove duplicate lines:

for idx, frame in enumerate(animation_frames):
    if remove_duplicate_lines:
        seen = []
        to_delete = []
        for i in range(len(frame)):
            if frame[i] in seen:
                to_delete.append(i)
            else:
                seen.append(frame[i])
        to_delete.sort(reverse=True)
        for i in to_delete:
            print(f"Deleting {i}")
            del frame[i]

    for lines in frame:
        canvas.append(lines)

canvas.save_svg('mice.svg')
# canvas.save_html('mice.html')



