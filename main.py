
import enum
import random
from tkinter import ACTIVE
from tokenize import String
from typing import List, Tuple
from matplotlib import blocking_input
import pygame as engine
import json
import math

jsonfile = open('gamesettings.json')
engineconfig = json.load(jsonfile)
jsonfile.close()


def euclideanDistance(p1: Tuple[int, int], p2: Tuple[int, int]):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1-x2)**2+(y1-y2)**2)


class Action(enum.Enum):
    North = 1
    South = 2
    East = 3
    West = 4
    NorthEast = 5
    NorthWest = 6
    SouthEast = 7
    SouthWest = 8


class World:
    def __init__(self) -> None:
        self._size = engineconfig["MapRadius"]
        self._map = [[] for _ in range(engineconfig["MapRadius"]*2)]
        self._players = []
        blnNext = True
        random.seed(engineconfig["Food"]["Seed"])
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                if(euclideanDistance((engineconfig["MapRadius"], engineconfig["MapRadius"]), (r, c)) >= engineconfig["MapRadius"]):
                    self._map[r].append(engineconfig["Zone"]["Reward"])
                else:
                    n = random.randint(0, engineconfig["Food"]["Probability"])
                    if(blnNext and n == engineconfig["Food"]["Probability"]):
                        self._map[r].append(engineconfig["Food"]["Reward"])
                        blnNext = not blnNext
                    else:
                        self._map[r].append(engineconfig["Reward"])
                        blnNext = not blnNext

        blnNext = True
        random.seed(engineconfig["BoostPad"]["Seed"])
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                if(not euclideanDistance((engineconfig["MapRadius"], engineconfig["MapRadius"]), (r, c)) >= engineconfig["MapRadius"]):
                    n = random.randint(
                        0, engineconfig["BoostPad"]["Probability"])
                    if(blnNext and n == engineconfig["BoostPad"]["Probability"]):
                        self._map[r][c] = engineconfig["BoostPad"]["Reward"]

        blnNext = True
        random.seed(engineconfig["Meteor"]["Seed"])
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                if(not euclideanDistance((engineconfig["MapRadius"], engineconfig["MapRadius"]), (r, c)) >= engineconfig["MapRadius"]):
                    n = random.randint(
                        0, engineconfig["Meteor"]["Probability"])
                    if(blnNext and n == engineconfig["Meteor"]["Probability"]):
                        self._map[r][c] = engineconfig["Meteor"]["Reward"]

        for p in engineconfig["Players"]:
            if(p["Active"]):
                self._players.append({"Name": p["Name"],
                                      "Path": p["Path"],
                                      "Reward": p["Reward"], "r": 0, "c": 0})

        dist = engineconfig["MapRadius"]/2
        r = dist
        c = 0
        blnSide = True
        for p in self._players:
            if(blnSide):
                c += dist
                self._map[math.floor(r)][math.floor(c)] = p["Name"]
                p["r"] = math.floor(r)
                p["c"] = math.floor(c)
                c += dist*2
                blnSide = not blnSide
            else:
                self._map[math.floor(r)][math.floor(c)] = p["Name"]
                p["r"] = math.floor(r)
                p["c"] = math.floor(c)
                r += dist*2
                c -= dist*3
                blnSide = not blnSide

    def updateZone(self):
        self._size -= 1
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                if(euclideanDistance((engineconfig["MapRadius"], engineconfig["MapRadius"]), (r, c)) >= self._size):
                    self._map[r][c] = engineconfig["Zone"]["Reward"]

    def getMoves(self, pName: str) -> List[Action]:
        actions = List[Action]
        for p in self._players:
            if(p["Name"] == pName):
                if(p["r"]-1 >= 0):
                    actions.append(Action.North)
                if(p["r"]+1 < engineconfig["MapRadius"]*2):
                    actions.append(Action.South)
                if(p["c"]+1 < engineconfig["MapRadius"]*2):
                    actions.append(Action.East)
                if(p["c"]-1 >= 0):
                    actions.append(Action.West)
                if(p["r"]-1 >= 0 and p["c"]+1 < engineconfig["MapRadius"]*2):
                    actions.append(Action.NorthEast)
                if(p["r"]-1 >= 0 and p["c"]-1 >= 0):
                    actions.append(Action.NorthWest)
                if(p["r"]+1 < engineconfig["MapRadius"]*2 and p["c"]-1 >= 0):
                    actions.append(Action.SouthWest)
                if(p["r"]+1 < engineconfig["MapRadius"]*2 and p["c"]+1 < engineconfig["MapRadius"]*2):
                    actions.append(Action.SouthEast)
        return actions

    def move(self, pName: str, action: Action):
        r = 0
        c = 0
        for p in self._players:
            if(p["Name"] == pName):
                if(action == Action.North):
                    r = p["r"]-1
                    c = p["c"]
                if(action == Action.South):
                    r = p["r"]+1
                    c = p["c"]
                if(action == Action.East):
                    r = p["r"]
                    c = p["c"]+1
                if(action == Action.West):
                    r = p["r"]
                    c = p["c"]-1
                if(action == Action.NorthEast):
                    r = p["r"]-1
                    c = p["c"]+1
                if(action == Action.NorthWest):
                    r = p["r"]-1
                    c = p["c"]-1
                if(action == Action.SouthWest):
                    r = p["r"]+1
                    c = p["c"]-1
                if(action == Action.SouthEast):
                    r = p["r"]+1
                    c = p["c"]+1

                if(r >= 0 and r < engineconfig["MapRadius"]*2 and c >= 0 and c < engineconfig["MapRadius"]*2):
                    self._map[p["r"]][p["c"]] = engineconfig["Reward"]
                    print(r)
                    p["r"] = r
                    p["c"] = c
                    self._map[r][c] = p["Name"]

    def gameOver(self) -> bool:
        if self._size < 0:
            return True
        return False


