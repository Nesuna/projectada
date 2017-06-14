"""
Ananya Rajgarhia
1/20/17
NOTE: numericStringParser requires pyparsing (currently not using numericStringParser though)
Ask Sarah:
  - what do you think syntax for function should be
  - how git (like if I wanna pull/merge the UI changes)
Current features:
  - addition, subtraction, mod, division, multiplication, int division
  - repeat loops
  - break points
  - print statements work too
  - eval expr using eval and checking for valid syms only
  - saving and loading of up to 10 diff files (by using keyboard lel)
  - if/else statements
  - debug mode (using breaks)
  - general variables
  - while loops
  - functions -> when you return you need to skip the rest of the fn  
  - TODO:
   - adjust pen width
   - super clear error handling
   - range -> actually implement it
   - confirm that debug-mode works correctly with fns** (it doesn't. lmao)
   - convert everything to data
   - self-check on drawing game
   - error handling <- uncomment all the excepts
   - time.sleep -> ("wait")
 
"""
# Begin writing interpreter for Adaas <- saada
#from tkinter import *
#from Modules.numericStringParser import NumericStringParser 
from tkinter.scrolledtext import *
import tkinter
import string
import math
import random
from tkinter import filedialog


# Begin writing interpreter for Adaas <- saada
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

# helper function that replaces variable name in expression 
# with the variables actual value
# variables:dict<str, _> - maps variable names to vals
# expr:str - expression containing some or no var names

def replace_vars_with_values(data, variables, expr):
    elist = list(expr)
    offset = 0

    for i in range(len(expr)):
        if expr[i] == "%":
            elist.insert(i + offset, "%")
            offset += 1
    expr = "".join(elist)
    sorted_by_len = sorted(variables, key=lambda s: -len(s)) # longest first
    for var in sorted_by_len:
        if var in expr:
            num_occurences = expr.count(var)
            val = variables[var]
            if type(val) == str:
                temp = expr.replace(var, "%s")
            else:
                temp = expr.replace(var, "%r")
            expr = temp % ((val,)*num_occurences)
    return expr

# line: 5, lineLength: 10 x+y

def test_replace_vars_with_vals(): 
    print("Testing replace_vars_with_vals...")
    class Struct(): pass
    data = Struct()
    variables = {"x": 10, "y":20, "z": 30, "color": "blue", "color2": None}
    assert(replace_vars_with_values(data, variables, "") == "")
    assert(replace_vars_with_values(data, variables, "x") == "10")
    assert(replace_vars_with_values(data, variables, "z") == "30")
    assert(replace_vars_with_values(data, variables, "color") == "\'blue\'")
    assert(replace_vars_with_values(data, variables, "x + y") == "10 + 20")
    assert(replace_vars_with_values(data, variables, "x + z*y") == "10 + 30*20")
    assert(replace_vars_with_values(data, variables, "color2") == 'None')
    assert(replace_vars_with_values(data, variables, "color color2") == 
                                                                    "\'blue\' None")
    assert(replace_vars_with_values(data, variables, "42") == "42")
    print("...passed!")

# helper function that processes mathematical assignment expressions
# variables is a mapping of var names to vals
# i is the line number of code being evaluated
# if expr doesn't result in a valid expr, None is returned and the error flag
#   is set
def eval_expr(data, variables, expr, line_num):
    assert(type(variables)==dict)
    
    if (expr == "") : return ""
    expr = replace_vars_with_values(data, variables, expr)
    if not containsDigit(expr): return expr
    print("165", expr)
    try:
        safe_syms = "<>/*+-.()%="
        for c in expr:
            if not(c.isspace() or c.isalpha() or c.isdigit() or c in safe_syms):   
                data.error = True
                data.err_msg = "expression contains invalid symbol: %s" % expr
                data.err_line = line_num
                return None    
        if ("range" in expr): 
            return list(eval(expr))
        return eval(expr)
    except Exception as e:
        data.error = True
        data.err_msg = "error evaluating expression: %s" % expr
        data.err_line = line_num
        return None

def test_eval_expr():
    print("Testing eval_expr...")
    class Struct(): pass
    data = Struct()
    data.fns = dict()
    variables = {"x": 10, "y":20, "z": 30, "t": -5}
    assert(eval_expr(data, variables, "x + y * z / t", 0) == -110)
    assert(eval_expr(data, variables, "(x + x + x)*5", 0) == 150)
    assert(eval_expr(data, variables, "x**2 + y**2", 0) == 500)
    assert(eval_expr(data, variables, "0", 0) == 0)
    assert(eval_expr(data, variables, "x+=0",0) == None) # == None)
    assert(eval_expr(data, variables, "(y+z)*(x+y)", 0) == 1500)
    assert(eval_expr(data, variables, "", 0) == "")
    print("...passed!")

# strip but doesn't strip the beginning because indents are important
def strip_end(s):
    slist = list(s)
    i = 0
    for i in range(len(s), 0, -1):
        if not(slist[i - 1].isspace()):
            break
    return "".join(slist[:i])


def test_strip_end():
    print("Testing strip_end...")
    assert(strip_end("") == "")
    assert(strip_end("asdfsdfsdf      ") == "asdfsdfsdf")
    assert(strip_end("asdf\t   \n \n") == "asdf")
    assert(strip_end("hi this is text with stuff\t \t \t ") == 
                     "hi this is text with stuff")
    assert(strip_end("\t    we don't touch stuff in the beginning  ") ==
                     "\t    we don't touch stuff in the beginning")
    assert(strip_end("how perfect there's nothing to strip") ==
                     "how perfect there's nothing to strip")
    print("...passed!")

