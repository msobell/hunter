#! /usr/bin/env python
"""
Solves the predator/prey problem
Usage: predprey.py <join name>
"""

import sys
import os
import time
import socket
import string
import random
import copy

HOST = 'localhost'
PORT = 23000
start_time = time.time()
walls = []
side = ""
turn = 0

def usage():
    sys.stdout.write( __doc__ % os.path.basename(sys.argv[0]))

class GameState:
    def __init__(self,hunter,prey,walls):
        self.h = hunter
        self.p = prey
        self.w = walls
        self.area = 0
        self.maxx = 499
        self.maxy = 499
        self.minx = 0
        self.miny = 0

    def __repr__(self):
        return "Hunter:\n%s\nPrey:\n%s\nBoundaries:\nminx=%s\tmaxx=%s\tminy=%s\tmaxy=%s\n" % \
               (repr(self.h),repr(self.p),repr(self.minx),repr(self.maxx),repr(self.miny),repr(self.maxy))

    def score(self):
        # Assume all walls are spanning. This is cheating.
        # This also assumes the hunter won't isolate the prey.
        # The second assumption is both stupid AND lazy.
        # I'm also sure there is a better way to do this.

        for wall in self.w:
            
            if wall.isVert():
                # x1 == x2
                if wall.x1 < self.maxx and wall.x1 > self.p.x:
                    self.maxx = wall.x1
                elif wall.x1 > self.minx and wall.x1 < self.p.x:
                    self.minx = wall.x1

            else:
                # y1 == y2
                if wall.y1 < self.maxy and wall.y1 > self.p.y:
                    self.maxy = wall.y1
                elif wall.y1 > self.miny and wall.y1 < self.p.y:
                    self.miny = wall.y1
            
        self.area = (self.maxx - self.minx) * \
                    (self.maxy - self.miny)

        return self.area
        
class Wall:
    def __init__(self,ident,x1,y1,x2,y2):
        self.ident = ident
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __repr__(self):
        return "%s (%s, %s), (%s, %s)" \
           % (repr(self.ident),repr(self.x1),\
              repr(self.y1),repr(self.x2),repr(self.y2))

    def isVert(self):
        return self.x1 == self.x2

class Hunter:
    def __init__(self,x,y,cd=0,d="SE"):
        self.x = x
        self.y = y
        self.cd = cd
        self.d = d

    def __repr__(self):
        return "x: %s\ty: %s\tcd: %s\td: %s" % \
               (repr(self.x),repr(self.y),repr(self.cd),repr(self.d))

class Prey:
    def __init__(self,x,y,cd=1):
        self.x = x
        self.y = y
        self.cd = cd

    def __repr__(self):
        return "x: %s\ty: %s\tcd: %s" % \
               (repr(self.x),repr(self.y),repr(self.cd))

def make_move(g):
    print "Current Score:",g.score()
    if side == "HUNTER":
        # if your cooldown is up
        # find the best place for a wall
        # and place it
        all_walls = []
        if turn == 1:
            return "ADD " + repr(NewWall(True,202,g))
        elif g.h.cd == 0: # hunter's cooldown is 0
            # move!
            # find out which side of the prey we're on
            if g.h.x < g.p.x:
                # we're on the left side of the prey
                # so look at the right side of the prey
                all_walls.append(NewWall(False,g.p.x+1,g))
                # and the left side of us
                all_walls.append(NewWall(False,g.h.x-1,g))
            else:
                all_walls.append(NewWall(False,g.p.x-1,g))
                all_walls.append(NewWall(False,g.h.x+1,g))

            if g.h.y < g.p.y:
                # we're below the prey
                # so look at above the prey
                all_walls.append(NewWall(True,g.p.y+1,g))
                # and below us
                all_walls.append(NewWall(True,g.h.y-1,g))
            else:
                all_walls.append(NewWall(True,g.p.y-1,g))
                all_walls.append(NewWall(True,g.h.y+1,g))
                
            min_game = g
            min_wall = all_walls[0]
            for wall in all_walls:
                game = copy.deepcopy(g)
                game.w.append(wall)
                print "Game score: %s for wall %s" % (repr(game.score()),repr(wall))
                if game.score() < min_game.score():
                    min_game = game
                    min_wall = wall

            if len(g.w) == 6:
                print "REMOVING A WALL!"
                horiz_walls = []
                vert_walls = []
                for wall in min_game.w:
                    if wall.isVert():
                        vert_walls.append(wall)
                    else:
                        horiz_walls.append(wall)

                if len(horiz_walls) > len(vert_walls):
                    new_walls = sorted(horiz_walls, key=lambda Wall: Wall.y1)
                else:
                    new_walls = sorted(vert_walls, key=lambda Wall: Wall.x1)

                i = 0
                if new_walls[0].isVert():
                    while new_walls[i].x1 < g.h.x:
                        i += 1
                else:
                    while new_walls[i].y1 < g.h.y:
                        i += 1

                # now i points to the element above/to the right
                # of the hunter. go one more (if it exists) and
                # remove it

                if i < len(new_walls) - 2:
                    old_wall = new_walls[-1].ident
                else:
                    old_wall = new_walls[0].ident

                return "REMOVE " + repr(old_wall) + "\n"

            return "ADD " + repr(min_wall)
        else:
            return "PASS"
    elif side == "PREY":
        # if your cooldown is up
        # find where the hunter is headed
        # find the closest boundary
        # move towards the midpoint
        moves = ['N','S','E','W','NE','NW','SE','SW']
        # return moves[random.randint(0,len(moves)-1)]
        if g.p.cd == 0: # prey's cooldown is 0
            # find where hunter will be next turn
            # g.h.x and g.h.y
            # dir = g.h.d
            # find out where the closest wall to the prey is
            # g.maxx g.maxy g.minx g.miny
            # find out where the middle is
            hx = g.h.x
            hy = g.h.y
            px = g.p.x
            py = g.p.y
            print "px,py",px,py
            if 'N' in g.h.d:
                hy += 1
                if py > (g.miny + 1):
                    py -= 1
            else:
                hy -= 1
                if py > (g.maxy - 1):
                    py += 1

            if 'E' in g.h.d:
                hx += 1
                if px > (g.minx + 1):
                    px -= 1
            else:
                hx -= 1
                if px > (g.maxx - 1):
                    px += 1

            # # top
            # if (g.p.y - g.miny) > (g.maxy - g.p.y):
            #     py += 1
            # # bottom
            # else:
            #     py -= 1

            # head for that

            # py -= 1
            
            print "moved px,py",px,py
            return "%s, %s" % (repr(px),repr(py))
        else:
            print "CD NOT 0",g.p.cd
            return "PASS"
    else:
        print "WTF?"

