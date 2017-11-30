"""
Ananya Rajgarhia
1/20/17

Current features:
  - addition, subtraction, mod, division, multiplication, int division
  - repeat loops
  - break points
  - print statements work too
  - eval expr using eval and checking for valid syms only
  - saving and loading files
  - if/else statements
  - debug mode (using breaks)
  - general variables
  - while loops
  - functions
 
"""

from tkinter.scrolledtext import *
import tkinter
import string
import math
import random
import time
import threading
import queue
from tkinter import filedialog
from tkinter import *


class CompileData(object):
    def __init__(self, code, variables=None, i=0, color="none", 
        to_repeat=None, repeated=0, x0=0, y0=0, x1=0, y1=0):
        self.code = code 
        self.variables = dict() if variables is None else variables
        self.i = i
        self.color = color
        self.to_repeat = None
        self.repeated = repeated
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def __repr__(self):
        rep = [
        'code=%r' % self.code,
        'variables=%r' % self.variables,
        'i=%r' % self.i,
        'color=%r' % self.color,
        'to_repeat=%r' % self.to_repeat,
        'repeated=%r' % self.repeated,
        'x0=%r' % self.x0,
        'y0=%r' % self.y0,
        'x1=%r' % self.x1,
        'y1=%r' % self.y1
        ]
        return 'CompileData(\n%s\n)' % '\n'.join(rep)




class ReturnData(object):
    def __init__(self, returned=False, terminated=False,
     break_called=False, wait_duration=0, 
                 x0=0, y0=0, x1=0, y1=0, color="none", variables=None):
        self.returned = returned
        self.terminated = terminated
        self.break_called = break_called
        self.wait_duration = wait_duration
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.color = color
        self.variables = variables
    def __repr__(self):
        return "%r" % self.__dict__

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

# sets data error flag, msg, and err_line
# returns None
def create_error(data, msg, line_num):
    data.error = True
    data.err_msg = msg
    data.err_line = line_num

# helper function that replaces variable name in expression 
# with the variable's actual value
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
            temp = expr.replace(var, "%r")
            expr = temp % ((val,)*num_occurences)
    return expr


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


def is_safe_expr(expr):
    safe_syms = "<>/*+-.()%=[],"
    for c in expr:
        if ((not c.isalpha()) and 
           (not(c.isspace() or c.isdigit() or c in safe_syms))):
            return False
    return True

# helper function that processes mathematical assignment expressions
# variables is a mapping of var names to vals
# i is the line number of code being evaluated
# if expr doesn't result in a valid expr, None is returned and the error flag
#   is set
def eval_expr(data, variables, expr, line_num, orig_expr=""):
    if (expr == ""): return ""
    expr = replace_vars_with_values(data, variables, expr)

    # treating entirety of contents as a string
    if (("\"" in expr) or ("\'" in expr)): 
        return get_str_contents(expr)

    

    # check if safe
    if not(is_safe_expr(expr)):
        msg = "expression <%s> contains invalid symbol" % expr
        return create_error(data, msg, line_num)

    # finally eval it
    try:   
        return eval(expr)
    except Exception as e:
        # if contains a variable that wasn't replaced with a value 
        # check moved here because you want to be able to evaluate "math.stuff"
        if containsAlpha(expr):
            err_expr = expr if orig_expr == "" else orig_expr
            msg = "<%s> is not a valid expression as some of the terms are\
     not defined, did you mean <\"%s\">?" % (err_expr, err_expr)
        else:
            msg = "error evaluating expression: %s" % expr
        return create_error(data, msg, line_num)


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
    assert(get_indent_body(data ,code_lines, 5) == (
        ["y<-y+10", "\n", "draw", "\n"], 7))
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


def replace_functions_with_values(data, functions, variables, line, color, x0, 
    y0, x1, y1, depth=0):

    sorted_by_len = sorted(functions, key=lambda s: -len(s)) # longest first
    for fn_name in sorted_by_len:
        i = line.find(fn_name)
        # replace all instances of the function name in the expr
        while (i != -1): 
            lparen_i = line.find("(", i)
            rparen_i = getMatchingClosingParen(line, lparen_i)
            name = line[:lparen_i].strip()
            vals = get_paren_contents(line, lparen_i)
            print("vals 347", vals) # need to do error check here -> if it's an undefined variable
            if vals == "":
                vals = []
            else:
                # make sure all values are reduced
                vals = [elem.strip() for elem in vals.split(",")] 
                tempvals = []
                for expr in vals:
                    if (containsFunction(data.fns, expr)):
                        tempvals.append(replace_functions_with_values(data, 
                            functions, variables, expr, color, x0, y0, x1, y1))
                    else:
                        tempvals.append(expr)

                vals = [eval_expr(data, variables, expr, i) 
                for expr in tempvals]

            (fn_line, args, body) = functions[fn_name]
            f_variables = init_variables()
            f_variables["x"] = variables["x"]
            f_variables["y"] = variables["y"]
            f_variables["color"] = variables["color"]
            print("args", args)
            print("vals", vals)
            if len(args) != len(vals):
                msg = "function %s expected %d arguments but received %d arguments instead." % (fn_name, len(args), len(vals))
                return create_error(data, msg, i)
            for j in range(len(vals)):
                var_name = args[j]
                f_variables[var_name] = vals[j]

            # if stack frames not empty, pop and execute
            code_body = "".join(body)
            if data.frames:
                print("here")
                print(data.frames[-1])
                print(code_body)
                result = interpret(data, data.frames.pop())
            else:
                # 0, color, 0, x0, y0, x1, y1
                new_compile_data = CompileData(code_body, 
                    variables=f_variables,
                    color=color,
                    x0=x0,
                    y0=y0,
                    x1=x1,
                    y1=y1)
                result = interpret(data, new_compile_data)
            if result == None:
                if not data.inside_fn:
                    data.err_line = fn_line + data.err_line + 1
                data.inside_fn = True
                return

            variables["x"] = result.variables["x"]
            variables["y"] = result.variables["y"]
            variables["color"] = result.variables["color"]
            if (result.break_called or result.wait_duration) and not result.terminated:
                return result               
            line = (line[:i] + "%r" + line[rparen_i+1:]) % result.variables["return"]
            i = line.find(fn_name)
    return line

