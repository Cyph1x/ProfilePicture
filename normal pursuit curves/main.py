import math
from typing import List

import PIL.ImagePalette
import drawsvg as draw
from drawsvg import Lines, Group
import threading
import lottie
import os

debug_figures = False
# Mice starting circle
debug_figures_starting_circle = True
debug_figures_position_group_dot = True
remove_duplicate_lines = True

# Mice
mice_count = 3 # How many mice
density_factor = 1 # will scale the line count and distance scale by this factor
target_distance_scale = density_factor * 0.035 # How much each mouse moves towards the target
distance = 200 # Distance between the mice and 0,0
step_count = int(50/density_factor) # Number of steps
rotation = 0 # Rotation offset for mice positioning
mice_group_count = 5 # Number of mice groups
reverse = False
cross_hatch = False # Cross hatch the lines


# Animation
enable_animation = False # Enable or disable the animation
animation_duration_ms = 1000 # Duration of the animation in milliseconds
begin_ms = 0 # Start time of the animation in milliseconds
infinite_repeat = True # Repeat the animation infinitely

# Export options
export_svg = True # Export the animation as an SVG file
export_png = True # Export the first frame as a PNG file
export_mp4 = False # Export the animation as an MP4 file
export_gif = False # Export the animation as a GIF file
export_frames = False # Export the animation as individual frames
export_spritesheet = False # Export the animation as a spritesheet
export_webp = False # Export the animation as a webp file (requires export_frames to be True)
gif_from_frames = False # Create a GIF from the frames (requires export_frames to be True)

fps = 30

# Canvas
target_resolution = 1000
line_width_scale = 0.002
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

line_width = resolution*line_width_scale

canvas = draw.Drawing(resolution, resolution, origin="center",
        animation_config=draw.types.SyncedAnimationConfig(
            # Animation configuration
            duration=animation_duration_ms/1000,  # Seconds
            #show_playback_progress=True,
            #show_playback_controls=True
            )
        )


#set the background color
canvas.append(draw.Rectangle(-resolution/2, -resolution/2, resolution, resolution, fill='none'))

class Line(draw.DrawingBasicElement):
    '''A line element that uses the SVG <line> tag.

    The endpoints of this custom Line element can be animated.  This is a workaround because `drawsvg.Line`
    cannot be animated.'''
    TAG_NAME = 'line'

    def __init__(self, x1, y1, x2, y2, **kwargs):
        super().__init__(x1=x1, y1=y1, x2=x2, y2=y2, **kwargs)