class Environment:
    def __init__(self) -> None:
        self._running = True
        self._gridsize = engineconfig["GridSize"]
        self._game = World()
        self._size = engineconfig["MapRadius"]*2*self._gridsize
        self._window = engine.display.set_mode((self._size, self._size))
        engine.display.set_caption('SpaceWars')
        self._bgimage = engine.image.load(engineconfig["Path"])
        self._window.blit(self._bgimage, (0, 0))
        self._zone = engine.transform.scale(engine.image.load(
            engineconfig["Zone"]["Path"]), (self._gridsize, self._gridsize))
        self._food = engine.transform.scale(engine.image.load(
            engineconfig["Food"]["Path"]), (self._gridsize, self._gridsize))
        self._meteor = engine.transform.scale(engine.image.load(
            engineconfig["Meteor"]["Path"]), (self._gridsize, self._gridsize))
        self._boostpad = engine.transform.scale(engine.image.load(
            engineconfig["BoostPad"]["Path"]), (self._gridsize, self._gridsize))

    def draw(self):
        self._window.blit(self._bgimage, (0, 0))
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                if self._game._map[r][c] == engineconfig["Zone"]["Reward"]:
                    self._window.blit(
                        self._zone, (c*self._gridsize, r*self._gridsize))
                if self._game._map[r][c] == engineconfig["Food"]["Reward"]:
                    self._window.blit(
                        self._food, (c*self._gridsize, r*self._gridsize))
                if self._game._map[r][c] == engineconfig["Meteor"]["Reward"]:
                    self._window.blit(
                        self._meteor, (c*self._gridsize, r*self._gridsize))
                if self._game._map[r][c] == engineconfig["BoostPad"]["Reward"]:
                    self._window.blit(
                        self._boostpad, (c*self._gridsize, r*self._gridsize))
                if self._game._map[r][c] == engineconfig["Players"][0]["Name"]:
                    self._window.blit(
                        engine.transform.scale(engine.image.load(
                            engineconfig["Players"][0]["Path"]), (self._gridsize, self._gridsize)), (c*self._gridsize, r*self._gridsize))
                if self._game._map[r][c] == engineconfig["Players"][1]["Name"]:
                    self._window.blit(
                        engine.transform.scale(engine.image.load(
                            engineconfig["Players"][1]["Path"]), (self._gridsize, self._gridsize)), (c*self._gridsize, r*self._gridsize))
                if self._game._map[r][c] == engineconfig["Players"][2]["Name"]:
                    self._window.blit(
                        engine.transform.scale(engine.image.load(
                            engineconfig["Players"][2]["Path"]), (self._gridsize, self._gridsize)), (c*self._gridsize, r*self._gridsize))
                if self._game._map[r][c] == engineconfig["Players"][3]["Name"]:
                    self._window.blit(
                        engine.transform.scale(engine.image.load(
                            engineconfig["Players"][3]["Path"]), (self._gridsize, self._gridsize)), (c*self._gridsize, r*self._gridsize))

        # Update the display using flip
        engine.display.flip()

    def run(self):
        time_interval = engineconfig["Tick"]
        object_time = 0
        clock = engine.time.Clock()
        # game loop
        while self._running:
            clock.tick(engineconfig["FPS"])
            current_time = engine.time.get_ticks()
            if current_time > object_time:
                object_time += time_interval
                if(((object_time/engineconfig["Zone"]["Tick"]).is_integer())):
                    self._game.updateZone()

            # for loop through the event queue
            for event in engine.event.get():
                # Check for QUIT event
                if event.type == engine.QUIT:
                    self._running = False
            self.draw()
            """ if self._game.gameOver():
                self._continue = False
                engine.quit() """

if __name__ == "__main__":
    env = Environment()
    env.run()