# checks if there are any numbers in the expr
def containsDigit(s):
    for c in s:
        if c.isdigit():
            return True
    return False

# checks if there are any alphabet characters in the expr
def containsAlpha(s):
    for c in s:
        if c.isalpha():
            return True
    return False

# gets the value within quotes for a str
def get_str_contents(s):
    delim = "\"" if "\"" in s else "\'"
    start = s.find(delim)
    end = s.find(delim, start + 1)
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
# frame = (variables, i, color, to_repeat, repeated, x0, y0, x1, y1, fn, ret)
def interpret(data, compile_data):

    code = compile_data.code.splitlines()
    n = len(code)
    while (compile_data.i < n):
        line = code[compile_data.i]
        # print(line)
        if line[0].isspace():
            msg = "unexpected or extra white space at the start of the line"     
            return create_error(data, msg, compile_data.i)

        if "<-" in line:
            tokens = line.split("<-")
            if (len(tokens) < 2):
                msg = "should be of the form \'variable_name <- value\'"
                return create_error(data, msg, compile_data.i)

            (var, expr) = (tokens[0].strip(), tokens[1].strip())
            expr = replace_functions_with_values(data, data.fns, 
                compile_data.variables, expr, compile_data.color, 
                compile_data.x0, compile_data.y0, compile_data.x1, 
                compile_data.y1)
            if expr is None:
                #error occured
                if not data.inside_fn:
                    data.err_line = i + data.err_line + 1
                return None
            # if the line was changed, you want to document that somehow
            elif isinstance(expr, ReturnData): # break or wait called
                frame = CompileData(code="\n".join(code),
                                    variables=compile_data.variables,
                                    i=compile_data.i,
                                    color=compile_data.color,
                                    to_repeat=compile_data.to_repeat,
                                    x0=compile_data.x0,
                                    y0=compile_data.y0,
                                    x1=compile_data.x1,
                                    y1=compile_data.y1)
                data.frames.append(frame)
                return ReturnData(returned=False,
                    terminated=False, 
                    break_called=expr.break_called,
                    x0=compile_data.x0, 
                    y0=compile_data.y0, 
                    x1=compile_data.x1, 
                    y1=compile_data.y1,
                    wait_duration=expr.wait_duration,
                    color=compile_data.color, 
                    variables=compile_data.variables)
            if "\"" in expr:
                val = get_str_contents(expr)
                if var == "x" or var == "y":
                    msg = "x and y must be integers"
                    return create_error(data, msg, compile_data.i)

                if var == "color":
                    compile_data.color = val
                compile_data.variables[var] = val
            else:
                res = eval_expr(data, compile_data.variables, expr, 
                                compile_data.i)
                if res == None: # there was an error
                    return 
                compile_data.variables[var] = res
                if var == "x":
                    compile_data.x1 = res
                elif var == "y":
                    compile_data.y1 = res
                elif var == "color":
                    compile_data.color = res

        elif line.startswith("draw("):
            width = get_paren_contents(line)
            # default line width
            line_width = data.default_line_width
            if width != "":
                line_width = eval_expr(data, compile_data.variables, width, 
                                       compile_data.i)

                if not isinstance(line_width, int): 
                    msg = "draw takes no arguments or one integer as the line width"
                    return create_error(data, msg, i)

            if compile_data.color != "none":
                data.to_draw.append((compile_data.x0, 
                                     compile_data.y0, 
                                     compile_data.x1, 
                                     compile_data.y1, 
                                     compile_data.color, 
                                     compile_data.i, 
                                     line_width))
            compile_data.x0 = compile_data.x1
            compile_data.y0 = compile_data.y1
        
        elif line.startswith("write("):
            write_args = get_paren_contents(line)
            text = eval(write_args.split(",")[0].strip())
            anchor = None
            font = None
            if len(write_args.split(",")) > 1:
                anchor = eval(write_args.split(",")[1].strip())
            if len(write_args.split(",")) > 2:
                font = eval(write_args.split(",")[2].strip())
            data.to_write.append((text,
                                 anchor,
                                 font,
                                 compile_data.x1, 
                                 compile_data.y1, 
                                 compile_data.i))
        
        elif line == ("clear()"):
            data.to_draw = []
            data.to_write = []

        elif line.startswith("if"):
            cond = None
            # get contents between parens
            expr = get_paren_contents(line)
            expr = replace_functions_with_values(data, data.fns, 
                compile_data.variables, expr, compile_data.color, 
                compile_data.x0, compile_data.y0, compile_data.x1, 
                compile_data.y1)
            cond = eval_expr(data, compile_data.variables, expr, compile_data.i)

            if (cond is None): 
                msg = "condition not set"
                return create_error(data, msg, compile_data.i)

            (body, k) = get_indent_body(data, compile_data.code.splitlines(), compile_data.i + 1)
            
            if (cond):

                if data.frames:
                    # new_compile_data = CompileData("".join(body), *data.frames.pop())
                    result = interpret(data, data.frames.pop())    
                else: 
                    new_compile_data = CompileData(
                        code="".join(body), 
                        variables=compile_data.variables,
                        color=compile_data.color, 
                        x0=compile_data.x0, 
                        y0=compile_data.y0, 
                        x1=compile_data.x1, 
                        y1=compile_data.y1)
                    result = interpret(data, new_compile_data)

                if result is None and data.error: 
                    #error occured
                    if not data.inside_fn:
                        data.err_line = i + data.err_line + 1
                    return None
                # (returned, terminated, break_called, x0, y0, x1, y1, color, variables) = result
                if result.returned:
                    ret = ReturnData(returned=False, terminated=False, break_called=False,
                        x0=compile_data.x0, y0=compile_data.y0,
                        x1=compile_data.x1, y1=compile_data.y1,
                        color=compile_data.color, variables=compile_data.variables)
                     
                    return ret
                if result.break_called or result.wait_duration:
                    # frame is line number, color, #repeats, and coord vals
                    frame = CompileData(code=compile_data.code,
                                        variables=compile_data.variables,
                                        color=compile_data.color,
                                        to_repeat=compile_data.to_repeat,
                                        x0=compile_data.x0,
                                        y0=compile_data.y0,
                                        x1=compile_data.x1,
                                        y1=compile_data.y1
                                        )
                    if result.terminated:
                        frame.i = k
                    else:
                        frame.i = compile_data.i
                    data.frames.append(frame)
                    return ReturnData(returned=False,
                        terminated=False, 
                        break_called=result.break_called,
                        x0=compile_data.x0, 
                        y0=compile_data.y0, 
                        x1=compile_data.x1, 
                        y1=compile_data.y1,
                        wait_duration=result.wait_duration,
                        color=compile_data.color, 
                        variables=compile_data.variables)
            check_elif = ((k < n and code[k].startswith("elif")) or
                          (data.debug_mode and k+1 < n and 
                           code[k+1].startswith("elif")))
            satisfied = cond
            while (check_elif):
                cond = None
                # get contents between parens
                expr = get_paren_contents(code[k])
                print("expr", expr)
                expr = replace_functions_with_values(data, data.fns, 
                    compile_data.variables, expr, compile_data.color, 
                    compile_data.x0, compile_data.y0, compile_data.x1, 
                    compile_data.y1)
                cond = eval_expr(data, compile_data.variables, expr, 
                    compile_data.i)
                print(cond)
                offset = int(data.debug_mode)
                (elif_body, k) = get_indent_body(
                    data, 
                    compile_data.code.splitlines(),
                    k + 1 + offset)
                if cond and not satisfied:
                    satisfied = True
                    if data.frames != []:
                        # new_compile_data = CompileData("".join(elif_body), 
                        #     *data.frames.pop())
                        result = interpret(data, data.frames.pop())
                        # result = interpret(data, else_body, *data.frames.pop())    
                    else:
                        new_compile_data = CompileData(
                            code="".join(elif_body), 
                            variables=compile_data.variables,
                            color=compile_data.color,
                            x0=compile_data.x0,
                            y0=compile_data.y0,
                            x1=compile_data.x1,
                            y1=compile_data.y1)
                        result = interpret(data, new_compile_data) 
                    
                    if result is None and data.error: #error occured
                        if not data.inside_fn:
                            data.err_line = i + data.err_line + 1
                        return 
                    # (returned, terminated, break_called, x0, y0, x1, y1, color, variables) = result
                    if result.returned:
                        ret = ReturnData(returned=False,
                            terminated=False,
                            break_called=False,
                            x0=compile_data.x0,
                            y0=compile_data.y0,
                            x1=compile_data.x1,
                            y1=compile_data.y1,
                            color=compile_data.color,
                            variables=compile_data.variables)
                        return ret
                        # return (True, False, True, x0, y0, x1, y1, color, variables)
                    if result.break_called or result.wait_duration: # can't hit both break and return
                        # frame is line number, color, #repeats, and coord vals
                        frame = CompileData(code=compile_data.code,
                                        variables=compile_data.variables,
                                        color=compile_data.color,
                                        to_repeat=compile_data.to_repeat,
                                        x0=compile_data.x0,
                                        y0=compile_data.y0,
                                        x1=compile_data.x1,
                                        y1=compile_data.y1
                                        )
                        if result.terminated:
                            frame.i = k
                        else:
                            frame.i = compile_data.i
                        data.frames.append(frame)
                        ret = ReturnData(returned=False,
                            terminated=False,
                            break_called=result.break_called,
                            wait_duration=result.wait_duration,
                            x0=compile_data.x0,
                            y0=compile_data.y0,
                            x1=compile_data.x1,
                            y1=compile_data.y1,
                            color=compile_data.color,
                            variables=compile_data.variables)
                        return ret
                check_elif = ((k < n and code[k].startswith("elif")) or
                          (data.debug_mode and k+1 < n and 
                           code[k+1].startswith("elif")))

            else_exists = False
            else_body = []
            if (k < n and code[k].startswith("else")) or (data.debug_mode
                and k+1 < n and code[k+1].startswith("else")):
                print("found else")
                else_exists = True
                offset = int(data.debug_mode)
                (else_body, k) = get_indent_body(data, compile_data.code.splitlines(), 
                    k + 1 + offset) 

            if (else_exists and not satisfied):
                if data.frames != []:
                    # new_compile_data = CompileData("".join(else_body), 
                    #     *data.frames.pop())
                    result = interpret(data, data.frames.pop())
                    # result = interpret(data, else_body, *data.frames.pop())    
                else:
                    new_compile_data = CompileData(
                        code="".join(else_body), 
                        variables=compile_data.variables,
                        color=compile_data.color,
                        x0=compile_data.x0,
                        y0=compile_data.y0,
                        x1=compile_data.x1,
                        y1=compile_data.y1)
                    result = interpret(data, new_compile_data) 
                
                if result is None and data.error: #error occured
                    if not data.inside_fn:
                        data.err_line = i + data.err_line + 1
                    return 
                # (returned, terminated, break_called, x0, y0, x1, y1, color, variables) = result
                if result.returned:
                    ret = ReturnData(returned=False,
                        terminated=False,
                        break_called=False,
                        x0=compile_data.x0,
                        y0=compile_data.y0,
                        x1=compile_data.x1,
                        y1=compile_data.y1,
                        color=compile_data.color,
                        variables=compile_data.variables)
                    return ret
                    # return (True, False, True, x0, y0, x1, y1, color, variables)
                if result.break_called or result.wait_duration: # can't hit both break and return
                    frame = CompileData(code=compile_data.code,
                                        variables=compile_data.variables,
                                        color=compile_data.color,
                                        to_repeat=compile_data.to_repeat,
                                        x0=compile_data.x0,
                                        y0=compile_data.y0,
                                        x1=compile_data.x1,
                                        y1=compile_data.y1
                                        )
                    if result.terminated:
                        frame.i = k
                    else:
                        frame.i = compile_data.i
                    data.frames.append(frame)
                    ret = ReturnData(returned=False,
                        terminated=False,
                        break_called=result.break_called,
                        wait_duration=result.wait_duration,
                        x0=compile_data.x0,
                        y0=compile_data.y0,
                        x1=compile_data.x1,
                        y1=compile_data.y1,
                        color=compile_data.color,
                        variables=compile_data.variables)
                    return ret
            compile_data.i = k - 1 # minus 1 because you increment i at the end
        elif line.startswith("while"):
            cond = None
            # get contents between parens
            start = line.find("(")
            expr = get_paren_contents(line, start)
            expr = replace_functions_with_values(data, data.fns, 
                compile_data.variables, expr, compile_data.color, 
                compile_data.x0, compile_data.y0, compile_data.x1, 
                compile_data.y1)
            cond = eval_expr(data, compile_data.variables, expr, compile_data.i)

            (body, k) = get_indent_body(data, code, compile_data.i + 1)
            while (cond or compile_data.repeated): # repeated seems to be keeping track of whether the loop terminated? oh.
                if data.frames != []:
                    # new_compile_data = CompileData("".join(body), 
                    #     *data.frames.pop())
                    result = interpret(data, data.frames.pop())    
                else: 
                    new_compile_data = CompileData(
                        code="".join(body),
                        variables=compile_data.variables,
                        color=compile_data.color,
                        x0=compile_data.x0,
                        y0=compile_data.y0,
                        x1=compile_data.x1,
                        y1=compile_data.y1
                        )
                    result = interpret(data, new_compile_data)
                    # result = interpret(data, body, variables, 0, color, None, 
                    #                    0, x0, y0, x1, y1)
                
                if result == None and data.error: # error occured
                    if not data.inside_fn:
                        data.err_line = compile_data.i + data.err_line + 1
                    return None

                # (returned, terminated, break_called, x0, y0, x1, y1, color, variables) = result
                if result.returned:
                    return_data = ReturnData(
                        returned=True,
                        break_called=True,
                        x0=compile_data.x0,
                        y0=compile_data.y0,
                        x1=compile_data.x1,
                        y1=compile_data.y1,
                        color=compile_data.color,
                        variables=compile_data.variables)
                    return return_data
                    # return (True, False, True, x0, y0, x1, y1, color, variables)
                if result.break_called or result.wait_duration:
                    # terminated keeps track of whether you've completed 
                    # the inner code of the loop
                    expr = replace_functions_with_values(data, data.fns, 
                        compile_data.variables, expr, compile_data.color, 
                        compile_data.x0, compile_data.y0, compile_data.x1, 
                        compile_data.y1)
                    cond = eval_expr(data, compile_data.variables, expr, compile_data.i)
                    if not cond and result.terminated: # this is the final iter of loop
                        i = k
                    frame = CompileData(code=compile_data.code,
                                        variables=compile_data.variables,
                                        i=compile_data.i,
                                        color=compile_data.color,
                                        to_repeat=compile_data.to_repeat,
                                        repeated=int(not(result.terminated)),
                                        x0=compile_data.x0,
                                        y0=compile_data.y0,
                                        x1=compile_data.x1,
                                        y1=compile_data.y1
                                        )
                    # frame = (compile_data.variables, compile_data.i, 
                    #     compile_data.color, compile_data.to_repeat, 
                    #     int(not(result.terminated)), compile_data.x0, 
                    #     compile_data.y0, compile_data.x1, compile_data.y1)
                    data.frames.append(frame)
                    return_data = ReturnData(
                        break_called=result.break_called,
                        x0=compile_data.x0,
                        y0=compile_data.y0,
                        x1=compile_data.x1,
                        y1=compile_data.y1,
                        wait_duration=result.wait_duration,
                        color=compile_data.color,
                        variables=compile_data.variables)
                    return return_data
                    # return (False, False, True, x0, y0, x1, y1, color, variables)
                expr = replace_functions_with_values(data, data.fns, 
                    compile_data.variables, expr, compile_data.color, 
                    compile_data.x0, compile_data.y0, 
                    compile_data.x1, compile_data.y1)
                cond = eval_expr(data, compile_data.variables, expr, 
                    compile_data.i)
                compile_data.repeated = 0
            compile_data.i = k - 1

        elif line.startswith("repeat"): 
            # get the number between the end of repeat and before the colon
            if ":" not in line:
                msg = "repeat loops should be of the form \'repeat <integer>:\'\
 followed by an indented block of code"
                return create_error(data, msg, compile_data.i)

            try:
                expr = line.split(":")[0][len("repeat"):].strip()

            except Exception as e:
                msg = "repeat loops should be of the form \'repeat <integer>:\'\
 followed by an indented block of code"
                return create_error(data, msg, compile_data.i)

            if compile_data.to_repeat is None: 
                expr = replace_functions_with_values(data, data.fns, 
                    compile_data.variables, expr, compile_data.color, 
                    compile_data.x0, compile_data.y0, compile_data.x1, 
                    compile_data.y1)
                m = eval_expr(data, compile_data.variables, expr, 
                    compile_data.i)
                if m < 0:
                    msg = "repeat value must be nonnegative"
                    return create_error(data, msg, compile_data.i)
                compile_data.to_repeat = m

            body, k = get_indent_body(data, compile_data.code.splitlines(), 
                compile_data.i + 1)
            if k == compile_data.i + 1: 
                msg = "no content to repeat\n\
(Hint: remember to indent the block you would like to repeat)"
                return create_error(data, msg, k)

            # we use to_repeat - repeated to handle for breakpoints
            for j in range(compile_data.to_repeat - compile_data.repeated):
                temp_repeat = compile_data.to_repeat
                compile_data.to_repeat = None
                if data.frames != []:
                    frame = data.frames.pop()
                    # new_compile_data = CompileData("".join(body), frame))
                    result = interpret(data, frame)   
                else: 
                    new_compile_data = CompileData("".join(body),
                        variables=compile_data.variables,
                        color=compile_data.color,
                        x0=compile_data.x0,
                        y0=compile_data.y0,
                        x1=compile_data.x1,
                        y1=compile_data.y1)
                    result = interpret(data, new_compile_data)
                compile_data.to_repeat = temp_repeat
                if result is None and data.error: # error occured
                    if not data.inside_fn:
                        data.err_line = i + data.err_line + 1
                    return None

                if result.returned:
                    result.terminated = False
                    result.terminated = True
                    return result
                    # return (True, False, True, x0, y0, x1, y1, color, variables)
                if result.break_called or result.wait_duration:
                    if j + 1 > compile_data.to_repeat - compile_data.repeated:
                        compile_data.i = k
    
                    # terminated keeps track of whether you've completed the inner loop or not
                    if (result.terminated): compile_data.repeated += 1
                    frame = CompileData(code=compile_data.code,
                                        variables=compile_data.variables,
                                        i=compile_data.i,
                                        color=compile_data.color,
                                        to_repeat=compile_data.to_repeat,
                                        repeated=compile_data.repeated+j,
                                        x0=compile_data.x0,
                                        y0=compile_data.y0,
                                        x1=compile_data.x1,
                                        y1=compile_data.y1)
                    # frame = (compile_data.variables, compile_data.i, 
                    #     compile_data.color, compile_data.to_repeat, 
                    #     compile_data.repeated + j, 
                    #     compile_data.x0, compile_data.y0, 
                    #     compile_data.x1, compile_data.y1)
                    data.frames.append(frame)
                    return_data = ReturnData(
                        returned=False,
                        terminated=False,
                        break_called=result.break_called,
                        wait_duration=result.wait_duration,
                        x0=compile_data.x0,
                        y0=compile_data.y0,
                        x1=compile_data.x1,
                        y1=compile_data.y1,
                        color=compile_data.color,
                        variables=compile_data.variables
                        )
                    return return_data
                    # return (False, False, True, x0, y0, x1, y1, color, variables)
                
            compile_data.to_repeat = None
            compile_data.i = k - 1

        elif line.startswith("print("):
            if ")" not in line:
                msg = "print is a function and needs parentheses,\
                 for example: print(\"hello world\")"
                return create_error(data, msg, compile_data.i)

            orig_expr = get_paren_contents(line)
            s = orig_expr
            if "\"" in orig_expr:
                s = get_str_contents(s)
            else:
                if "(" in orig_expr:
                    s = replace_functions_with_values(data, data.fns, 
                        compile_data.variables, 
                        s, compile_data.color, compile_data.x0, 
                        compile_data.y0, compile_data.x1, compile_data.y1)
                    if s == None:
                        return None
                s = eval_expr(data, compile_data.variables, s, compile_data.i, 
                    orig_expr)
                if s == None:
                    return 
            data.print_string.append(str(s))

        elif line.startswith("break"):
            frame = CompileData(code=compile_data.code,
                                variables=compile_data.variables,
                                i=compile_data.i + 1,
                                color=compile_data.color,
                                to_repeat=compile_data.to_repeat,
                                x0=compile_data.x0,
                                y0=compile_data.y0,
                                x1=compile_data.x1,
                                y1=compile_data.y1
                                )
            # frame = (compile_data.variables, compile_data.i + 1, 
            #     compile_data.color, compile_data.to_repeat, 0, compile_data.x0, 
            #     compile_data.y0, compile_data.x1, compile_data.y1)
            return_data = ReturnData(
                    returned=False,
                    terminated=True,
                    break_called=True,
                    x0=compile_data.x0,
                    y0=compile_data.y0,
                    x1=compile_data.x1,
                    y1=compile_data.y1,
                    color=compile_data.color,
                    variables=compile_data.variables)
            if (compile_data.i + 1) == n:
                return return_data
            data.frames.append(frame)
            return_data.terminated = False
            return return_data 

        elif line.startswith("wait("):
            expr = get_paren_contents(line)
            duration = eval_expr(data, compile_data.variables, expr, compile_data.i)
            frame = CompileData(code=compile_data.code,
                                variables=compile_data.variables,
                                i=compile_data.i + 1,
                                color=compile_data.color,
                                to_repeat=compile_data.to_repeat,
                                x0=compile_data.x0,
                                y0=compile_data.y0,
                                x1=compile_data.x1,
                                y1=compile_data.y1
                                )
            # frame = (compile_data.variables, compile_data.i + 1, 
            #     compile_data.color, compile_data.to_repeat, 0, compile_data.x0, 
            #     compile_data.y0, compile_data.x1, compile_data.y1)
            return_data = ReturnData(
                    returned=False,
                    terminated=True,
                    break_called=False,
                    x0=compile_data.x0,
                    y0=compile_data.y0,
                    x1=compile_data.x1,
                    y1=compile_data.y1,
                    color=compile_data.color,
                    variables=compile_data.variables,
                    wait_duration=duration)
            if (compile_data.i + 1) == n:
                return return_data
            data.frames.append(frame)
            return_data.terminated = False
            return return_data 

        elif line.startswith("def"):
            try:

                lparen_i = line.find("(") 
                rparen_i = getMatchingClosingParen(line, lparen_i)
                if line[rparen_i + 1] != ":":
                    msg = "missing : in function definition\ne.g. def foo(n):"
                    return create_error(data, msg, compile_data.i)
                offset = 4
                fn_name = line[offset:lparen_i]
                args = line[lparen_i+1:rparen_i]
                args = [elem.strip() for elem in args.split(",") if elem != ''] # potential safety concern
                (body, k) = get_indent_body(data, compile_data.code.splitlines(), 
                    compile_data.i + 1)
                # int, tuple, str
                data.fns[fn_name] = (compile_data.i, args, body)
                compile_data.i = k - 1 # set i to skip code for body
                
            except Exception as e:
                msg = "\nfunction definition should be \
of the form\ndef function_name(argument1, argument2, argument3):\n\t#code\
 content goes here"
                return create_error(data, msg, compile_data.i)

        elif line.startswith("return"):
            expr = line[len("return"):].strip()
            expr = replace_functions_with_values(data, data.fns, 
                compile_data.variables, expr, compile_data.color, 
                compile_data.x0, compile_data.y0, compile_data.x1, 
                compile_data.y1)
            if expr == None:
                return None
            result = eval_expr(data, compile_data.variables, expr, 
                compile_data.i)
            if result == None:
                return None
            compile_data.variables["return"] = result
            return_data = ReturnData(
                returned=True,
                terminated=True,
                break_called=False,
                x0=compile_data.x0,
                y0=compile_data.y0,
                x1=compile_data.x1,
                y1=compile_data.y1,
                color=compile_data.color,
                variables=compile_data.variables)
            return return_data
            # return (True, True, False, x0, y0, x1, y1, color, variables)

        # here is where you run the function        
        elif "(" in line: 
            lparen_i = line.find("(")
            revs = line[::-1]
            rparen_i = len(line) - revs.find(")") - 1 # finds right most paren ()
            name = line[:lparen_i].strip()
            vals = line[lparen_i+1:rparen_i]
            if vals == "":
                vals = []
            else:
                vals = [elem.strip() for elem in vals.split(",")]
                # if break is called when you're replacing functions with values?
                vals = [replace_functions_with_values(data, data.fns, 
                    compile_data.variables, expr, compile_data.color, 
                    compile_data.x0, compile_data.y0, compile_data.x1, 
                    compile_data.y1) for expr in vals]
                vals = [eval_expr(data, compile_data.variables, expr, 
                    compile_data.i) for expr in vals]
            if name in data.fns:
                (fn_line_num, args, body) = data.fns[name]
                f_variables = init_variables()
                f_variables["x"] = compile_data.variables["x"]
                f_variables["y"] = compile_data.variables["y"]
                f_variables["color"] = compile_data.variables["color"]
                if len(args) != len(vals):
                    msg = ("function %s requires %d argument(s) but %d were\
 given" % (name, len(args), len(vals)))
                    return create_error(data, msg, compile_data.i)

                for j in range(len(vals)):
                    var_name = args[j]
                    f_variables[var_name] = vals[j]
                # 0, color, 0, x0, y0, x1, y1
                if data.frames != []:
                    # new_compile_data = CompileData("".join(body), *data.frames.pop())
                    result = interpret(data, data.frames.pop())    
                else:
                    new_compile_data = CompileData(
                        code="".join(body),
                        variables=f_variables,
                        color=compile_data.color,
                        x0=compile_data.x0,
                        y0=compile_data.y0,
                        x1=compile_data.x1,
                        y1=compile_data.y1)
                    result = interpret(data, new_compile_data)
                    # result = interpret(data, body, f_variables, 0, color, None, 
                    #     0, x0, y0, x1, y1, depth=depth+4)
                if result is None:
                    if not data.inside_fn:
                        data.err_line = fn_line_num + data.err_line + 1
                    data.inside_fn = True
                    return 
                # (_, terminated, break_called, x0, y0, x1, y1, color, _) = result
                
                compile_data.variables["x"] = f_variables["x"]
                compile_data.variables["y"] = f_variables["y"]
                compile_data.variables["color"] = f_variables["color"]
                
                if result.break_called or result.wait_duration:
                    # terminated keeps track of whether you've completed the inner loop or not
                    if (not result.terminated):
                        frame = CompileData(code=compile_data.code,
                                variables=compile_data.variables,
                                i=compile_data.i,
                                color=compile_data.color,
                                to_repeat=compile_data.to_repeat,
                                x0=compile_data.x0,
                                y0=compile_data.y0,
                                x1=compile_data.x1,
                                y1=compile_data.y1
                                )
                        # frame = (compile_data.variables, compile_data.i, compile_data.color, 
                        #     compile_data.to_repeat, 
                        #     0, compile_data.x0, compile_data.y0, compile_data.x1, 
                        #     compile_data.y1)
                        data.frames.append(frame)
                        return_data = ReturnData(
                            returned=False,
                            terminated=False,
                            break_called=result.break_called,
                            wait_duration=result.wait_duration,
                            x0=compile_data.x0,
                            y0=compile_data.y0,
                            x1=compile_data.x1,
                            y1=compile_data.y1,
                            color=compile_data.color,
                            variables=compile_data.variables)
                        return return_data
            else:
                msg = "%s is not a defined function" % name
                return create_error(data, msg, compile_data.i)

        else:
            msg = "invalid starting keyword: %s" % line
            return create_error(data, msg, compile_data.i)
    
        compile_data.i += 1

    return_data = ReturnData(
        returned=False,
        terminated=True,
        break_called=False,
        x0=compile_data.x0,
        y0=compile_data.y0,
        x1=compile_data.x1,
        y1=compile_data.y1,
        color=compile_data.color,
        variables=compile_data.variables)
    return return_data
    # return (False, True, False, x0, y0, x1, y1, color, variables)