def NewWall(isHoriz,XorY,g):
    """
    wrapper for creating an instance of the wall class:
    adds a wall to the walls array and returns the
    string to send to the server to add the wall
    """

    max_ident = 0
    for w in g.w:
        if w.ident > max_ident:
            max_ident = w.ident

    r = max_ident + 1
    x1, y1, x2, y2 = [0,0,0,0]
    g.score()
    if isHoriz:
        # only need y value
        y1 = y2 = XorY
        # spanning wall
        x1 = g.minx
        x2 = g.maxx-1
    else:
        x1 = x2 = XorY
        y1 = g.miny
        y2 = g.maxy-1
    w = Wall(r,x1,y1,x2,y2)
    return w
    
def MakeGS(line):
    """
    line will be in the form:
    YOURTURN _ROUNDNUMBER_ H(x, y, cooldown, direction),
    P(x, y, cooldown), W[wall_one, wall_two]

    This very confusing function parses this protocol
    to create a GameState object, and then calls
    make_move to make the actual move.
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
    walls = []

    while True:
        if a[9+offset] == "W[]":
            break
        else:
            wall_id = int(a[9+offset].split("(")[1].strip(","))
            wall_x1 = int(a[10+offset].strip(","))
            wall_y1 = int(a[11+offset].strip(","))
            wall_x2 = int(a[12+offset].strip(","))
            t = a[13+offset]
            wall_y2 = int(t.strip("]").strip(",").strip(")"))
            w = Wall(wall_id,wall_x1,wall_y1,wall_x2,wall_y2)
            walls.append(w)
            offset += 5
            if "]" in t:
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

    return g

## From:
## Charles J. Scheffold
## cjs285@nyu.edu
def SReadLine (conn):
    data = ""
    while True:
        c = conn.recv(1)
        if not c:
            time.sleep(1)
            break
        data = data + c
        if c == "\n" or c == "\r":
            print data
            break
    return data

if __name__ == "__main__":

    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    # Open connection to evasion server
    s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    s.connect ((HOST, PORT))
    print "Connected to", HOST, "port", PORT

    join = "JOIN" + repr(sys.argv[1]) + "\n"
    s.send(join)

    # Read status line
    data = SReadLine (s)
    line = string.strip (data)

    if line == "ACCEPTED HUNTER":
        side = "HUNTER"
    elif line == "ACCEPTED PREY":
        side = "PREY"

    print side

    # Now get the game parameters
    data = SReadLine (s)
    line = string.strip (data)

    # TODO - dynamic?
    xdim = 500
    ydim = 500
    wallcount = 6
    wallcd = 25
    preycd = 1

    while True:
        turn += 1
        print "in loop",turn
        # Read one line from server
        data = SReadLine (s)

        # If it's empty, we are finished here
        if data == None or data == '' or "GAMEOVER" in data:
            print "GAMEOVER:",data
            break

        # Strip the newline
        line = string.strip (data)
        print "Line:",line

        if "YOURTURN" in line:
            GS = MakeGS(line)
            move = make_move(GS)
            print "Move",move
            s.send(move + "\n")

    # Poof!
    s.close ()

    print "Time: ",round(time.time() - start_time)
