# Ananya Rajgarhia
# 1/20/17

# Begin writing interpreter for Adaas
from tkinter import *

class Textbox(object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = []
        self.clicked = False
        self.index=0

    def in_bounds(self, x, y):
        if ((self.x <= x <= self.x + self.width) and
                 (self.y <= y <= self.y + self.height)):
            self.clicked = True
            return True
        self.clicked = False
        return False
    
    def add_text(self, c):
        self.text.insert(self.index, c)
        self.index+=1

    def move_index(self, delta):
        if self.index + delta < 0 or self.index + delta >= len(self.text):
            return
        self.index += delta

    def backspace(self):
        if len(self.text) > 0:
            self.text.pop()

    def draw(self, canvas, counter=0):
        canvas.create_rectangle(self.x, self.y, 
                                self.x + self.width, 
                                self.y +self.height, 
                                width=3)
        margin = 10
        if counter % 10 < 5 and self.clicked:
            
            self.text.append("|")
            canvas.create_text(self.x + margin, self.y + margin, 
                text="".join(self.text), 
                anchor=NW, font="14")
            self.text.pop()
        else:
            canvas.create_text(self.x + margin, self.y + margin, 
                text="".join(self.text), 
                anchor=NW)

    def get_text(self):
        return "".join(self.text)


"""
Input is a multi-line string of "code" w/ the following constraints:
    -valid variable names include: x, y, color, (angle, r)
    -valid function calls include: draw(x, y, color, angle), 
                                   check_background_color()
    -valid commands: repeat <int> times,
                     if/else 
"""

#TODO: SUPPORT IF/IF-ELSE; WHILE LOOPS (ugh); HINT SYSTEM; line number errors;
# syntax highlighting
# window size bug
# fontsize variability
# draw image/copy image functionality
def interpret(data, code, x0=0, y0=0, x1=0, y1=0):

    color = ""
    i = 0
    # print("starting code:", code)
    code_lines = code.splitlines()
    n = len(code_lines)

    while (i < n):
        line = code_lines[i]
        print("processing line:", line)
        if line.startswith("x"):
            # if you can't split, then there's a syntax error
            expr = line.split("->")[1].strip()
            components = expr.split("+")
            if len(components) < 2:
                x1 = int(components[0])
            else: 
                if components[0].strip() != "x": 
                    data.error = True
                    data.err_msg = "invalid variable name - should be x"
                    return
                x1 = x1 + int(components[1].strip())

        elif line.startswith("y"):
            # if you can't split, then there's a syntax error
            expr = line.split("->")[1].strip()

            components = expr.split("+")
            if len(components) < 2:
                y1 = int(components[0])
            else: 
                if components[0].strip() != "y": 
                    data.error = True
                    data.err_msg = "invalid variable name - should be y"
                    return
                y1 = y1 + int(components[1].strip())

        elif line.startswith("color"):
            # if you can't split, then there's a syntax error
            if (len(line.split("->")) < 2):
                data.error = True
                data.err_msg = "Syntax error: should be of the form \'color -> black\'"
            color = line.split("->")[1].strip() 

        # TODO: (maybe) elif line.startswith("angle"):

        elif line.startswith("draw"):
            # print(x0, y0, x1, y1)
            if color != "none":
                data.to_draw.append((x0, y0, x1, y1, color))
            x0 = x1
            y0 = y1
            
        elif line.startswith("repeat"): 
            # get the number between the end of repeat and before the colon
            m = int(line.split(":")[0][6:].strip())

            # if not(line.startswith("\t") or line.startswith("    ") 
            # or line.startswith("  ")):
            #     print(repr(line)) 
            #     data.error = True
            #     data.err_msg = "No content to repeat"
            #     return 

            body = []
            k = i + 1
            while (k < len(code_lines) and len(code_lines[k]) > 0 
                   and code_lines[k][0].isspace()):
                body += [code_lines[k].strip(), "\n"]
                k += 1

            for j in range(m):    
                (x0, y0, x1, y1) = interpret(data, "".join(body), 
                                              x0, y0, x1, y1)
            i = k - 1
            # continue

        elif line == "" or line.isspace() or line.startswith("#"):
            print("I'M EMPTY!")
            pass

        else:
            # print some exception
            print("error:", repr(line))
            data.error = True
            data.err_msg = "Invalid starting keyword"
            return
        i += 1

    return (x0, y0, x1, y1)

def draw_code(canvas, data):

    draw_window_height = data.height - data.draw_window_margin*2
    cx = data.draw_window_margin + data.draw_window_width/2
    cy = data.draw_window_margin + draw_window_height/2
    for obj in data.to_draw:
        (x0, y0, x1, y1, color) = obj
        try:
            # negating y to account for conversion to graphical coordinates
            # to cartesian coordinates
            canvas.create_line(x0 + cx,
                               -y0 + cy, 
                               x1 + cx, 
                               -y1 + cy, fill=color, width=5)
        except Exception as e:
            data.error = True
            data.err_msg = "Error: " + str(e)

def draw_axes(canvas, data):

    
    offset = data.draw_window_margin
    draw_window_height = data.height - offset*2
    cx = data.draw_window_margin + data.draw_window_width/2
    cy = data.draw_window_margin + draw_window_height/2
    
    # x axis
    canvas.create_line(offset, 
                       cy,
                       offset + data.draw_window_width,
                       cy)

    # divide into chunks of 10 rounded down to the nearest even
    interval = 10
    increments_x = data.draw_window_width//interval//2*2 
    marker_radius = 5
    cx = data.draw_window_margin + data.draw_window_width/2
    cy = data.draw_window_margin + draw_window_height/2
    for i in range(1, int(increments_x//2 + 1)):
        mx = cx + interval*i
        mx_n = cx - interval*i
        my_top = cy - marker_radius
        my_bot = cy + marker_radius
        canvas.create_line(mx, my_top, mx, my_bot)
        canvas.create_line(mx_n, my_top, mx_n, my_bot)

    # draw y axis
    canvas.create_line(cx, data.draw_window_margin, cx, 
                       data.draw_window_margin + draw_window_height)

    increments_y = draw_window_height//interval//2*2
    for i in range(1, int(increments_y//2 + 1)):
        mx_l = cx - marker_radius
        mx_r = cx + marker_radius
        my = cy + interval*i
        my_n = cy - interval*i
        canvas.create_line(mx_l, my, mx_r, my)
        canvas.create_line(mx_l, my_n, mx_r, my_n)

def init(data):
    data.counter = 0
    data.to_draw = []
    data.axes = False
    data.draw_window_margin = 20
    data.draw_window_width = data.width*3/5
    data.draw_window_height = data.height - data.draw_window_margin*2
    data.margin = 10
    data.draw_window_cx = data.draw_window_margin + data.draw_window_width/2
    data.draw_window_cy = data.draw_window_margin + data.draw_window_height/2
    textx = data.draw_window_margin + data.draw_window_width + data.margin
    texty = data.draw_window_margin
    textw = data.width - data.draw_window_width -data.draw_window_margin*2 - data.margin
    texth = data.height - 2*data.draw_window_margin
    data.textbox = Textbox(textx, texty, textw, texth)
    data.code = ""
    data.error = False
    data.err_msg = ""
    data.code = """x -> -25
y -> 25
color -> none
draw
y -> -25
color -> black
draw
x->-25
y->0
draw
x->-5
draw
y->25
color->none
draw
y->-25
color->black
draw
x->5
y->25
color->none
draw
y->-25
color->blue
draw
"""
    interpret(data, data.code)

def mousePressed(event, data):
    # use event.x and event.y
    if data.textbox.in_bounds(event.x, event.y):
        data.type_mode = True
    else:
        data.type_mode = False

def keyPressed(event, data):
    # use event.char and event.keysym
    
    if data.type_mode:
        valid = "->+-#:" 
        if event.keysym == "Return":
            data.textbox.add_text("\n")
        elif event.keysym == "Tab":
            data.textbox.add_text("    ")
        elif event.keysym == "BackSpace":
            data.textbox.backspace()
        # elif event.keysym == "Right":
        #     print("RIGHT")
        #     data.textbox.move_index(1)
        # elif event.keysym == "Left":
        #     print("LEFT")
        #     data.textbox.move_index(-1)
        elif (event.char.isalpha() 
             or event.char.isdigit() 
             or event.char.isspace()
             or event.char in valid):
            data.textbox.add_text(event.char)

    elif event.keysym == "Return":
        data.error = False
        data.err_msg = ""
        data.code = data.textbox.get_text()
        data.to_draw = []
        interpret(data, data.code)

    elif event.char == "a":
        data.axes = not(data.axes)

def timerFired(data):
    data.counter += 1

def redrawAll(canvas, data):
    
    if data.axes:
        draw_axes(canvas, data)
    canvas.create_rectangle(data.draw_window_margin, data.draw_window_margin,
                            data.draw_window_margin + data.draw_window_width, 
                            data.height - data.draw_window_margin, width=3)
    data.textbox.draw(canvas, data.counter)
    if data.error:
        canvas.create_text(data.draw_window_margin + data.margin, 
                           data.draw_window_margin + data.margin, 
                           text=data.err_msg, anchor=NW)
    else:
        draw_code(canvas, data)

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(800, 500)