def draw_code(canvas, data):
    draw_window_height = data.canvas_height - data.draw_window_margin*2
    cx = data.draw_window_margin + data.draw_window_width/2
    cy = data.draw_window_margin + draw_window_height/2
    for obj in data.to_draw:
        (x0, y0, x1, y1, color, i, lw) = obj
        try:
            # negating y to account for conversion to graphical coordinates
            # to cartesian coordinates
            canvas.create_line(x0 + cx,
                               -y0 + cy, 
                               x1 + cx, 
                               -y1 + cy, fill=color, width=lw)
        except Exception as e:
            msg = str(e)
            return create_error(data, msg, i)
    for text_obj in data.to_write:
        (text, anchor, font, x, y, i) = text_obj
        try:
            canvas.create_text(cx + x, cy - y, text=text, anchor=anchor, font=font)
        except Exception as e:
            print(e)
            return create_error(data, str(e), i)

def draw_axes(canvas, data):
    cwidth = canvas.winfo_width()
    cheight = canvas.winfo_height()
    offset = data.draw_window_margin
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
    data.axes = False

def init_compile_data(data):
    data.fns = dict()
    data.inside_fn = False
    data.error = False
    data.err_msg = ""
    data.err_line = 0
    data.code = data.textbox.get_text()
    data.default_line_width = 5
    data.to_draw = []
    data.to_write = []
    data.frames = []
    data.print_string = []