def filter_comments(code_lines):
    result = []
    for i in range(len(code_lines)):
        line = code_lines[i]
        if not line.startswith("#"):
            result.append(line)
    return result

# returns list of split lines and new line number
# extracts indented body of code as in body of for loop/if statement etc.
# returns list of lines of code as well as the new line number
def get_indent_body(data, code_lines, k):
    body = []
    while (k < len(code_lines) and code_lines[k][0].isspace()):
        start = code_lines[k][0]
        if start == " ":
            code_lines[k] = code_lines[k][4:] # get rid of 4 tabbed spaces
        elif start == "\t":
            code_lines[k] = code_lines[k][1:]
        if not code_lines[k][0] == "#":
            body += [code_lines[k], "\n"] # there used to be strip_end call here
        k += 1
    return (body, k)

def test_get_indent_body():
    print("Testing get_indent_body...")
    class Struct(): pass
    data = Struct()
    code_lines = ["#this is code", "x<-10", "    x<-10"]
    assert(get_indent_body(data, code_lines, 2) == (["x<-10", "\n"], 3))
    assert(get_indent_body(data, code_lines, 1) == ([], 1))
    code_lines = ["repeat 5:", "    x<-x+10", "\ty<-y+10", "\tdraw", 
                  "# more stuff"]
    assert(get_indent_body(data, code_lines, 1) == 
                          (["x<-x+10", "\n", "y<-y+10", "\n", "draw", "\n"], 4))
    code_lines =  ["repeat 5:", "    x<-x+10", "\ty<-y+10", "\tdraw", 
                  "# more stuff", "\ty<-y+10", "\tdraw"]
    assert(get_indent_body(data ,code_lines, 5) == (["y<-y+10", "\n", "draw", "\n"], 7))
    print("...passed!")

# gets rid of empty lines, lines with comments
# inserts break points if debug mode is on
# code_lines is a list
# returns a list
def filter_space(code_lines, debug=False):

    filtered_code = []
    ln_map = []
    for i in range(len(code_lines)):
        line = code_lines[i]
        if not(line == "" or line.isspace() or line.startswith("#")):
            filtered_code.append(strip_end(line))
            ln_map.append(i + 1)

    # adds break statements between lines
    if debug and len(filtered_code) > 0:
        result = [filtered_code[0]] 
        for i in range(1, len(filtered_code)):
            debug_line = "break"
            line = filtered_code[i]
            if line[0].isspace():
                for j in range(len(line)):
                    if not(line[j].isspace()):
                        break
                debug_line = line[:j] + debug_line
            result.append(debug_line)
            result.append(filtered_code[i])
            # edge case, add break after last line as well
            if (i == len(filtered_code) - 1):
                result.append(debug_line)
    else:
        result = filtered_code
    return result, ln_map

def test_filter_space():
    print("Testing filter_space...")
    code_lines = ["", "", "", "code", "code", "", "code", ""]
    code_lines1 = [" ", "    ", "        ", "code", "  ", "   ", "  ", "", 
                   "code"]
    code_lines2 = ["repeat 5:", "   ", "    x<-x+10", "\ty<-y+10", 
                                "\tdraw", "# more stuff", "\ty<-y+10", "\tdraw",
                                "", "# this is the end of stuff"]
    # assert(filter_space(code_lines) == ["code", "code", "code"])
    # assert(filter_space(code_lines1) == ["code", "code"])
    # assert(filter_space(code_lines2) == ["repeat 5:", "    x<-x+10", "\ty<-y+10", 
    #                             "\tdraw", "\ty<-y+10", "\tdraw"])
    # assert(filter_space(code_lines, True) == ["code", "break", "code", "break", 
    #                                     "code", "break"])
    # assert(filter_space(code_lines2, True) == ['repeat 5:', '    break', 
    #     '    x<-x+10', '\tbreak', '\ty<-y+10', '\tbreak', '\tdraw', '\tbreak', 
    #     '\ty<-y+10', '\tbreak', '\tdraw', '\tbreak'])

# checks if there's a fn name in the expr
def containsFunction(functions, expr):
    for fn_name in functions:
        if fn_name in expr:
            return True
    return False

# finds index of closing paren given index of opening paren
def getMatchingClosingParen(expr, i=0):
    count = 0
    for j in range(i, len(expr)):
        if expr[j] == "(":
            count += 1
        if expr[j] == ")":
            count -= 1
        if count == 0:
            return j 
    return i 

# gets contents between parentheses
# does not include parentheses themselves
# takes in optional starting index of left parenthesis 
# o.w. assumes left paren at index 0
def get_paren_contents(expr, i=0):
    lparen_i = expr.find("(", i)
    rparen_i = getMatchingClosingParen(expr, lparen_i)
    return expr[lparen_i+1:rparen_i]

def test_get_paren_contents():
    print("Testing get_paren_contents...")
    assert(get_paren_contents("hi(these are the contents)") == "these are the contents")
    assert(get_paren_contents("(((yo)))") == "((yo))")
    assert(get_paren_contents("(((yo)), (hi))", 9) == "hi")
    print("...passed!")

