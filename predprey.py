#! /usr/bin/env python
"""
Solves the predator/prey problem
"""

import sys
import os
import time
import socket
import string
import random

HOST = 'localhost'
PORT = 23000
start_time = time.time()
walls = []
side = ""

def usage():
    sys.stdout.write( __doc__ % os.path.basename(sys.argv[0]))

class GameState:
    def __init__(self,hunter,prey,walls):
        h = hunter
        p = prey
        w = walls

    def __repr__(self):
        return "Hunter:\n%s\nPrey:\n%s\nWalls:\n%s\n" % \
               (repr(h),repr(p),repr(w))

class Wall:
    def __init__(self,ident,x1,y1,x2,y2):
        ident = ident
        x1 = x1
        y1 = y1
        x2 = x2
        y2 = y2

    def __repr__(self):
        return "%s (%s, %s), (%s, %s)" \
           % (repr(r),repr(x1),repr(y1),repr(x2),repr(y2))

class Hunter:
    def __init__(self,x,y,cd=0,d="SE"):
        x = x
        y = y
        cd = cd
        d = d

    def __repr__(self):
        return "x: %s\ty: %s\tcd: %s\td: %s" % \
               (repr(x),repr(y),repr(cd),repr(d))

class Prey:
    def __init__(self,x,y,cd=0):
        x = x
        y = y
        cd = cd

    def __repr__(self):
        return "x: %s\ty: %s\tcd: %s" % \
               (repr(x),repr(y),repr(cd))

def NewWall(x1,y1,x2,y2):
    """
    wrapper for creating an instance of the wall class:
    adds a wall to the walls array and returns the
    string to send to the server to add the wall
    """
    bad_num = False
    r = random.random(1,9999)
    while True:
        for w in walls:
            if r == w.ident:
                bad_num = True
        if not bad_num:
            break
        else:
            r = random.random(1,9999)

    w = Wall(r,x1,y1,x2,y2)
    walls.append(w)
    return "ADD",repr(w)
    
def make_move(line):
    """
    line will be in the form:
    YOURTURN _ROUNDNUMBER_ H(x, y, cooldown, direction),
    P(x, y, cooldown), W[wall_one, wall_two]
    """
    a = line.split()

    round_num = a[1]

    hunt_x = int(a[2].split("(")[1].strip(","))
    hunt_y = int(a[3].strip(","))
    hunt_cd = int(a[4].strip(","))
    hunt_dir = a[5].strip(",").strip(")")

    prey_x = int(a[6].split("(")[1].strip(","))
    prey_y = int(a[7].strip(","))
    prey_cd = int(a[8].strip(",").strip(")"))

    offset = 0
    while True:
        wall_id = int(a[9+offset].split("(")[1].strip(","))
        wall_x1 = int(a[10+offset].strip(","))
        wall_y1 = int(a[11+offset].strip(","))
        wall_x2 = int(a[12+offset].strip(","))
        t = a[13+offset]
        wall_y2 = int(t.strip(",").strip(")"))
        w = Wall(wall_id,wall_x1,wall_y1,wall_x2,wall_y2)
        print w
        walls.append(w)
        if ")]" in t:
            break

    g = GameState(Hunter(hunt_x,hunt_y,hunt_cd,hunt_dir),\
                  Prey(prey_x,prey_y,prey_cd),\
                  walls)

    print g

    if side == "HUNTER":
        print "IM A HUNTER RAAAWR"
    elif side == "PREY":
        print "IM A PREY.... FFFFFUUUUUUUUUUU"
    else:
        print "WTF?"


## From:
## Charles J. Scheffold
## cjs285@nyu.edu
def SReadLine (conn):
    data = ""
    while True:
        c = conn.recv(1)
        if not c:
            time.sleep (1)
            break
        data = data + c
        if c == "\n":
            break
    return data

if __name__ == "__main__":

    if len(sys.argv) != 1:
        usage()
        sys.exit(1)

    # Open connection to evasion server
    s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    s.connect ((HOST, PORT))
    print "Connected to", HOST, "port", PORT

    accepted = False
    game_on = False

    s.send("JOIN MAX")

    # Read status line
    data = SReadLine (s)
    line = string.strip (data)

    if line == "ACCEPTED HUNTER":
        side = "HUNTER"
    elif line == "ACCEPTED PREY":
        side = "PREY"

    # Now get the game parameters
    data = SReadLine (s)
    line = string.strip (data)

    data = SReadLine (s)
    line = string.strip (data)

    xdim, ydim, wallcount, wallcd, preycd = 0

    # TODO - dynamic?
    xdim = 500
    ydim = 500
    wallcount = 1
    wallcd = 10
    preycd = 1

    while True:
        # Read one line from server
        data = SReadLine (s)

        # If it's empty, we are finished here
        if data == None or data == '' or "GAMEOVER" in data:
            print "GAMEOVER:",data
            break

        # Strip the newline
        line = string.strip (data)
        print line

        if "YOUTURN" in line:
            make_move(line)

    # Poof!
    s.close ()

    print "Time: ",round(time.time() - start_time)
