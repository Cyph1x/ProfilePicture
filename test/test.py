import drawsvg as draw
duration=1
d = draw.Drawing(400, 200, origin='center',
        animation_config=draw.types.SyncedAnimationConfig(
            # Animation configuration
            duration=duration,  # Seconds
            show_playback_progress=True,
            show_playback_controls=True))

class Line(draw.DrawingBasicElement):
    '''A line element that uses the SVG <line> tag.

    The endpoints of this custom Line element can be animated.  This is a workaround because `drawsvg.Line`
    cannot be animated.'''
    TAG_NAME = 'line'

    def __init__(self, x1, y1, x2, y2, **kwargs):
        super().__init__(x1=x1, y1=y1, x2=x2, y2=y2, **kwargs)

#d.append(draw.Rectangle(-200, -100, 400, 200, fill='#eee'))  # Background
#d.append(draw.Circle(0, 0, 40, fill='green'))  # Center circle
# Animation
circle = draw.Circle(0, 0, 0, fill='gray')  # Moving circle
circle.add_key_frame(duration*0.0, cx=-100, cy=0,    r=0)
circle.add_key_frame(duration*0.2, cx=0,    cy=-100, r=40)
circle.add_key_frame(duration*0.4, cx=100,  cy=0,    r=0)
circle.add_key_frame(duration*0.6, cx=0,    cy=100,  r=40)
circle.add_key_frame(duration*0.8, cx=-100, cy=0,    r=0)
d.append(circle)
r = draw.Rectangle(0, 0, 0, 0, fill='silver')  # Moving square
r.add_key_frame(duration*0.0, x=-100, y=0,       width=0,  height=0)
r.add_key_frame(duration*0.2, x=0-20, y=-100-20, width=40, height=40)
r.add_key_frame(duration*0.4, x=100,  y=0,       width=0,  height=0)
r.add_key_frame(duration*0.6, x=0-20, y=100-20,  width=40, height=40)
r.add_key_frame(duration*0.8, x=-100, y=0,       width=0,  height=0)
d.append(r)
#make a line
l = Line(0, 0, 100, 100, stroke='white', stroke_width=2)  # Moving line

#l.add_key_frame(duration*0.0, stroke='black')
#l.add_key_frame(duration*0.2, stroke='white')
#l.add_key_frame(duration*0.4, stroke='black')
#l.add_key_frame(duration*0.6, stroke='white')
#l.add_key_frame(duration*0.8, stroke='black')

#l.add_key_frame(duration*0.0, d="M0,100 L100,100")
#l.add_key_frame(duration*0.2, d="M100,100 L100,100")
#l.add_key_frame(duration*0.4, d="M100,100 L100,0")
#l.add_key_frame(duration*0.6, d="M100,100 L0,0")
#l.add_key_frame(duration*0.8, d="M100,0 L0,0")



l.add_key_frame(duration*0.0, x1=0,   y1=100, x2=100, y2=100)
l.add_key_frame(duration*0.2, x1=100, y1=100, x2=100, y2=100)
l.add_key_frame(duration*0.4, x1=100, y1=100, x2=100, y2=0  )
l.add_key_frame(duration*0.6, x1=100, y1=100, x2=0,   y2=0  )
l.add_key_frame(duration*0.8, x1=100, y1=0,   x2=0,   y2=0  )

d.append(l)

#make a polyline
#pl = PolyLine("0,100 100,100 100,0 0,0", stroke='white', stroke_width=2,fill='none')  # Moving line
#pl.add_key_frame(duration*0.0, points=[0,100, 100,100, 100,0, 0,0])
#pl.add_key_frame(duration*0.2, points=[100,100, 100,100, 100,0, 0,0])
#pl.add_key_frame(duration*0.4, points=[100,100, 100,100, 100,0, 100,0])
#pl.add_key_frame(duration*0.6, points=[100,100, 100,100, 100,0, 0,0])
#pl.add_key_frame(duration*0.8, points=[100,0, 100,0, 100,0, 0,0])

#d.append(pl)


# Changing text
draw.native_animation.animate_text_sequence(
        d,
        [0, 2, 4, 6],
        ['0', '1', '2', '3'],
        30, 0, 1, fill='yellow', center=True)

# Save as a standalone animated SVG or HTML
d.save_svg('playback-controls.svg')
d.save_html('playback-controls.html')

# Display in Jupyter notebook
#d.display_image()  # Display SVG as an image (will not be interactive)
#d.display_iframe()  # Display as interactive SVG (alternative)
#d.as_gif('orbit.gif', fps=10)  # Render as a GIF image, optionally save to file
d.as_mp4('orbig.mp4', fps=60, verbose=True)  # Render as an MP4 video, optionally save to file
#d.as_spritesheet('orbit-spritesheet.png', row_length=10, fps=3)  # Render as a spritesheet
d.display_inline()  # Display as interactive SVG