def replace_functions_with_values(data, functions, variables, line, color, x0, y0, x1, y1, depth=0):

    sorted_by_len = sorted(functions, key=lambda s: -len(s)) # longest first
    for fn_name in sorted_by_len:
        i = line.find(fn_name)
        while (i != -1): # replace all instances of the function name in the expr
            # current logic assumes no parentheses are used in args
            lparen_i = line.find("(", i)
            rparen_i = getMatchingClosingParen(line, lparen_i)
            name = line[:lparen_i].strip()
            vals = get_paren_contents(line, lparen_i)
            if vals == "":
                vals = []
            else:
                vals = [elem.strip() for elem in vals.split(",")] 
                tempvals = []
                for expr in vals:
                    if (containsFunction(data.fns, expr)):
                        tempvals.append(replace_functions_with_values(data, functions, variables, expr, color, x0, y0, x1, y1))
                    else:
                        tempvals.append(expr)

                
                # vals = [replace_functions_with_values(data, functions, variables, expr, color, x0, y0, x1, y1) if containsFunction(functions, expr) else expr for expr in vals]
                vals = [eval_expr(data, variables, expr, i) for expr in tempvals]
            (_, args, body) = functions[fn_name]
            f_variables = dict()
            f_variables["x"] = variables["x"]
            f_variables["y"] = variables["y"]
            f_variables["color"] = variables["color"]
            for j in range(len(vals)):
                var_name = args[j]
                f_variables[var_name] = vals[j]
            # 0, color, 0, x0, y0, x1, y1
            result = interpret(data, body, f_variables, 0, color, 0, x0, y0, x1, y1, depth=depth+4)
            if result == None:
                return
            (_, _, _, x0, y0, x1, y1, color, _) = result
            variables["x"] = f_variables["x"]
            variables["y"] = f_variables["y"]
            variables["color"] = f_variables["color"]
            line = (line[:i] + "%r" + line[rparen_i+1:]) % f_variables["return"]
            i = line.find(fn_name)
    return line

# checks if there are any numbers in the expr
def containsDigit(s):
    for c in s:
        if c.isdigit():
            return True
    return False

def get_str_contents(s):
    start = s.find("\"")
    end = s.find("\"", start + 1)
    if end == -1:
        return None
    return s[start+1:end]

def test_get_str_contents():
    print("testing get_str_contents...")
    assert(get_str_contents("hi this is a string \"and you want this stuff\"") == "and you want this stuff")
    assert(get_str_contents("a\"\"b") == "")
    assert(get_str_contents("a\"b\"c") == "b")
    assert(get_str_contents("\"asdf\"") == "asdf")
    assert(get_str_contents("asdf\"asdf") == None)
    print("...passed!")


