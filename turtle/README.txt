Saada

This is a visual programming tool to introduce code to beginners. There are 3 
main variables that can be manipulated to draw on the graph: x, y, color. 
Imagine a paintbrush that starts at the origin of the graph (Ctrl + a to view 
axes), you can move the paintbrush to various points in the plane by changing 
the x and y coordinates and naturally change color by setting the color 
variable. 

Global variables:
    
    x                       integer; defines x coordinate of 'paintbrush'
    
    y                       integer; defines y coordinate of 'paintbrush'
    
    color                   string; defines color of 'paintbrush'

Types:

    integer                 e.g. 0, 1, 2, 42

    string                  e.g. "blue", "green", "hello world"

Basic Syntax: 
    comments                # this is a comment
    
    if statement            if(<condition>):
    
    else statement          else:
    
    while loop              while(<condition>):
    
    for loop                repeat <nonnegative number>:
    
    print                   print(<argument>)
    
    variable assignment     <- 

    wait                    wait(<a number in seconds>)

 Using Functions
     
     define a function       def fn_name(arg1, arg2)
     
     return an argument      return <value> 
 
 Debug Syntax and Use:
     
     activate debug mode     Control + d

     step in debug mode      Control + e
     
     break statement         break
              
 Draw Syntax:
     
     coordinates for drawing (x,y)
     
     default start point     (0,0)
    
     color of line           color 
     
     draw([width])           draws from second to last point to last point set, 
                             optionally accepts integer argument for line width

 Sample Code (also in sample.sda):

    def f(t):
         x<-t+10
         color<-"blue"
         draw()
 
    f(10)
    break
 
    def g(n, m):
        repeat n:
            print("this is x")
            print(x)
            x<-x+m
            color<-"black"
            draw(5)
 
    g(1, 10)
    break
    g(3, 10)