class PolyLine(draw.DrawingBasicElement):
    '''A line element that uses the SVG <line> tag.

    The endpoints of this custom Line element can be animated.  This is a workaround because `drawsvg.Line`
    cannot be animated.'''
    TAG_NAME = 'polyline'

    def __init__(self, points, **kwargs):
        super().__init__(points=points, **kwargs)

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

    def get_rounded_position(self):
        # using the canvas resolution there should be the same number of pixels between each mouse
        unit_count = resolution / group_distance
        x = round(self.x * unit_count) / unit_count
        y = round(self.y * unit_count) / unit_count
        return (x, y)

    def get_new_position(self):
        return (self.new_x, self.new_y)

    def get_rounded_new_position(self):
        # using the canvas resolution there should be the same number of pixels between each mouse
        unit_count = resolution / group_distance
        x = round(self.new_x * unit_count) / unit_count
        y = round(self.new_y * unit_count) / unit_count

        return (x, y)

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
        self.stroke_linecap = "round"
        self.stroke_linejoin = "round"
        self.shape_rendering = "geometricPrecision"
        self.make_individual_lines = False
        self.make_polylines = True
        self.use_keyframes = False

    def generate_mice_lines(self,g: draw.Group=None):
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
                x1, y1 = mouse.get_rounded_position()
                x2, y2 = mouse.get_target().get_rounded_position()
                x3, y3 = mouse.get_rounded_new_position()
                x4, y4 = mouse.get_target().get_rounded_new_position()
                if self.make_individual_lines:
                    mouse_lines.append((x1, y1, x2, y2))
                    target_lines.append((x3, y3, x4, y4))
                elif self.make_polylines:
                    mouse_lines.extend([str(x1), str(y1), str(x2), str(y2)])
                    target_lines.extend([str(x3), str(y3), str(x4), str(y4)])
                else:
                    mouse_lines.extend([x1, y1, x2, y2])
                    target_lines.extend([x3, y3, x4, y4])

            repeat_count = 'indefinite' if self.repeat else 1

            if self.make_individual_lines:
                lines = []
                for i in range(self.n):
                    line = Line(*mouse_lines[i], stroke=self.colour, stroke_width=self.line_width,
                                opacity=self.opacity, stroke_linecap=self.stroke_linecap, stroke_linejoin=self.stroke_linejoin, shape_rendering=self.shape_rendering)
                    if enable_animation:
                        if self.reverse:
                            if self.use_keyframes:
                                line.add_key_frame(0, x1=mouse_lines[i][0],
                                                   y1=mouse_lines[i][1], x2=mouse_lines[i][2], y2=mouse_lines[i][3])
                                line.add_key_frame(animation_duration_ms / 1000, x1=target_lines[i][0],
                                                   y1=target_lines[i][1], x2=target_lines[i][2], y2=target_lines[i][3])
                            else:
                                line.append_anim(draw.Animate(attributeName='x1',
                                                              from_or_values=mouse_lines[i][0],
                                                              to=target_lines[i][0], begin=f"{self.begin_ms}ms",
                                                              dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                                line.append_anim(draw.Animate(attributeName='y1',
                                                              from_or_values=mouse_lines[i][1],
                                                              to=target_lines[i][1], begin=f"{self.begin_ms}ms",
                                                              dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                                line.append_anim(draw.Animate(attributeName='x2',
                                                              from_or_values=mouse_lines[i][2],
                                                              to=target_lines[i][2], begin=f"{self.begin_ms}ms",
                                                              dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                                line.append_anim(draw.Animate(attributeName='y2',
                                                              from_or_values=mouse_lines[i][3],
                                                              to=target_lines[i][3], begin=f"{self.begin_ms}ms",
                                                              dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))

                        else:
                            if self.use_keyframes:
                                line.add_key_frame(0, x1=target_lines[i][0],
                                                   y1=target_lines[i][1], x2=target_lines[i][2], y2=target_lines[i][3])
                                line.add_key_frame(animation_duration_ms / 1000, x1=mouse_lines[i][0],
                                                   y1=mouse_lines[i][1], x2=mouse_lines[i][2], y2=mouse_lines[i][3])

                            else:
                                line.append_anim(draw.Animate(attributeName='x1',
                                                              from_or_values=target_lines[i][0],
                                                              to=mouse_lines[i][0], begin=f"{self.begin_ms}ms",
                                                              dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                                line.append_anim(draw.Animate(attributeName='y1',
                                                              from_or_values=target_lines[i][1],
                                                              to=mouse_lines[i][1], begin=f"{self.begin_ms}ms",
                                                              dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                                line.append_anim(draw.Animate(attributeName='x2',
                                                              from_or_values=target_lines[i][2],
                                                              to=mouse_lines[i][2], begin=f"{self.begin_ms}ms",
                                                              dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                                line.append_anim(draw.Animate(attributeName='y2',
                                                              from_or_values=target_lines[i][3],
                                                              to=mouse_lines[i][3], begin=f"{self.begin_ms}ms",
                                                              dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                        #line.add_key_frame(0, x1=target_lines[i][0], y1=target_lines[i][1], x2=target_lines[i][2], y2=target_lines[i][3])
                            #line.add_key_frame(animation_duration_ms/1000, x1=mouse_lines[i][0], y1=mouse_lines[i][1], x2=mouse_lines[i][2], y2=mouse_lines[i][3])
                    lines.append(line)
            elif self.make_polylines:
                if self.make_polylines:
                    mouse_lines = PolyLine(" ".join(mouse_lines), fill='none', stroke=self.colour, stroke_width=self.line_width, opacity=self.opacity, stroke_linecap=self.stroke_linecap, stroke_linejoin=self.stroke_linejoin, shape_rendering=self.shape_rendering)
                    target_lines = PolyLine(" ".join(target_lines), fill='none', stroke=self.colour, stroke_width=self.line_width, opacity=self.opacity, stroke_linecap=self.stroke_linecap, stroke_linejoin=self.stroke_linejoin, shape_rendering=self.shape_rendering)

                if self.reverse:
                    if enable_animation:
                        mouse_lines.append_anim(
                            draw.Animate(attributeName='points', from_or_values=mouse_lines.args["points"], to=target_lines.args["points"], begin=f"{self.begin_ms}ms",
                                         dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                    lines = mouse_lines
                else:
                    if enable_animation:
                        target_lines.append_anim(
                            draw.Animate(attributeName='points', from_or_values=target_lines.args["points"], to=mouse_lines.args["points"], begin=f"{self.begin_ms}ms",
                                         dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                    lines = target_lines
            else:

                mouse_lines = draw.Lines(*mouse_lines, close=True, fill='none', stroke=self.colour, stroke_width=line_width, opacity=self.opacity, stroke_linecap=self.stroke_linecap, stroke_linejoin=self.stroke_linejoin, shape_rendering=self.shape_rendering)
                target_lines = draw.Lines(*target_lines, close=True, fill='none', stroke=self.colour, stroke_width=line_width, opacity=self.opacity, stroke_linecap=self.stroke_linecap, stroke_linejoin=self.stroke_linejoin, shape_rendering=self.shape_rendering)



                if self.reverse:
                    if enable_animation:
                        mouse_lines.append_anim(
                            draw.Animate(attributeName='d', from_or_values=mouse_lines.args["d"], to=target_lines.args["d"], begin=f"{self.begin_ms}ms",
                                         dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                    lines = mouse_lines
                else:
                    if enable_animation:
                        target_lines.append_anim(
                            draw.Animate(attributeName='d', from_or_values=target_lines.args["d"], to=mouse_lines.args["d"], begin=f"{self.begin_ms}ms",
                                         dur=f"{animation_duration_ms}ms", repeatCount=repeat_count))
                    lines = target_lines
            if self.make_individual_lines:
                for line in lines:
                    g.append(line)
            else:
                g.append(lines)
            for mouse in new_mice:
                mouse.update_position()
        return g

class MouseGroup:
    def __init__(self):
        self.mice: List[MouseLines] = []

    def AddMouseLines(self, mouse_lines: MouseLines):
        self.mice.append(mouse_lines)

    def generate_mice_lines(self,g: draw.Group = None):
        if g is None:
            g = draw.Group()
        #for i in range(len(self.mice)):
        #    self.mice[len(self.mice)-1-i].generate_mice_lines(g)
        for mouse in self.mice:
            mouse.generate_mice_lines(g)
        return g



forward_animation_group = MouseGroup()
forward_animation = MouseLines(mice_count, step_count, distance, rotation,reverse=False,colour='black',line_width=line_width,opacity=1,begin_ms=begin_ms)
forward_animation_group.AddMouseLines(forward_animation)
forward_animation = MouseLines(mice_count, step_count, distance, rotation,reverse=False,colour='white',line_width=line_width/2,opacity=1,begin_ms=begin_ms)
forward_animation_group.AddMouseLines(forward_animation)

reverse_animation_group = MouseGroup()
reverse_animation = MouseLines(mice_count, step_count, distance, rotation,reverse=True,colour='black',line_width=line_width,opacity=1,begin_ms=begin_ms)
reverse_animation_group.AddMouseLines(reverse_animation)
reverse_animation = MouseLines(mice_count, step_count, distance, rotation,reverse=True,colour='white',line_width=line_width/2,opacity=1,begin_ms=begin_ms)
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

occupied_positions = set()
reverse_positions = set()
forward_positions = set()
for i, group_positions in enumerate(group_position_layers):
    for group_position in group_positions:
        if (round(group_position[0],2), round(group_position[1],2)) in occupied_positions and remove_duplicate_lines:
            continue
        occupied_positions.add((round(group_position[0],2), round(group_position[1],2)))
        if reverse:
            reverse_positions.add(group_position)
        else:
            forward_positions.add(group_position)
    reverse = not reverse


forward_animation_group_generated = forward_animation_group.generate_mice_lines()
reverse_animation_group_generated = reverse_animation_group.generate_mice_lines()

def check_circle_within_bounds(x: float, y: float, radius: float):
    max_x = radius+x
    min_x = -radius+x
    max_y = radius+y
    min_y = -radius+y
    if min_x > resolution/2 or max_x < -resolution/2:
        return False
    if min_y > resolution/2 or max_y < -resolution/2:
        return False
    return True
for x, y, rotation in forward_positions:
    if not check_circle_within_bounds(x, y, distance):
        continue
    canvas.append(draw.Use(forward_animation_group_generated, x=x, y=y, transform=f"rotate({math.degrees(rotation)} {x} {y})"))
    if cross_hatch:
        canvas.append(
            draw.Use(reverse_animation_group_generated, x=x, y=y, transform=f"rotate({math.degrees(rotation)} {x} {y})"))
for x, y, rotation in reverse_positions:
    if not check_circle_within_bounds(x, y, distance):
        continue
    canvas.append(draw.Use(reverse_animation_group_generated, x=x, y=y, transform=f"rotate({math.degrees(rotation)} {x} {y})"))
    if cross_hatch:
        canvas.append(
            draw.Use(forward_animation_group_generated, x=x, y=y, transform=f"rotate({math.degrees(rotation)} {x} {y})"))


#canvas.append(draw.Circle(0, 0, 50, fill='red'))
#canvas.append(draw.Circle(0, 0, group_distance, fill='none', stroke='red'))

if export_svg:
    print("Rendering SVG")
    canvas.save_svg('mice.svg')

if export_png:
    print("Rendering PNG")
    canvas.rasterize('mice.png')

if export_frames:
    import shutil
    print("Rendering Frames")
    #save all the frames
    result = canvas.as_animation_frames(fps=fps)
    if os.path.exists("frames"):
        shutil.rmtree("frames")
    os.makedirs("frames", exist_ok=True)

    for i, frame in enumerate(result):
        print(f"Rendering frame {i:05d}")
        frame.rasterize(f"frames/frame_{i:05d}.png")
    print("All frames rendered")

if export_spritesheet:
    print("Rendering Spritesheet")
    canvas.as_spritesheet('spritesheet.png', fps=fps,row_length=10, verbose=True)

if export_mp4:
    print("Rendering MP4")
    canvas.save_mp4('mice.mp4', fps=fps,verbose=True)

if export_gif:
    print("Rendering GIF")
    canvas.save_gif('mice.gif', fps=fps,verbose=True)

if gif_from_frames and export_frames:
    from PIL import Image
    print("Rendering GIF from frames")
    frames = os.listdir("frames")
    frames.sort()
    images = []
    for frame in frames:
        images.append(Image.open(f"frames/{frame}"))

    assert len(images) > 0, "No frames found"

    common_colors = {}
    for i in range(1, len(images)):
        colors = images[i].getcolors(99999)
        for count, color in colors:
            if color in common_colors:
                common_colors[color] += count
            else:
                common_colors[color] = count
    # sort the colors by count
    common_colors = sorted(common_colors.items(), key=lambda x: x[1], reverse=True)

    max_size = 768 # Bytes
    palette = []
    for color, count in common_colors:
        if len(palette) + len(color) > max_size:
            break
        palette.extend(color)


    images[0].save('mice_from_frames.gif',
                   format="GIF",
                   disposal=2, #after each image, clear to the background color
                   save_all=True,
                   append_images=images[1:],
                   duration=1000/fps,
                   loop=0,
                   palette = PIL.ImagePalette.ImagePalette(mode="RGBA", palette=palette)
                   )


if export_webp and export_frames:
    from PIL import Image
    print("Rendering WebP from frames")

    frames = os.listdir("frames")
    frames.sort()
    images = []
    for frame in frames:
        images.append(Image.open(f"frames/{frame}"))

    assert len(images) > 0, "No frames found"

    images[0].save('mice_from_frames.webp',
                   format="WEBP",
                   save_all=True,
                   append_images=images[1:],
                   background=[0,0,0,0],
                   duration=1000 / fps,
                   loop=0,
                   alpha_quality=10,
                   method=6,
                   quality=40,
                   lossless=False
                   )

"""

from lottie.exporters import exporters
from lottie.importers import importers
from lottie.utils.stripper import float_strip, heavy_strip
import os
print("Start Lottie conversion")


infile = 'mice.svg'
suf = os.path.splitext(infile)[1][1:]
for p in importers:
    if suf in p.extensions:
        importer = p
        break
assert importer
outfile = 'mice.webp'
exporter = exporters.get_from_filename(outfile)

print(f"Loading \"{infile}\" into lottie converter")

an = importer.process(infile)

print(f"Loaded \"{infile}\" into lottie converter")
fps = 30
an.frame_rate = fps
an.out_point = int(fps*animation_duration_ms/1000)

print(f"Converting to lottie file \"{outfile}\"")

exporter.process(an, outfile)

print(f"Converted to lottie file \"{outfile}\"")
"""