"""
code: a multi-line string of "code"
variables: a dict mapping var name (str) to value
i: line number
color: string indicating color for line
repeated: number of iterations of for loop completed
x0, y0, x1, y1: coordinates for line
fn: are you inside a fn rn?
"""
# frame = (variables, i, color, repeated, x0, y0, x1, y1, fn, ret)
def interpret(data, code, variables, i=0, color="", repeated=0, x0=0, y0=0, 
              x1=0, y1=0, depth=0):

    code_lines = code.splitlines()
    n = len(code_lines)
    while (i < n):
        line = code_lines[i]
        print("i: ", i)
        print("processing line:", line)
        
        if "<-" in line:
            if (len(line.split("<-")) < 2):
                data.error = True
                data.err_msg = "should be of the form \'variable_name <- value\'"
                data.err_line = i

            (var, expr) = (line.split("<-")[0].strip(), line.split("<-")[1].strip())
            expr = replace_functions_with_values(data, data.fns, variables, expr, color, x0, y0, x1, y1)
            if "\"" in expr:
                print("this is unprocessed", repr(expr))
                val = get_str_contents(expr)
                print("THIS IS THE COLOR", repr(val))
                if var == "x" or var == "y":
                    data.error = True
                    data.err_line = i
                    data.err_msg = "x and y must be numbers"
                    return None
                if var == "color":
                    color = val
                variables[var] = val
            else:
                print("367 expr", expr)
                res = eval_expr(data, variables, expr, i)
                print("res", res)
                if res == None:
                    data.err_line = i + data.err_line + 1
                    return 
                variables[var] = res
                if var == "x":
                    x1 = res
                elif var == "y":
                    y1 = res
                elif var == "color":
                    print("setting the color here!")
                    color = res
                    print("this is the color", color)
                    print("this is the color repr", repr(color))

        elif line.startswith("draw") and line[len("draw"):] == "":
            if color != "none":
                data.to_draw.append((x0, y0, x1, y1, color, i))
            x0 = x1
            y0 = y1
        
        elif line.startswith("if"):
            cond = None
            try: 
                # get contents between parens <- you can make that a helper function
                start = line.find("(")
                # revline = line[::-1]
                # end = len(line) - revline.find(")") - 1
                expr = get_paren_contents(line, start)
                expr = replace_functions_with_values(data, data.fns, variables, expr, color, x0, y0, x1, y1)
                cond = eval_expr(data, variables, expr, i)

            except Exception as e:
                data.error = True
                data.err_msg = str(e)
                data.err_line = i 

            if (cond == None): 
                data.error = True
                data.err_msg = str("Condition not set")
                data.err_line = i 
                return 
            (body, k) = get_indent_body(data, code_lines, i + 1)
            
            else_exists = False
            else_body = []
            if (k < n and code_lines[k].startswith("else")) or (data.debug_mode and k+1 < n and code_lines[k+1].startswith("else")):
                else_exists = True
                offset = int(data.debug_mode)
                (else_body, k) = get_indent_body(data, code_lines, k + 1 + offset) 
            
            if (cond):

                if data.frames != []:
                    result = interpret(data, "".join(body), *data.frames.pop(), depth=depth+4)    
                else: 
                    result = interpret(data, "".join(body), variables, 0, color,
                                       0, x0, y0, x1, y1, depth+4)

                if result == None and data.error: 
                    #error occured
                    data.err_line = i + data.err_line + 1
                    return 
                (returned, terminated, break_called, x0, y0, x1, y1, color, variables) = result
                if returned:
                    return (False, False, True, x0, y0, x1, y1, color, variables)
                if break_called:
                    # frame is line number, color, #repeats, and coord vals
                    if terminated:
                        frame = (variables, k, color, 0, x0, y0, x1, y1)
                    else:
                        frame = (variables, i, color, 0, x0, y0, x1, y1)
                    # print("434 appending frame: ", frame)
                    data.frames.append(frame)
                    return (False, False, True, x0, y0, x1, y1, color, variables)
            elif (else_exists):
                if data.frames != []:
                    result = interpret(data, "".join(else_body), *data.frames.pop(), depth=depth+4)    
                else: 
                    result = interpret(data, "".join(else_body), variables, 0, color,
                                       0, x0, y0, x1, y1, depth+4)
                
                if result == None and data.error: #error occured
                    data.err_line = i + data.err_line + 1
                    return 
                (returned, terminated, break_called, x0, y0, x1, y1, color, variables) = result
                if returned:
                    return (True, False, True, x0, y0, x1, y1, color, variables)
                if break_called: # can't hit both break and return
                    # frame is line number, color, #repeats, and coord vals
                    if terminated:
                        frame = (variables, k, color, 0, x0, y0, x1, y1)
                    else:
                        frame = (variables, i, color, 0, x0, y0, x1, y1)
                   
                    # print("appending frame: ", frame)
                    data.frames.append(frame)
                    return (False, False, True, x0, y0, x1, y1, color, variables)
        
            i = k - 1 # minus 1 because you increment i at the end
        elif line.startswith("while"):
            cond = None
            try: 
                # get contents between parens
                start = line.find("(")
                expr = get_paren_contents(line, start)
                # expr = line[start + 1:end]
                print("468 expr", expr)
                expr = replace_functions_with_values(data, data.fns, variables, expr, color, x0, y0, x1, y1)
                cond = eval_expr(data, variables, expr, i)

            except Exception as e:
                data.error = True
                data.err_msg = str(e)
                print(e)
                data.err_line = i 

            (body, k) = get_indent_body(data, code_lines, i + 1)

            while (cond or repeated):
                if data.frames != []:
                    result = interpret(data, "".join(body), *data.frames.pop())    
                else: 
                    result = interpret(data, "".join(body), variables, 0, color,
                                       0, x0, y0, x1, y1)
                
                if result == None and data.error: # error occured
                    data.err_line = i + data.err_line + 1
                    return None

                (returned, terminated, break_called, x0, y0, x1, y1, color, variables) = result
                if returned:
                    return (True, False, True, x0, y0, x1, y1, color, variables)
                if break_called:
                    # terminated keeps track of whether you've completed 
                    # the inner code of the loop
                    if not cond and terminated: # this is the final iter of loop
                        i = k
                    frame = (variables, i, color, int(not(terminated)), x0, y0, x1, y1)
                    print("appending frame in while: ", frame)
                    data.frames.append(frame)
                    return (False, False, True, x0, y0, x1, y1, color, variables)
                expr = replace_functions_with_values(data, data.fns, variables, expr, color, x0, y0, x1, y1)
                cond = eval_expr(data, variables, expr, i)

        elif line.startswith("repeat"): 
            # get the number between the end of repeat and before the colon
            try:
                expr = line.split(":")[0][len("repeat"):].strip()

            except Exception as e:
                data.error = True
                data.err_msg = str(e)
                data.err_line = i 
                return None

            if data.to_repeat == None:
                expr = replace_functions_with_values(data, data.fns, variables, expr, color, x0, y0, x1, y1)
                m = eval_expr(data, variables, expr, i)
                if m < 0:
                    data.error = True
                    data.err_msg = "repeat value must be nonnegative"
                    data.err_line = i
                    return None
                data.to_repeat = m
            

            body, k = get_indent_body(data, code_lines, i + 1)
            # print("repeat loop body:\n", "".join(body))
            # print(k)
            # never entered the while loop
            if k == i + 1: 
                data.error = True
                data.err_msg = "no content to repeat\n\
(Hint: remember to indent the block\nyou would like to repeat)"
                data.err_line = k 
                return None

            # data.to_repeat - repeated to handle for breakpoints
            for j in range(data.to_repeat - repeated):
                temp_repeat = data.to_repeat
                data.to_repeat = None
                if data.frames != []:
                    # print(data.frames)
                    frame = data.frames.pop()
                    # print("550 frame: ", frame)
                    result = interpret(data, "".join(body), *(frame), depth=depth+4)   
                else: 
                    result = interpret(data, "".join(body), variables, 0, color, 0, x0, y0, x1, y1, depth+1)
                data.to_repeat = temp_repeat
                if result == None and data.error: # error occured
                    data.err_line = i + data.err_line + 1
                    return 
                (returned, terminated, break_called, x0, y0, x1, y1, color, variables) = result
                if returned:
                    return (True, False, True, x0, y0, x1, y1, color, variables)
                if break_called:
                    if j + 1 > data.to_repeat - repeated:
                        i = k
                        data.to_repeat = None
    
                    # terminated keeps track of whether you've completed the inner loop or not
                    if (terminated): repeated += 1
                    frame = (variables, i, color, repeated, x0, y0, x1, y1)
                    # print("appending frame: ", frame)
                    data.frames.append(frame)
                    return (False, False, True, x0, y0, x1, y1, color, variables)
                
            data.to_repeat = None
            i = k - 1

        elif line.startswith("print"):
            s = line[len("print("):]
            revs = s[::-1]
            end = len(s) - revs.find(")") - 1 # finds right most paren (
            s = s[:end]

            if "\"" in s:
                s = get_str_contents(s)
            else:
                s = replace_functions_with_values(data, data.fns, variables, s, color, x0, y0, x1, y1)
                s = replace_vars_with_values(data, variables, s)
                s = str(eval_expr(data, variables, s, i))
            data.print_string.append(s)

        elif line.startswith("break"):
            frame = (variables, i + 1, color, 0, x0, y0, x1, y1)
            
            if (i + 1) == n:
                return (False, True, True, x0, y0, x1, y1, color, variables)
            # print("595 appending frame: ", frame)
            data.frames.append(frame)
            return (False, False, True, x0, y0, x1, y1, color, variables)

        elif line.startswith("def"):
            try:

                lparen_i = line.find("(") 
                rparen_i = getMatchingClosingParen(line, lparen_i)
                if line[rparen_i + 1] != ":":
                    data.error = True
                    data.err_msg = "missing : in function definition\ne.g. def foo(n):"
                    data.err_line = i 
                offset = 4 
                fn_name = line[offset:lparen_i]
                args = line[lparen_i+1:rparen_i]
                args = [elem.strip() for elem in args.split(",")] # potential safety concern
                (body, k) = get_indent_body(data, code_lines, i + 1)
                # int, tuple, str
                data.fns[fn_name] = (i, args, "".join(body))
                i = k - 1 # set i to skip code for body
                
                
            except Exception as e:
                # print(e)
                data.error = True
                data.err_msg = "\nfunction definition should be \
of the form\ndef function_name(argument1, argument2, argument3):\n\t#code content goes here"
                data.err_line = i
                return None

        elif line.startswith("return"):
            expr = line[len("return"):].strip()
            expr = replace_functions_with_values(data, data.fns, variables, expr, color, x0, y0, x1, y1)
            variables["return"] = eval_expr(data, variables, expr, i)
            return (True, True, False, x0, y0, x1, y1, color, variables)
        # here is where you run the function        
        elif "(" in line: # what if it's return ("(")
            lparen_i = line.find("(")
            revs = line[::-1]
            rparen_i = len(line) - revs.find(")") - 1 # finds right most paren ()
            name = line[:lparen_i].strip()
            vals = line[lparen_i+1:rparen_i]
            if vals == "":
                vals = []
            else:
                vals = [elem.strip() for elem in vals.split(",")]
                vals = [replace_functions_with_values(data, data.fns, variables, expr, color, x0, y0, x1, y1) for expr in vals]
                vals = [eval_expr(data, variables, expr, i) for expr in vals]
            if name in data.fns:
                (fn_line_num, args, body) = data.fns[name]
                f_variables = dict()
                f_variables["x"] = variables["x"]
                f_variables["y"] = variables["y"]
                f_variables["color"] = variables["color"]
                for j in range(len(vals)):
                    var_name = args[j]
                    f_variables[var_name] = vals[j]
                # 0, color, 0, x0, y0, x1, y1
                if data.frames != []:
                    result = interpret(data, "".join(body), *data.frames.pop())    
                else: 
                    result = interpret(data, body, f_variables, 0, color, 0, x0, y0, x1, y1, depth=depth+4)
                if result == None:
                    print("fn_line_num", fn_line_num)
                    data.err_line = fn_line_num + data.err_line + 1
                    return 
                (_, terminated, break_called, x0, y0, x1, y1, color, _) = result
                
                variables["x"] = f_variables["x"]
                variables["y"] = f_variables["y"]
                variables["color"] = f_variables["color"]
        
                if break_called:
                    # terminated keeps track of whether you've completed the inner loop or not
                    if (not terminated):
                        frame = (variables, i, color, 0, x0, y0, x1, y1)
                        # print("appending frame: ", frame)
                        data.frames.append(frame)
                        return (False, False, True, x0, y0, x1, y1, color, variables)
            else:
                data.error = True
                data.err_msg = "invalid function name"
                data.err_line = i
                return None
            # replace any variable names with args with stuff
            # replace variables in body with values
            # ok what you need to do is you need to make the dict with the general variables
            # info, an arg so this is one of the things that can't be packed into data...
        

        else:
            # print some exception
            print("invalid starting keyword")
            data.error = True
            data.err_msg = "invalid starting keyword"
            data.err_line = i 
            return None
    
        i += 1

    return (False, True, False, x0, y0, x1, y1, color, variables)