def init_variables():
    variables = dict()
    variables['x'] = 0
    variables['y'] = 0
    variables['color'] = None
    variables['True'] = 1
    variables['False'] = 0
    # variables['return'] = None
    return variables

def init(data):
    init_GUI(data)
    init_compile_data(data)
    
    data.debug_mode = False
    data.type_mode = False
    data.wait_timer = 0
    data.start = time.time()
     # each string in this list should be separated by new line
    data.help = False
    data.ver = None
    variables = init_variables()

def mousePressed(event, data):
    pass

def updateconsole(data):
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
        p = "\n".join(data.print_string)
        #clear the console
        data.console.configure(state="normal")
        data.console.delete('1.0', END)
        data.console.insert(tkinter.INSERT, p)
        data.console.configure(state="disabled")

def saveandrun(data):
    savecode(data)
    runcode(data)

def runcode(data):
    init_compile_data(data)
    code_lines, data.ln_map = filter_space(data.code.splitlines(), 
                                           data.debug_mode)
    data.code = "\n".join(code_lines)
    variables = init_variables()
    compile_data = CompileData(data.code, variables=variables)
    return_data = interpret(data, compile_data)
    updateconsole(data)
    if return_data is not None and return_data.wait_duration:
        wait(data, return_data.wait_duration)

