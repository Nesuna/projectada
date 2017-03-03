"""
Ananya Rajgarhia
1/20/17
NOTE: numericStringParser requires pyparsing (currently not using numericStringParser though)
Current features:
  - addition, subtraction, mod, division, multiplication, int division
  - repeat loops
  - break points THEY SEEM TO WORK!!
  - print statements work too
  - eval expr using eval and checking for valid syms only
  - saving and loading of up to 10 diff files (by using keyboard lel)
  - if statements
  - debug mode (using breaks)
  - TODO:
   - repeat var: (if var changes within the loop, doesn't affect repeat)
   - implement else statements 
   - general variables
   - while loops. ... ):
   - self-check on drawing game
   - functions -> does not need to support recursion :D
 
"""

# Begin writing interpreter for Adaas
from tkinter import *
# from Modules.numericStringParser import NumericStringParser 

# taken from http://www.kosbie.net/cmu/fall-14/15-112/notes/file-and-web-io.py
def readFile(filename, mode="rt"):
    # rt = "read text"
    with open(filename, mode) as fin:
        return fin.read()

# taken from http://www.kosbie.net/cmu/fall-14/15-112/notes/file-and-web-io.py
def writeFile(filename, contents, mode="wt"):
    # wt = "write text"
    with open(filename, mode) as fout:
        fout.write(contents)

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

    def save(self, ver=None):
        contents = self.get_text()
        if ver == None:
            writeFile("code.txt", contents)
        else:
            filename = "code%d.txt" % ver
            writeFile(filename, contents)

    def load(self, ver=None):
        if ver == None:
            contents = readFile("code.txt")
        else:
            filename = "code%d.txt" % ver
            contents = readFile(filename)
        self.text = list(contents)
        self.index = len(self.text)

# helper function that processes mathematical assignment expressions
# let var and val be lists that are all the vars in play
# var is a list of strs that are variable names
# vals is a list of values corresponding to the appropriate index of var
# i is the line number 
def eval_expr(data, expr, var, vals, i):

    try:
        elist = list(expr)
        offset = 0

        # fix formatting -> change % to %%
        for i in range(len(expr)):
            if expr[i] == "%":
                elist.insert(i + offset, "%")
                offset += 1
        expr = "".join(elist)

        for i in range(len(var)):
            if (var[i] in expr):
                temp = expr.replace(var[i], "%d")
                expr = temp % vals[i]
    except Exception as e:
        print("Error:", e)
        data.error = True
        data.err_msg = "invalid variable name - should be %s" % var
        data.err_line = i 
        return None

    try:
        safe_syms = "<>/*+-.()%="
        for c in expr:
            if not(c.isspace() or c.isalpha() or c.isdigit() or c in safe_syms):
                data.error = True
                data.err_msg = "math syntax error"
                data.err_line = i
                return None    
        
        return eval(expr)
    except:
        data.error = True
        data.err_msg = "math syntax error"
        data.err_line = i
        return None

# strip but doesn't strip the beginning because indents are important
def strip_end(s):
    slist = list(s)
    for i in range(len(s), 0, -1):
        if not(slist[i - 1].isspace()):
            break
    return "".join(slist[:i])

# returns list of split lines and new line number
# extracts indented body of code as in body of for loop/if statement etc.
def get_indent_body(data, code_lines, k):
    body = []
    while (k < len(code_lines) and len(code_lines[k]) > 0 
           and code_lines[k][0].isspace()):
        start = code_lines[k][0]
        if start == " ":
            code_lines[k] = code_lines[k][4:] # get rid of 4 tabbed spaces
        elif start == "\t":
            code_lines[k] = code_lines[k][1:]
        else:
            print(code_lines[k])
            raise Exception("you missed something")
        body += [strip_end(code_lines[k]), "\n"]
        k += 1
    return body, k

# gets rid of empty lines
def filter_space(code_lines, debug=False):

    filtered_code = []
    for i in range(len(code_lines)):
        line = code_lines[i]
        if not(line == "" or line.isspace() or line.startswith("#")):
            filtered_code.append(strip_end(line))

    # adds break statements between lines
    if debug:
        result = [filtered_code[0]]
        for i in range(1, len(filtered_code)):
            debug_line = "break"
            if line[0].isspace():
                for j in range(len(line)):
                    if not(line[j].isspace()):
                        break
                debug_line = line[:j] + debug_line
            result.append(debug_line)
            result.append(filtered_code[i])
            if (i == len(filtered_code) - 1):
                result.append(debug_line)
    else:
        result = filtered_code
    return result