def draw_code(canvas, data):

    draw_window_height = data.canvas_height - data.draw_window_margin*2
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
    cwidth = canvas.winfo_width()
    cheight = canvas.winfo_height()
    offset = data.draw_window_margin
    # draw_window_height = data.canvas_height - offset*2
    # cx = data.draw_window_margin + data.draw_window_width/2
    # cy = data.draw_window_margin + draw_window_height/2
    draw_window_height = cheight - offset*2
    cx = data.draw_window_margin + cwidth/2
    cy = data.draw_window_margin + draw_window_height/2    
    # x axis
    canvas.create_line(offset, 
                       cy,
                       offset + cwidth,
                       cy, fill=data.outcolor)
    interval = 10
    increments_x = cwidth//interval//2*2 
    marker_radius = 5
    for i in range(1, int(increments_x//2 + 1)):
        mx = cx + interval*i
        mx_n = cx - interval*i
        my_top = cy - marker_radius
        my_bot = cy + marker_radius
        canvas.create_line(mx, my_top, mx, my_bot,fill=data.outcolor)
        canvas.create_line(mx_n, my_top, mx_n, my_bot,fill=data.outcolor)

    # draw y axis
    canvas.create_line(cx, data.draw_window_margin, cx, 
                       data.draw_window_margin + draw_window_height,
                       fill=data.outcolor)

    increments_y = draw_window_height//interval//2*2
    for i in range(1, int(increments_y//2 + 1)):
        mx_l = cx - marker_radius
        mx_r = cx + marker_radius
        my = cy + interval*i
        my_n = cy - interval*i
        canvas.create_line(mx_l, my, mx_r, my, fill=data.outcolor)
        canvas.create_line(mx_l, my_n, mx_r, my_n, fill=data.outcolor)

def init_GUI(data):
    data.draw_window_margin = 5
    data.draw_window_width = data.canvas_width-data.draw_window_margin 
    data.draw_window_height = data.canvas_height - data.draw_window_margin
    data.margin = 10
    data.draw_window_cx = data.draw_window_margin + data.draw_window_width/2
    data.draw_window_cy = data.draw_window_margin + data.draw_window_height/2
    #data.to_draw = []
    data.axes = False

def init_compile_data(data):
    data.fns = dict()
    data.to_repeat = None 
    # data.variables = dict()
    # data.variables['x'] = 0
    # data.variables['y'] = 0
    # data.variables['color'] = None
    data.error = False
    data.err_msg = ""
    data.code = data.textbox.get_text()
    data.to_draw = []
    data.frames = []
    data.print_string = []

def init(data):
    init_GUI(data)
    init_compile_data(data)
    
    data.debug_mode = False
    data.type_mode = False
    data.counter = 0
     # each string in this list should be separated by new line
    data.help = False
    data.error = False
    data.ver = None
    data.err_line = 0
    data.err_msg = ""
    data.code = ""
    variables = dict()
    variables['x'] = 0
    variables['y'] = 0
    variables['color'] = None
    interpret(data, data.code, variables)

def mousePressed(event, data):
    pass

def runcode(data):
    init_compile_data(data)
    code_lines, data.ln_map = filter_space(data.code.splitlines(), data.debug_mode)
    data.code = "\n".join(code_lines)
    variables = dict()
    variables['x'] = 0
    variables['y'] = 0
    variables['color'] = None
    interpret(data, data.code, variables)
    # print("frame post return: ", data.frames)


def savecode(data):
    data.textbox.save(data.ver)

def saveascode(data):
    data.textbox.saveas()

def loadcode(data):
    data.textbox.load(data.ver)

def clearcode(data):
    data.textbox.delete()

def toggleaxes(data):
    data.axes = not(data.axes)

def toggledebug(data):
    data.debug_mode = not(data.debug_mode)
    if(data.debug_mode):
        data.textbox.setoutline("yellow")
    else:
        data.textbox.setoutline("black")

def stepdebug(data):
    while len(data.frames) > 0:
        frame = data.frames.pop()
        # print("popped frame:", frame)
        result = interpret(data, data.code, *frame)
        if result == None: # an error occured
            data.frames = []
            return 
        (_, _, break_called, x0, y0, x1, y1, color, variables) = result
        if break_called:
            # print("frame post c: ", data.frames)
            return


def keyPressed(event, data):
    data.textbox.color()

def timerFired(data):
    data.counter += 1

def draw_screens(canvas, data):
    canvas.create_rectangle(data.draw_window_margin, data.draw_window_margin,
                            data.canvas_width-data.draw_window_margin, 
                           data.canvas_height, width=3)


def redrawAll(canvas, data):
    if data.axes:
        draw_axes(canvas, data)
    if data.error:
        if data.debug_mode:
            line_num = data.ln_map[data.err_line//2]
        else:
            line_num = data.ln_map[data.err_line]
        err_msg = "Error on line %d: %s" % (line_num, data.err_msg)
        data.console.configure(state="normal")
        data.console.delete('1.0', END)
        data.console.insert(tkinter.INSERT, err_msg)
        data.console.configure(state="disabled")
    else:
        draw_code(data.canvas, data)
        p = "\n".join(data.print_string)
        #clear the console
        data.console.configure(state="normal")
        data.console.delete('1.0', END)
        data.console.insert(tkinter.INSERT, p)
        data.console.configure(state="disabled")

#http://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget
class TextLineNumbers(tkinter.Canvas):
    def __init__(self, *args, **kwargs):
        tkinter.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.color = "#8f908a"

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum, fill= self.color)
            i = self.textwidget.index("%s+1line" % i)

class CustomText(tkinter.Text):
    def __init__(self, *args, **kwargs):
        tkinter.Text.__init__(self, *args, **kwargs)

        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lindex $args 0] in {insert replace delete}) ||
                    ([lrange $args 0 2] == {mark set insert}) || 
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))