def sleeper(s, status_queue, lock):
    time.sleep(s)
    with lock:
        status_queue.put(True)

def start_timer(data, duration):
    data.wait_timer = duration
    data.start = time.time()

def wait(data, duration):
    data.canvas.delete(ALL)
    redrawAll(data.canvas, data)
    data.canvas.update()
    start_timer(data, duration)

def savecode(data):
    data.textbox.save(data.ver)

def saveascode(data):
    data.textbox.saveas()

def loadcode(data):
    init(data)
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
    print("data.frames", data.frames)
    if not data.frames:
        return 
    while len(data.frames) > 0:
        frame = data.frames.pop()
        # new_compile_data = CompileData(data.code, *frame)
        result = interpret(data, frame)
        updateconsole(data)
        if result is None: # an error occured
            data.frames = []
            return 
        elif result.break_called:
            return

        elif result.wait_duration:
            return wait(data, result.wait_duration)


def keyPressed(event, data):
    data.textbox.color()

def timerFired(data):
    if data.wait_timer and (time.time() - data.start > data.wait_timer):
        data.wait_timer = 0
        data.start = time.time()
        stepdebug(data)


def draw_screens(canvas, data):
    canvas.create_rectangle(data.draw_window_margin, data.draw_window_margin,
                            data.canvas_width-data.draw_window_margin, 
                           data.canvas_height, width=3)


def redrawAll(canvas, data):
    if data.axes:
        draw_axes(canvas, data)
    if not data.error:
        draw_code(data.canvas, data)
    

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

        self.keywords = ["if", "while", "repeat", "else", "elif", "<-"]
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
        self.filename =  filedialog.asksaveasfilename(initialdir = "../../",title = "Select file", defaultextension=".sda")
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
        self.filename =  filedialog.askopenfilename(initialdir = "../../",title = "Select file", filetypes=[('Saada file','*.sda')])
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
                             command=lambda: saveandrun(data), accelerator="Ctrl+R")
    tools_menu.add_command(label="Toggle Axes",  underline=1,
        command=lambda: toggleaxes(data),  accelerator="Ctrl+A")
    tools_menu.add_command(label="Toggle Debug", underline=1, 
        command=lambda: toggledebug(data), accelerator="Ctrl+D")
    tools_menu.add_command(label="Step", underline=1, 
        command=lambda: stepdebug(data), accelerator="Ctrl+E")

    root.bind_all("<Control-r>", lambda e: saveandrun(data))
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
    data.timerDelay = 10 # milliseconds
    data.textbox_width = width//2
    data.canvas_width = width//2
    data.canvas_height = height*(5/8)
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
