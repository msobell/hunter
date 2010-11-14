#! /usr/bin/env python
"""
Solves the predator/prey problem
"""

import sys
import os
import time
import socket
import string

HOST = 'localhost'
PORT = 23000
start_time = time.time()

side = ""

def usage():
    sys.stdout.write( __doc__ % os.path.basename(sys.argv[0]))

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