class CustomTextBox(tkinter.Frame):
    def __init__(self, *args, **kwargs):
        tkinter.Frame.__init__(self, *args, **kwargs)
        self.text = CustomText(self)
        self.vsb = tkinter.Scrollbar(orient="vertical", command=self.text.yview)
        bg = "#272822"
        self.outcolor = "#505050"
        highcolor ="#49483e"
        self.text.configure(yscrollcommand=self.vsb.set, font=("Menlo-Regular", "14"),
            background=bg, fg ="white", highlightbackground = self.outcolor,
            highlightthickness = 0.5, selectbackground= highcolor,
            insertbackground="white")

        self.linenumbers = TextLineNumbers(self, width=30)
        self.linenumbers.attach(self.text)
        self.linenumbers.config(background=bg, highlightthickness = 0)


        self.vsb.pack(side="right", fill="y")
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change) 
        self.text.bind("<Tab>", self.insert_tab) # BUG WITH TAB IF NO INIT
        self.debugcolor = "#66d9ef"
        self.keycolor = "#c52672"
        self.stringcolor = "#e6db6e"
        self.boolcolor = "#ad80fe"
        self.text.tag_configure("keyword", foreground=self.keycolor)
        self.text.tag_configure("debug", foreground=self.debugcolor)
        self.text.tag_configure("string", foreground=self.stringcolor)
        self.text.tag_configure("bool", foreground=self.boolcolor)

        self.keywords = ["if", "while", "repeat", "else", "<-"]
        self.debug = ["break", "print", "def"]
        self.bool = ["True", "False"]
        self.oldtext=""

        self.filename=""
        self.text.bind("<Command-Key-a>", self.select_all)
        self.text.bind("<Command-Key-A>", self.select_all)
        #https://stackoverflow.com/questions/8449053/how-to-make-menubar-cut-copy-paste-with-python-tkinter
        self.text.bind("<KeyRelease>", self.color)


    def copy(self, event=None):
        self.clipboard_clear()
        text = self.text.get("sel.first", "sel.last")
        self.clipboard_append(text)

    def cut(self, event=None):
        self.copy()
        self.text.delete("sel.first", "sel.last")

    def paste(self, event=None):
        text = self.selection_get(selection='CLIPBOARD')
        self.text.insert('insert', text)

    #https://stackoverflow.com/questions/13801557/select-all-text-in-a-text-widget-using-python-3-with-tkinter
    def select_all(self, event=None):
        self.text.tag_add(SEL, "1.0", END)
        self.text.mark_set(INSERT, "1.0")
        self.text.see(INSERT)
        return 'break'

    def setoutline(self, color):
        self.text.configure(highlightbackground=color, highlightcolor=color)

    def insert_tab(self, event):
        # insert 4 spaces
        self.text.insert(INSERT, " " * 4)
        return 'break'

    def _on_change(self, event):
        self.linenumbers.redraw()

    def get_text(self):
        text = self.text.get("1.0",'end-1c')
        return text

    def saveas(self):
        self.filename =  filedialog.asksaveasfilename(initialdir = ".",title = "Select file", defaultextension=".sda")
        if(self.filename != ""):
            contents = self.get_text()
            writeFile(self.filename, contents)

    def save(self, ver=None):
        if(self.filename==""):
            self.saveas()
        else:
            contents = self.get_text()
            writeFile(self.filename, contents)

    def load(self, ver=None):
        self.filename =  filedialog.askopenfilename(initialdir = ".",title = "Select file", filetypes=[('Saada file','*.sda')])
        if(self.filename != ""):
            self.delete()
            contents = readFile(self.filename)
            self.text.insert("end",contents)
            self.color()
        self.enable()

    
    def delete(self):
        self.text.delete('1.0', END)

    def enable(self):
        self.text.configure(state="normal")

    def color(self, event=None):
        text = self.text.get("1.0", END)
        if(self.oldtext != text):
            self.oldtext = text
            r = 1
            #rows start at 1 and columns start at 0 *_*
            #coordinate is row.col
            for line in text.splitlines():
                c = 0

                #highlight each word if it is a debug or keyword
                while(c < len(line)):
                    char = line[c]
                    if(char not in string.whitespace):
                        initc = "%d.%d" %(r, c)
                        while(c<len(line)-1 and line[c+1] not in string.whitespace):
                            # print("finding word", char, c)
                            c+=1
                            char = line[c]
                        # print("end c ", c)
                        endc = "%d.%d" % (r, c+1)
                        word = self.text.get(initc, endc)
                        # print("word", word, initc,endc)
                        #remove  old tags
                        for tag in self.text.tag_names():
                            self.text.tag_remove(tag, initc, endc)

                        #apply tags
                        if word in self.keywords:
                            self.text.tag_add("keyword", initc, endc)
                        elif word in self.debug:
                            self.text.tag_add("debug", initc, endc)
                        elif word in self.bool:
                            self.text.tag_add("bool", initc, endc)
                    c+= 1

                #highlight strings
                i = 0
                strstart = None
                while(i < len(line)):
                    if(line[i] == "\"" and strstart == None):
                        strstart = i
                    elif(line[i] == "\"" and strstart != None):
                        initc = "%d.%d" % (r, strstart)
                        endc = "%d.%d" % (r, i + 1)
                        self.text.tag_add("string", initc, endc)
                        strstart = None
                    i+=1

                #highlight numbers
                #highlight line in debug mode
                #highlight line if error
                r+=1