"""
code: a multi-line string of "code" w/ the following constraints:
    -valid variable names include: x, y, color
    -valid function calls include: draw(x, y, color, angle)
    -valid commands: repeat <int>: 
    -mathematical operators supported: ^,+,-,/,| (integer division), *,%,abs, exp, 
                                       and sin, cos, tan (radians)
"""
def interpret(data, code, i=0, color="", repeated=0, x0=0, y0=0, x1=0, y1=0):

    code_lines = code.splitlines()
    n = len(code_lines)

    while (i < n):
        line = code_lines[i]
        # print("processing line:", line)
        if line.startswith("x"):
            # if you can't split, then there's a syntax error
            expr = line.split("<-")[1].strip()
            val = eval_expr(data, expr, ["x"], [x1], i)
            if val == None:
                data.error = True
                data.err_msg = "assignment error"
                data.err_line = i 
                return None
            x1 = val

        elif line.startswith("y"):
            # if you can't split, then there's a syntax error
            expr = line.split("<-")[1].strip()
            val = eval_expr(data, expr, ["y"], [y1], i)
            if val == None:
                data.error = True
                data.err_msg = "assignment error"
                data.err_line = i  
                return None # there was an error
            y1 = val

        elif line.startswith("color"):
            # if you can't split, then there's a syntax error
            if (len(line.split("<-")) < 2):
                data.error = True
                data.err_msg = "should be of the form \'color <- black\'"
                data.err_line = i
            color = line.split("<-")[1].strip() 

        elif line.startswith("draw"):
            if color != "none":
                data.to_draw.append((x0, y0, x1, y1, color, i))
            x0 = x1
            y0 = y1
        
        elif line.startswith("if"):
            cond = None
            try: 
                # get contents between parens
                start = line.find("(")
                end = line.find(")")
                expr = line[start + 1:end]
                #DEFINE VAR AND VAL
                cond = eval_expr(data, expr, ["x", "y"], [x1, y1], i)

            except Exception as e:
                print("here!")
                data.error = True
                data.err_msg = str(e)
                print(e)
                data.err_line = i 

            if (cond == None): 
                data.error = True
                data.err_msg = str("Condition not set")
                data.err_line = i 
                return 
            (body, k) = get_indent_body(data, code_lines, i + 1)
            if (cond):
                # (body, k) = get_indent_body(data, code_lines, i + 1)
                print(k)
                print("body: ", body)
                result = interpret(data, "".join(body), 0, color, 0, x0, y0, x1, y1)

                if result == None and data.error: #error occured
                    return 
                (_, break_called, x0, y0, x1, y1, color) = result
                if break_called:
                    # you might want to update the variables 
                    # frame is line number, color, #repeats, and coord vals
                    frame = (i, color, 0, x0, y0, x1, y1)
                    print("appending frame: ", frame)
                    data.frames.append(frame)
                    return (False, True, x0, y0, x1, y1, color)
            else:
                print("not cond")
            i = k - 1

        elif line.startswith("repeat"): 
            # get the number between the end of repeat and before the colon
            # 6 because 6 letters in repeat
            try:
                m = int(line.split(":")[0][len("repeat"):].strip())
            except Exception as e:
                data.error = True
                data.err_msg = str(e)
                data.err_line = i 
                return None
            
            print("before get_indent_body")
            print(i + 1)
            print(code_lines)
            body, k = get_indent_body(data, code_lines, i + 1)
            print("repeat loop body:\n", "".join(body))
            # print(k)
            # never entered the while loop
            if k == i + 1: 
                data.error = True
                data.err_msg = "no content to repeat\n\
(Hint: remember to indent the block\nyou would like to repeat)"
                data.err_line = k 
                return None

            # m - repeated to handle for breakpoints
            for j in range(m - repeated):
    
                if data.frames != []:
                    result = interpret(data, "".join(body), *data.frames.pop())    
                else: 
                    result = interpret(data, "".join(body), 0, color, 0, x0, y0, x1, y1)
                
                if result == None and data.error: # error occured
                    return 
                (terminated, break_called, x0, y0, x1, y1, color) = result
                if break_called:
                    
                    if j + 1 > m - repeated:
                        print("we should be exiting the loop")
                        i = k
    
                    # terminated keeps track of whether you've completed the inner loop or not
                    print("terminated: ", terminated)
                    if (terminated): repeated += 1
                    frame = (i, color, repeated, x0, y0, x1, y1)
                    print("appending frame: ", frame)
                    data.frames.append(frame)
                    return (False, True, x0, y0, x1, y1, color)
                

            i = k - 1
            print("i = %d" % k)

        elif line.startswith("print"):
            s = line[len("print("):]
            end = s.find(")")
            s = s[:end]
            variables = ["x", "y"]
            vals = [x1, y1]
            for j in range(len(variables)):
                var = variables[j]
                if var in s:
                    s = s.replace(var, "%d") % vals[j]
    
            data.print_string.append(s)

        elif line.startswith("break"):
            frame = (i + 1, color, 0, x0, y0, x1, y1)
            
            if (i + 1) == n:
                return (True, True, x0, y0, x1, y1, color)
            data.frames.append(frame)
            return (False, True, x0, y0, x1, y1, color)

        else:
            # print some exception
            print("error:", repr(line))
            data.error = True
            data.err_msg = "invalid starting keyword"
            data.err_line = i 
            return None
    
        i += 1

    return (True, False, x0, y0, x1, y1, color)

