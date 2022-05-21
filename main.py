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
engine.init()
font = engine.font.SysFont("arial", 20)
big_font = engine.font.SysFont("arial", 30)


def euclideanDistance(p1: Tuple[int, int], p2: Tuple[int, int]):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1-x2)**2+(y1-y2)**2)


class Action(enum.Enum):
    North = 1
    South = 2
    East = 3
    West = 4
    """ NorthEast = 5
    NorthWest = 6
    SouthEast = 7
    SouthWest = 8 """


class QTable():
    def __init__(self, lstActions: List[Action]):
        self._map = [[] for _ in range(2 ^ 4)]

        for r in range(2 ^ 4):
            for _ in range(3 ^ 8):
                dictQ = {}
                for a in lstActions:
                    dictQ[a] = 0.0
                self._map[r].append(dictQ)

    def getBestQ(self, tplCoord: Tuple[int, int]) -> Tuple[Action, float]:
        qs = self[tplCoord]
        qbest = list(qs.values())[0]
        abest = list(qs.keys())[0]

        for a, q in qs.items():
            if q > qbest:
                qbest = q
                abest = a
        return (abest, qbest)


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

        """ blnNext = True
        random.seed(engineconfig["BoostPad"]["Seed"])
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                if(not euclideanDistance((engineconfig["MapRadius"], engineconfig["MapRadius"]), (r, c)) >= engineconfig["MapRadius"]):
                    n = random.randint(
                        0, engineconfig["BoostPad"]["Probability"])
                    if(blnNext and n == engineconfig["BoostPad"]["Probability"]):
                        self._map[r][c] = engineconfig["BoostPad"]["Reward"] """

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
                                      "isAlive": True,
                                      "Score": p["Size"], "r": 0, "c": 0})

        dist = engineconfig["MapRadius"]/2
        r = dist
        c = 0
        blnSide = True
        for p in self._players:
            if(blnSide):
                c += dist
                p["r"] = math.floor(r)
                p["c"] = math.floor(c)
                c += dist*2
                blnSide = not blnSide
            else:
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

    def update(self):
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                for pl in self._players:
                    if(self._map[r][c] == engineconfig["Zone"]["Reward"]):
                        if(pl["r"] == r and pl["c"] == c):
                            pl["isAlive"] = False

        for p in self._players:
            for otherP in self._players:
                if(otherP["Name"] != p["Name"]):
                    if(otherP["r"] == p["r"] and otherP["c"] == p["c"]):
                        if(otherP["Score"] > p["Score"]):
                            p["isALive"] = False
                            p["Score"] -= engineconfig["PlayerReward"]
                        elif (otherP["Score"] < p["Score"]):
                            otherP["isAlive"] = False
                            p["Score"] += engineconfig["PlayerReward"]

            if self._map[p["r"]][p["c"]] == engineconfig["Food"]["Reward"]:
                p["Score"] += engineconfig["Food"]["Reward"]
            if self._map[p["r"]][p["c"]] == engineconfig["Meteor"]["Reward"]:
                p["Score"] += engineconfig["Meteor"]["Reward"]
            if self._map[p["r"]][p["c"]] == engineconfig["BoostPad"]["Reward"]:
                p["Score"] += engineconfig["BoostPad"]["Reward"]
            if self._map[p["r"]][p["c"]] == engineconfig["Zone"]["Reward"]:
                p["Score"] += engineconfig["Zone"]["Reward"]
            else:
                p["Score"] += engineconfig["Reward"]
                self._map[p["r"]][p["c"]] = engineconfig["Reward"]

    def getMoves(self, pName: str) -> List[Action]:
        actions = list()
        for p in self._players:
            if(p["Name"] == pName):
                if(p["isAlive"]):
                    if(p["r"]-1 >= 0):
                        actions.append(Action.North)
                    if(p["r"]+1 < engineconfig["MapRadius"]*2):
                        actions.append(Action.South)
                    if(p["c"]+1 < engineconfig["MapRadius"]*2):
                        actions.append(Action.East)
                    if(p["c"]-1 >= 0):
                        actions.append(Action.West)
                    """ if(p["r"]-1 >= 0 and p["c"]+1 < engineconfig["MapRadius"]*2):
                        actions.append(Action.NorthEast)
                    if(p["r"]-1 >= 0 and p["c"]-1 >= 0):
                        actions.append(Action.NorthWest)
                    if(p["r"]+1 < engineconfig["MapRadius"]*2 and p["c"]-1 >= 0):
                        actions.append(Action.SouthWest)
                    if(p["r"]+1 < engineconfig["MapRadius"]*2 and p["c"]+1 < engineconfig["MapRadius"]*2):
                        actions.append(Action.SouthEast) """
        return actions

    def move(self, pName: str, action: Action):
        if action in self.getMoves(pName):
            r = 0
            c = 0
            for p in self._players:
                if(p["Name"] == pName):
                    if(p["isAlive"]):
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
                        """ if(action == Action.NorthEast):
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
                            c = p["c"]+1 """

                        if(r >= 0 and r < engineconfig["MapRadius"]*2 and c >= 0 and c < engineconfig["MapRadius"]*2):
                            p["r"] = r
                            p["c"] = c

    def gameOver(self) -> bool:
        if self._size < 0:
            return True
        return False