def createmenu(root, data):
    # create a menu for the menubar and associate it
    # with the window
    menubar = tkinter.Menu()
    root.configure(menu=menubar)

    # create a File menu and add it to the menubar
    file_menu = tkinter.Menu(menubar, tearoff=False)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Save", underline=1, command=lambda: savecode(data), 
        accelerator="Ctrl+s")
    file_menu.add_command(label="Save As", underline=1, command=lambda: saveascode(data), 
        accelerator="Ctrl+Shift+S")
    file_menu.add_command(label="Open", underline=1, command=lambda: loadcode(data),
         accelerator="Ctrl+O")

    edit_menu = tkinter.Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    #edit_menu.add_command(label="Clear", command=lambda: clearcode(data), accelerator="Command-V")
    edit_menu.add_command(
        label="Select All", 
        command=data.textbox.select_all, 
        accelerator="Command-A"
        )
    edit_menu.add_command(
        label="Copy", 
        command=data.textbox.copy,
        accelerator="Command-C")
    edit_menu.add_command(
        label="Cut", 
        command=data.textbox.cut,
        accelerator="Command-X")
    edit_menu.add_command(
        label="Paste", 
        command=data.textbox.paste,
        accelerator="Command-V")
    
    tools_menu = tkinter.Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Tools", menu=tools_menu)

    tools_menu.add_command(label="Run", underline=1,
                             command=lambda: runcode(data), accelerator="Ctrl+R")
    tools_menu.add_command(label="Toggle Axes",  underline=1,
        command=lambda: toggleaxes(data),  accelerator="Ctrl+A")
    tools_menu.add_command(label="Toggle Debug", underline=1, 
        command=lambda: toggledebug(data), accelerator="Ctrl+D")
    tools_menu.add_command(label="Step", underline=1, 
        command=lambda: stepdebug(data), accelerator="Ctrl+E")

    root.bind_all("<Control-r>", lambda e: runcode(data))
    root.bind_all("<Control-a>", lambda e: toggleaxes(data))
    root.bind_all("<Control-d>", lambda e: toggledebug(data))
    root.bind_all("<Control-e>", lambda e: stepdebug(data))
    root.bind_all("<Control-s>", lambda e: savecode(data))
    root.bind_all("<Control-o>", lambda e: loadcode(data))