def draw_code(canvas, data):

    draw_window_height = data.height - data.draw_window_margin*2
    cx = data.draw_window_margin + data.draw_window_width/2
    cy = data.draw_window_margin + draw_window_height/2
    for obj in data.to_draw:
        (x0, y0, x1, y1, color, i) = obj
        try:
            # negating y to account for conversion to graphical coordinates
            # to cartesian coordinates
            canvas.create_line(x0 + cx,
                               -y0 + cy, 
                               x1 + cx, 
                               -y1 + cy, fill=color, width=5)
        except Exception as e:
            data.error = True
            data.err_msg = str(e)
            data.err_line = i 

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

def init_GUI(data):
    data.draw_window_margin = 20
    data.draw_window_width = data.width * 3/5
    data.draw_window_height = data.height - data.draw_window_margin*2
    data.margin = 10
    data.draw_window_cx = data.draw_window_margin + data.draw_window_width/2
    data.draw_window_cy = data.draw_window_margin + data.draw_window_height/2
    textx = data.draw_window_margin + data.draw_window_width + data.margin
    texty = data.draw_window_margin
    textw = (data.width - data.draw_window_width
             - data.draw_window_margin*2 - data.margin)
    texth = data.height - 2*data.draw_window_margin
    data.to_draw = []
    data.axes = False
    data.textbox = Textbox(textx, texty, textw, texth)


def init(data):
    init_GUI(data)
    data.nsp = NumericStringParser()
    data.debug_mode = False
    data.type_mode = False
    data.counter = 0
    data.frames = []
    data.print_string = [] # each string in this list should be separated by new line
    data.help = False
    data.error = False
    data.ver = None
    data.err_line = 0
    data.err_msg = ""
    data.code = """x <- -25
y <- 25
color <- none
draw
y <- -25
color <- black
draw
x<--25
y<-0
draw
x<--5
draw
y<-25
color<-none
draw
y<--25
color<-black
draw
x<-5
y<-25
color<-none
draw
y<--25
color<-blue
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
        valid = "\<-+#:()^*/%=" 
        if event.keysym == "Return":
            data.textbox.add_text("\n")
        elif event.keysym == "Tab":
            data.textbox.add_text("    ")
        elif event.keysym == "BackSpace":
            data.textbox.backspace()
        elif (event.char.isalpha() 
             or event.char.isdigit() 
             or event.char.isspace()
             or event.char in valid):
            data.textbox.add_text(event.char)

    elif event.keysym == "Return":
        # when you break and then recompile something weird happens
        data.error = False
        data.err_msg = ""
        data.code = data.textbox.get_text()
        data.to_draw = []
        data.frames = []
        data.print_string = []
        code_lines = filter_space(data.code.splitlines(), data.debug_mode)
        data.code = "\n".join(code_lines)
        interpret(data, data.code)
        print("frame post return: ", data.frames)

    # display axes
    elif event.char == "a":
        data.axes = not(data.axes)

    elif event.char == "d":
        data.debug_mode = not(data.debug_mode)

    elif event.char.isdigit():
        ver = int(event.char)
        if ver == 0:
            data.ver = None
        else:
            data.ver = int(event.char)
    # save code written
    elif event.char == "s":
        data.textbox.save(data.ver)
        print("data saved")

    # load previous code written
    elif event.char == "l":
        data.textbox.load(data.ver)
        print("data loaded")

    # help
    elif event.char == "h":
        data.help = True

    # continue after break point
    elif event.char == "c":
        # TODO: DO STACK TRACE OF RECURSIVE CALLS FOR FOR LOOP
        while len(data.frames) > 0:
            frame = data.frames.pop()
            print("frame:", frame)
            # transfer results from recursive call for next iteration
            result = interpret(data, data.code, *frame)
            if result == None: # an error occured
                data.frames = []
                return 
            (_, break_called, x0, y0, x1, y1, color) = result
            if break_called:
                print("frame post c: ", data.frames)
                return


def timerFired(data):
    data.counter += 1

def draw_screens(canvas, data):
    canvas.create_rectangle(data.draw_window_margin, data.draw_window_margin,
                            data.draw_window_margin + data.draw_window_width, 
                            data.height - data.draw_window_margin, width=3)
    data.textbox.draw(canvas, data.counter)

def redrawAll(canvas, data):

    draw_screens(canvas, data)

    if data.debug_mode:
        canvas.create_text(data.draw_window_margin + data.margin,
                           data.draw_window_margin + data.draw_window_height,
                           text="Debug Mode",
                           anchor=SW)
    if data.axes:
        draw_axes(canvas, data)
    
    if data.error:
        err_msg = "Error on line %d: %s" % (data.err_line, data.err_msg)
        canvas.create_text(data.draw_window_margin + data.margin, 
                           data.draw_window_margin + data.margin, 
                           text=err_msg, anchor=NW)
    else:
        draw_code(canvas, data)
        p = "\n".join(data.print_string)
        canvas.create_text(data.draw_window_margin + data.margin,
                           data.draw_window_margin + data.margin,
                           text=p, anchor=NW)

def run(width=1000, height=600):
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

run(500, 400)