class Environment:
    def __init__(self, intEpisodes: int) -> None:
        self._running = True
        self._gridsize = engineconfig["GridSize"]
        self._game = World()
        self._size = engineconfig["MapRadius"]*2*self._gridsize
        self._window = engine.display.set_mode(
            (self._size + engineconfig["LeaderboardSize"], self._size))
        engine.display.set_caption('SpaceWars')
        self._bgimage = engine.transform.scale(
            engine.image.load(engineconfig["Path"]), (self._size, self._size))
        self._window.blit(self._bgimage, (0, 0))
        self._zone = engine.transform.scale(engine.image.load(
            engineconfig["Zone"]["Path"]), (self._gridsize, self._gridsize))
        self._food = engine.transform.scale(engine.image.load(
            engineconfig["Food"]["Path"]), (self._gridsize, self._gridsize))
        self._meteor = engine.transform.scale(engine.image.load(
            engineconfig["Meteor"]["Path"]), (self._gridsize, self._gridsize))
        self._boostpad = engine.transform.scale(engine.image.load(
            engineconfig["BoostPad"]["Path"]), (self._gridsize, self._gridsize))
        self._leaderboard = engine.Surface(
            (engineconfig["LeaderboardSize"], self._size), engine.SRCALPHA)
        self._leaderboard.fill((255, 255, 255))
        self._agentR = ReferenceAgent(self, "Finalizer")

    def draw(self):
        self._window.blit(self._bgimage, (0, 0))
        self._window.blit(self._leaderboard, (self._size, 0))
        self._window.blit(big_font.render("Leaderboard", 0, (0, 0, 0)),
                          (self._size+20, 20))

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
        intPLoc = 1
        for p in self._game._players:
            self._window.blit(engine.transform.scale(engine.image.load(
                p["Path"]), (self._gridsize+5, self._gridsize+5)), (self._size+20, 32+30*intPLoc))
            self._window.blit(font.render(
                p["Name"] + ": "+str(p["Score"]), 1, (0, 0, 0)), (self._size+50, 30+30*intPLoc))
            if(p["isAlive"]):
                self._window.blit(
                    engine.transform.scale(engine.image.load(p["Path"]), (self._gridsize, self._gridsize)), (p["c"]*self._gridsize, p["r"]*self._gridsize))
            intPLoc += 1

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
                self._game.move("Millennium Falcon", Action.East)
                self._agentR.act()
                self._game.update()

            # for loop through the event queue
            for event in engine.event.get():
                # Check for QUIT event
                if event.type == engine.QUIT:
                    self._running = False
            self.draw()
            """ if self._game.gameOver():
                self._continue = False
                engine.quit() """


class ReferenceAgent:
    def __init__(self, env: Environment, pName: str):
        self._env = env
        for p in self._env._game._players:
            if(p["Name"] == pName):
                self._pName = p

    def act(self) -> None:
        a: List[Action] = self._env._game.getMoves(self._pName["Name"])
        if(self._env._game._map[self._pName["r"]+2][self._pName["c"]] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._pName["r"]+2][self._pName["c"]] == engineconfig["Meteor"]["Reward"]):
            a.remove(Action.South)
        if(self._env._game._map[self._pName["r"]-2][self._pName["c"]] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._pName["r"]-2][self._pName["c"]] == engineconfig["Meteor"]["Reward"]):
            a.remove(Action.North)
        if(self._env._game._map[self._pName["r"]][self._pName["c"]+2] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._pName["r"]][self._pName["c"]+2] == engineconfig["Meteor"]["Reward"]):
            a.remove(Action.East)
        if(self._env._game._map[self._pName["r"]][self._pName["c"]-2] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._pName["r"]][self._pName["c"]-2] == engineconfig["Meteor"]["Reward"]):
            a.remove(Action.West)
        print(f"{self._pName}: actions {a}")
        self._env._game.move("Finalizer", random.choice(a))


class Agent:
    def __init__(self, epsilon: float, gamma: float, alpha: float, env: Environment, pName: str):
        self._epsilon = epsilon
        self._gamma = gamma
        self._alpha = alpha
        self._env = env
        for p in self._env._game._players:
            if p["Name"] == pName:
                self._player = self._env._game._players
        self._location = (self._player["r"], self._player["c"])
        self._actions = [Action.North, Action.South, Action.East, Action.West]
        self._qtable = QTable(
            (self._env._rewards.rows, self._env._rewards.cols), self._actions)

    def act(self) -> None:
        a = self._qtable.getBestQ(self.location)[0]
        self._env._game.move("Millennium Falcon", a)

    def train(self):
        print("Training")
        locOriginal = self.location
        for e in range(self._env.episodes):
            print(f"Training episode: {e}")
            self.location = random.choice(self._env.openLocations())
            while not self._env.isTerminal(self.location):
                locStart = self.location
                print(f"In {self.location} - Q: {self._qtable[locStart]}")
                a = self.choose()
                print(f"Selection action: {a}")
                qStart = self._qtable[locStart][a]
                print(f"Quality of action: {qStart}")
                self.act(a)
                reward = self._env._rewards[self.location]
                print(f"Immediate reward for action: {reward}")
                print(f"Now in {self.location} - Q: {self._qtable[locStart]}")

                _, qBest = self._qtable.getBestQ(self.location)
                print(f"Best quality is {qBest}")
                td = reward + (self._gamma * qBest) - qStart
                print(f"Temporal Difference: {td}")

                qNew = qStart + td * self._alpha
                self._qtable[locStart][a] = qNew
                print(f"Updating qvalue @{locStart} for {a} to {qNew}\n\n")

        self.location = locOriginal
        print("Training Complete")
        for o in self._env.openLocations():
            print(f"@{o} - Q: {self._qtable[o]}")


if __name__ == "__main__":
    env = Environment(200)
    env.run()