def run(width=1500, height=600):
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
    data.textbox_width = width//2
    data.canvas_width = width//2
    data.canvas_height = height//2
    data.bg = "#272822"
    data.outcolor ="#505050"
    data.outthick = 0.5
    # create the root and the canvas
    root = Tk()
    root.configure(bg=data.bg)
    # xscrollbar = tkinter.Scrollbar(root, orient="horizontal")
    # xscrollbar.pack(side=BOTTOM, fill=X)

    #left frame = left half of the screen
    data.leftframe = Frame(
        root,
        width = data.textbox_width,
        height = height
        )
    data.leftframe.pack(
        side="left", 
        fill="both", 
        expand = True
        )
    data.leftframe.pack_propagate(False)

    data.textbox = CustomTextBox(
        data.leftframe, 
        width = data.textbox_width, 
        height = height
        )
    data.textbox.pack(fill="both", expand = True)

    #rightframe = right half of the screen
    data.rightframe = Frame(
        root, 
        width = data.canvas_width, 
        height= height)
    data.rightframe.pack(
        side="left",
        fill="both",
        expand=True)
    data.rightframe.configure(bg=data.bg)
    data.rightframe.pack_propagate(False)

    data.canvas = Canvas(
        data.rightframe, 
        width = data.canvas_width, 
        height = data.canvas_height)
    data.canvas.pack(
        side="top", 
        fill="both",
        expand= True)
    data.canvas.configure(
        highlightbackground = data.outcolor, 
        highlightthickness = data.outthick)

    data.console = tkinter.scrolledtext.ScrolledText(
        master = data.rightframe,
        wrap   = tkinter.WORD,
    )
    data.console.pack(
        side="bottom", 
        fill="both", 
        expand = True
        )
    data.console.configure(
        bg=data.bg, 
        fg ="white", 
        highlightbackground = data.outcolor, 
        highlightthickness = data.outthick,
        state="disabled"
        )

    # create menu
    createmenu(root, data)

    init(data)

    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, data.canvas, data))    
    timerFiredWrapper(data.canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

def test_replace_functions_with_values():
    # data, functions, variables, line, color, x0, y0, x1, y1
    # make sure you replace multiple instances of the function 
    print("Testing replace_functions_with_values...")
    class Struct(): pass
    data = Struct()
    fns = {'fibb': (1, ['n'], 'if (n == 0):\n    return 1\nif (n == 1):\n    return 1\nreturn fibb(n - 1) + fibb(n - 2)\n')}
    data.fns = fns
    data.debug_mode = False
    data.frames = []
    variables = {'n': 3, 'y': 0, 'x': 0, 'color': None}
    expr = "fibb(n - 1) + fibb(n - 2)"
    fns['bar'] = (1, ['m'], 'return 0')
    assert(replace_functions_with_values(data, fns, variables, expr, None, 0, 0, 0, 0) == "2 + 1")
    # assert(replace_functions_with_values(data, fns, variables, "fibb(bar(42))", None, 0, 0, 0, 0) == "1")
    print("...passed!")

def test_all():
    print("Testing all functions...")
    test_replace_vars_with_vals()
    test_eval_expr()
    test_strip_end()
    test_get_indent_body()
    test_filter_space()
    test_replace_functions_with_values()
    test_get_str_contents()
    print("...passed!")

# test_all()
run(900, 600) #width, height
