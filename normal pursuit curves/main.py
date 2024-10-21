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

# Animation
enable_animation = True# Enable or disable the animation
animation_duration_ms = 1000 # Duration of the animation in milliseconds
begin_ms = 0 # Start time of the animation in milliseconds
infinite_repeat = True # Repeat the animation infinitely
cross_hatch = False # Cross hatch the lines

# Canvas
target_resolution = 2000
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
resolution = group_distance * 2

#scale to the target resolution
if 'target_resolution' in locals():
    scale = target_resolution / resolution
    resolution *= scale
    distance *= scale
    group_distance *= scale
    start_x *= scale
    start_y *= scale

line_width = 0.001*resolution

canvas = draw.Drawing(resolution, resolution, origin="center",
        animation_config=draw.types.SyncedAnimationConfig(
            # Animation configuration
            duration=animation_duration_ms/1000,  # Seconds
            #show_playback_progress=True,
            #show_playback_controls=True)
            )
        )


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

class MouseLines:

    def __init__(self,n: int, n_steps: int, distance: float, rotation: float, reverse: bool, colour: str, line_width: float, opacity=0.5,begin_ms: float = begin_ms, repeat: bool=infinite_repeat):
        self.n = n
        self.n_steps = n_steps
        self.distance = distance
        self.rotation = rotation
        self.reverse = reverse
        self.colour = colour
        self.line_width = line_width
        self.opacity = opacity
        self.begin_ms = begin_ms
        self.repeat = repeat
        self.new_mice = []

    def generate_mice_lines(self,g: draw.Group=None,t=0):
        new_mice = []
        if g is None:
            g = draw.Group()
        if debug_figures and debug_figures_starting_circle:
            # Define the circle radius
            g.append(draw.Circle(0, 0, distance, fill='none', stroke='black'))
        for i in range(self.n):
            angle = self.rotation + i * 2 * math.pi / self.n
            # angle = random.uniform(0, 2 * math.pi)
            x = 0 + distance * math.cos(angle)
            y = 0 + distance * math.sin(angle)
            new_mice.append(Mouse(x, y))
        if self.reverse:
            new_mice.reverse()
        for i in range(self.n):
            print(f"Mouse {i}: ({new_mice[i].x:.2f}, {new_mice[i].y:.2f})")
            new_mice[i].set_target(new_mice[(i + 1) % self.n])

        for i in range(self.n_steps):
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
                #interpolate the x1,y1,x2,y2,x3,y3,x4,y4
                x1,y1 = x1 + (x3-x1)*t, y1 + (y3-y1)*t
                x2,y2 = x2 + (x4-x2)*t, y2 + (y4-y2)*t

                mouse_lines.extend([x1, y1, x2, y2])
                target_lines.extend([x3, y3, x4, y4])

            mouse_lines = draw.Lines(*mouse_lines, close=True, fill='none', stroke=self.colour, stroke_width=line_width,
                                     opacity=self.opacity)
            target_lines = draw.Lines(*target_lines, close=True, fill='none', stroke=self.colour, stroke_width=line_width,
                                      opacity=self.opacity)

            repeat_count = 'indefinite' if self.repeat else 1

            if self.reverse:
                if enable_animation:
                    mouse_lines.append_anim(
                        draw.Animate(attributeName='d', to=target_lines.args["d"], begin=f"{self.begin_ms}ms",
                                     dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                lines = mouse_lines
            else:
                if enable_animation:
                    target_lines.append_anim(
                        draw.Animate(attributeName='d', to=mouse_lines.args["d"], begin=f"{self.begin_ms}ms",
                                     dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                lines = target_lines

            g.append(lines)
            for mouse in new_mice:
                mouse.update_position()
        return g

class MouseGroup:
    def __init__(self):
        self.mice: List[MouseLines] = []

    def AddMouseLines(self, mouse_lines: MouseLines):
        self.mice.append(mouse_lines)

    def generate_mice_lines(self,g: draw.Group = None,t: float = 0):
        if g is None:
            g = draw.Group()
        for mouse in self.mice:
            mouse.generate_mice_lines(g,t)
        return g

forward_animation_group = MouseGroup()
forward_animation = MouseLines(mice_count, step_count, distance, rotation,reverse=False,colour='black',line_width=line_width,opacity=0.5,begin_ms=begin_ms)
forward_animation_group.AddMouseLines(forward_animation)
forward_animation = MouseLines(mice_count, step_count, distance, rotation,reverse=False,colour='white',line_width=line_width,opacity=0.5,begin_ms=begin_ms)
forward_animation_group.AddMouseLines(forward_animation)

reverse_animation_group = MouseGroup()
reverse_animation = MouseLines(mice_count, step_count, distance, rotation,reverse=True,colour='black',line_width=line_width,opacity=0.5,begin_ms=begin_ms)
reverse_animation_group.AddMouseLines(reverse_animation)
reverse_animation = MouseLines(mice_count, step_count, distance, rotation,reverse=True,colour='white',line_width=line_width,opacity=0.5,begin_ms=begin_ms)
reverse_animation_group.AddMouseLines(reverse_animation)


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


forward_animation_group_generated = forward_animation_group.generate_mice_lines()
reverse_animation_group_generated = reverse_animation_group.generate_mice_lines()
for x, y, rotation in forward_positions:
    canvas.append(draw.Use(forward_animation_group_generated, x=x, y=y, transform=f"rotate({math.degrees(rotation)} {x} {y})"))
    if cross_hatch:
        canvas.append(
            draw.Use(reverse_animation_group_generated, x=x, y=y, transform=f"rotate({math.degrees(rotation)} {x} {y})"))
for x, y, rotation in reverse_positions:
    canvas.append(draw.Use(reverse_animation_group_generated, x=x, y=y, transform=f"rotate({math.degrees(rotation)} {x} {y})"))
    if cross_hatch:
        canvas.append(
            draw.Use(forward_animation_group_generated, x=x, y=y, transform=f"rotate({math.degrees(rotation)} {x} {y})"))


#canvas.append(draw.Circle(0, 0, 50, fill='red'))
#canvas.append(draw.Circle(0, 0, group_distance, fill='none', stroke='red'))

canvas.save_svg('mice.svg')

fps = 30
duration = animation_duration_ms / 1000
time_step = 1 / fps
steps = int(duration / time_step)
def gen_frame(t):
    t = t / duration
    t = t - int(t)
    print(t)
    canvas = draw.Drawing(resolution, resolution, origin="center")
    canvas.append(draw.Rectangle(-resolution / 2, -resolution / 2, resolution, resolution, fill='None'))
    forward_animation_group_generated = forward_animation_group.generate_mice_lines(t=t)
    reverse_animation_group_generated = reverse_animation_group.generate_mice_lines(t=t)
    for x, y, rotation in forward_positions:
        canvas.append(draw.Use(forward_animation_group_generated, x=x, y=y,
                               transform=f"rotate({math.degrees(rotation)} {x} {y})"))
        if cross_hatch:
            canvas.append(
                draw.Use(reverse_animation_group_generated, x=x, y=y,
                         transform=f"rotate({math.degrees(rotation)} {x} {y})"))
    for x, y, rotation in reverse_positions:
        canvas.append(draw.Use(reverse_animation_group_generated, x=x, y=y,
                               transform=f"rotate({math.degrees(rotation)} {x} {y})"))
        if cross_hatch:
            canvas.append(
                draw.Use(forward_animation_group_generated, x=x, y=y,
                         transform=f"rotate({math.degrees(rotation)} {x} {y})"))
    print(f"Saving frame {i}")
    #canvas.save_png(f"mice_{i:04d}.png")
    return canvas

#with draw.frame_animate_video('mice.mp4', gen_frame,duration=0.05) as frame:
    #for i in range(steps):
        #frame.draw_frame(i)

#canvas.as_mp4('mice.mp4',fps=10,verbose=True)
#canvas.save_html('mice.html')



