import enum
import random
from tkinter import ACTIVE
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
        self._map = [[] for _ in range(6561)]

        for r in range(6561):
            for _ in range(16):
                dictQ = {}
                for a in lstActions:
                    dictQ[a] = 0.0
                self._map[r].append(dictQ)

    def __getitem__(self, QPos: Tuple[int, int]) -> float:
        r, c = QPos
        return self._map[r][c]

    def __setitem__(self, QPos: Tuple[int, int], value) -> None:
        r, c = QPos
        self._map[r][c] = value

    def BestQValue(self, QPos: Tuple[int, int]) -> Tuple[Action, float]:
        qloc = self[QPos]
        QVal = list(qloc.values())[0]
        BestAction = list(qloc.keys())[0]

        for a, q in qloc.items():
            if q > QVal:
                QVal = q
                BestAction = a
        return (BestAction, QVal)


class World:
    def __init__(self) -> None:
        self._size = engineconfig["MapRadius"]
        self._map = [[] for _ in range(engineconfig["MapRadius"]*2)]
        blnNext = True
        random.seed(engineconfig["Food"]["Seed"])
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                if(self.euclideanDistance((engineconfig["MapRadius"], engineconfig["MapRadius"]), (r, c)) >= engineconfig["MapRadius"]):
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
                if(not self.euclideanDistance((engineconfig["MapRadius"], engineconfig["MapRadius"]), (r, c)) >= engineconfig["MapRadius"]):
                    n = random.randint(
                        0, engineconfig["Meteor"]["Probability"])
                    if(blnNext and n == engineconfig["Meteor"]["Probability"]):
                        self._map[r][c] = engineconfig["Meteor"]["Reward"]

        p = engineconfig["Players"][0]
        self._playerA = {"Name": p["Name"],
                         "Path": p["Path"],
                         "isAlive": True,
                         "Score": p["Size"], "r": 0, "c": 0}

        p = engineconfig["Players"][1]
        self._playerB = {"Name": p["Name"],
                         "Path": p["Path"],
                         "isAlive": True,
                         "Score": p["Size"], "r": 0, "c": 0}

        dist = engineconfig["MapRadius"]/2

        self._playerA["r"] = math.floor(dist)
        self._playerA["c"] = math.floor(dist)

        self._playerB["r"] = math.floor(dist*3)
        self._playerB["c"] = math.floor(dist*3)

    def reset(self):
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                self._map[r][c] = engineconfig["Reward"]
        self._size = engineconfig["MapRadius"]
        blnNext = True
        random.seed(engineconfig["Food"]["Seed"])
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                if(self.euclideanDistance((engineconfig["MapRadius"], engineconfig["MapRadius"]), (r, c)) >= engineconfig["MapRadius"]):
                    self._map[r][c] = engineconfig["Zone"]["Reward"]
                else:
                    n = random.randint(0, engineconfig["Food"]["Probability"])
                    if(blnNext and n == engineconfig["Food"]["Probability"]):
                        self._map[r][c] = engineconfig["Food"]["Reward"]
                        blnNext = not blnNext
                    else:
                        self._map[r][c] = engineconfig["Reward"]
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
                if(not self.euclideanDistance((engineconfig["MapRadius"], engineconfig["MapRadius"]), (r, c)) >= engineconfig["MapRadius"]):
                    n = random.randint(
                        0, engineconfig["Meteor"]["Probability"])
                    if(blnNext and n == engineconfig["Meteor"]["Probability"]):
                        self._map[r][c] = engineconfig["Meteor"]["Reward"]

        p = engineconfig["Players"][0]
        self._playerA = {"Name": p["Name"],
                         "Path": p["Path"],
                         "isAlive": True,
                         "Score": p["Size"], "r": 0, "c": 0}

        p = engineconfig["Players"][1]
        self._playerB = {"Name": p["Name"],
                         "Path": p["Path"],
                         "isAlive": True,
                         "Score": p["Size"], "r": 0, "c": 0}

        dist = engineconfig["MapRadius"]/2

        self._playerA["r"] = math.floor(dist)
        self._playerA["c"] = math.floor(dist)

        self._playerB["r"] = math.floor(dist*3)
        self._playerB["c"] = math.floor(dist*3)

    def updateZone(self):
        self._size -= 1
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                if(self.euclideanDistance((engineconfig["MapRadius"], engineconfig["MapRadius"]), (r, c)) >= self._size):
                    self._map[r][c] = engineconfig["Zone"]["Reward"]

    def update(self):
        for r in range(engineconfig["MapRadius"]*2):
            for c in range(engineconfig["MapRadius"]*2):
                if(self._map[r][c] == engineconfig["Zone"]["Reward"]):
                    if(self._playerA["r"] == r and self._playerA["c"] == c):
                        self._playerA["isAlive"] = False

                    if(self._playerB["r"] == r and self._playerB["c"] == c):
                        self._playerB["isAlive"] = False

        if(self._playerA["r"] == self._playerB["r"] and self._playerA["c"] == self._playerB["c"]):
            if(self._playerA["Score"] > self._playerB["Score"]):
                self._playerB["isALive"] = False
                self._playerB["Score"] -= engineconfig["PlayerReward"]
            elif (self._playerA["Score"] < self._playerB["Score"]):
                self._playerA["isAlive"] = False
                self._playerB["Score"] += engineconfig["PlayerReward"]

        if self._map[self._playerA["r"]][self._playerA["c"]] == engineconfig["Food"]["Reward"]:
            self._playerA["Score"] += engineconfig["Food"]["Reward"]
        if self._map[self._playerA["r"]][self._playerA["c"]] == engineconfig["Meteor"]["Reward"]:
            self._playerA["Score"] += engineconfig["Meteor"]["Reward"]
        if self._map[self._playerA["r"]][self._playerA["c"]] == engineconfig["BoostPad"]["Reward"]:
            self._playerA["Score"] += engineconfig["BoostPad"]["Reward"]
        if self._map[self._playerA["r"]][self._playerA["c"]] == engineconfig["Zone"]["Reward"]:
            self._playerA["Score"] += engineconfig["Zone"]["Reward"]
        else:
            self._playerA["Score"] += engineconfig["Reward"]
            self._map[self._playerA["r"]][self._playerA["c"]
                                          ] = engineconfig["Reward"]

        if self._map[self._playerB["r"]][self._playerB["c"]] == engineconfig["Food"]["Reward"]:
            self._playerB["Score"] += engineconfig["Food"]["Reward"]
        if self._map[self._playerB["r"]][self._playerB["c"]] == engineconfig["Meteor"]["Reward"]:
            self._playerB["Score"] += engineconfig["Meteor"]["Reward"]
        if self._map[self._playerB["r"]][self._playerB["c"]] == engineconfig["BoostPad"]["Reward"]:
            self._playerB["Score"] += engineconfig["BoostPad"]["Reward"]
        if self._map[self._playerB["r"]][self._playerB["c"]] == engineconfig["Zone"]["Reward"]:
            self._playerB["Score"] += engineconfig["Zone"]["Reward"]
        else:
            self._playerB["Score"] += engineconfig["Reward"]
            self._map[self._playerB["r"]][self._playerB["c"]
                                          ] = engineconfig["Reward"]

    def getMoves(self, p) -> List[Action]:
        actions = list()

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

    def move(self, p, action: Action):
        if action in self.getMoves(p):
            r = 0
            c = 0

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

    def euclideanDistance(self, p1: Tuple[int, int], p2: Tuple[int, int]):
        x1, y1 = p1
        x2, y2 = p2
        return math.sqrt((x1-x2)**2+(y1-y2)**2)

    def gameOver(self) -> bool:
        if(self._playerA["isAlive"] == False):
            return True
        if(self._playerB["isAlive"] == False):
            return True
        if self._size < 0:
            return True
        return False


class Environment:
    def __init__(self) -> None:
        self._epochs = engineconfig["Epochs"]
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
        self._agentR = ReferenceAgent(self)
        self._agentQ = Agent(0.9, 0.9, 0.9, self)

    def draw(self, epoch: int):
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

        self._window.blit(engine.transform.scale(engine.image.load(
            self._game._playerA["Path"]), (self._gridsize+5, self._gridsize+5)), (self._size+20, 32+30))
        self._window.blit(font.render(
            self._game._playerA["Name"] + ": "+str(self._game._playerA["Score"]), 1, (0, 0, 0)), (self._size+50, 30+30))
        if(self._game._playerA["isAlive"]):
            self._window.blit(
                engine.transform.scale(engine.image.load(self._game._playerA["Path"]), (self._gridsize, self._gridsize)), (self._game._playerA["c"]*self._gridsize, self._game._playerA["r"]*self._gridsize))

        self._window.blit(engine.transform.scale(engine.image.load(
            self._game._playerB["Path"]), (self._gridsize+5, self._gridsize+5)), (self._size+20, 32+30*2))
        self._window.blit(font.render(
            self._game._playerB["Name"] + ": "+str(self._game._playerB["Score"]), 1, (0, 0, 0)), (self._size+50, 30+30*2))
        if(self._game._playerB["isAlive"]):
            self._window.blit(
                engine.transform.scale(engine.image.load(self._game._playerB["Path"]), (self._gridsize, self._gridsize)), (self._game._playerB["c"]*self._gridsize, self._game._playerB["r"]*self._gridsize))

        self._window.blit(font.render("Epoch: "+str(epoch),
                          1, (0, 0, 0)), (self._size+50, self._size - 100))
        engine.display.flip()

    def run(self):
        time_interval = engineconfig["Tick"]
        object_time = 0
        clock = engine.time.Clock()
        for e in range(self._epochs):
            self._game.reset()

            while self._running and not self._game.gameOver():
                clock.tick(engineconfig["FPS"])
                current_time = engine.time.get_ticks()
                if current_time > object_time:
                    object_time += time_interval
                    if(((object_time/engineconfig["Zone"]["Tick"]).is_integer())):
                        self._game.updateZone()
                    self._agentQ.train()
                    self._agentR.act()
                    self._game.update()

                # for loop through the event queue
                for event in engine.event.get():
                    # Check for QUIT event
                    if event.type == engine.QUIT:
                        self._running = False
                self.draw(e+1)
                """ if self._game.gameOver():
                        self._continue = False
                        engine.quit() """


class ReferenceAgent:
    def __init__(self, env: Environment):
        self._env = env

    def act(self) -> None:
        a: List[Action] = self._env._game.getMoves(self._env._game._playerB)
        if(self._env._game._map[self._env._game._playerB["r"]+2][self._env._game._playerB["c"]] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerB["r"]+2][self._env._game._playerB["c"]] == engineconfig["Meteor"]["Reward"]):
            a.remove(Action.South)
        if(self._env._game._map[self._env._game._playerB["r"]-2][self._env._game._playerB["c"]] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerB["r"]-2][self._env._game._playerB["c"]] == engineconfig["Meteor"]["Reward"]):
            a.remove(Action.North)
        if(self._env._game._map[self._env._game._playerB["r"]][self._env._game._playerB["c"]+2] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerB["r"]][self._env._game._playerB["c"]+2] == engineconfig["Meteor"]["Reward"]):
            a.remove(Action.East)
        if(self._env._game._map[self._env._game._playerB["r"]][self._env._game._playerB["c"]-2] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerB["r"]][self._env._game._playerB["c"]-2] == engineconfig["Meteor"]["Reward"]):
            a.remove(Action.West)
        # print(f"{self._pName}: actions {a}")
        if(len(a) > 0):
            self._env._game.move(self._env._game._playerB, random.choice(a))


class Agent:
    def __init__(self, epsilon: float, gamma: float, alpha: float, env: Environment):
        self._epsilon = epsilon
        self._gamma = gamma
        self._alpha = alpha
        self._env = env
        self._actions = [Action.North, Action.South, Action.East, Action.West]
        self._qtable = QTable(self._actions)

    def act(self, a: Action) -> None:
        self._env._game.move(self._env._game._playerA, a)

    def choose(self) -> Action:
        QLoc = self._qtable._map[self.getState()[0]][self.getState()[1]]
        if random.random() < self._epsilon:
            BestAction, _ = self._qtable.BestQValue(
                (self.getState()[0], self.getState()[1]))
            return BestAction
        else:
            return random.choice(list(QLoc.keys()))

    def train(self):
        locStart = self.getState()
        print(f"QVal: {self._qtable._map[locStart[0]][locStart[1]]}")
        action = self.choose()
        qStart = self._qtable[locStart][action]
        print(f"The Action: {action} Action Value: {qStart}")
        self.act(action)
        reward = self._env._game._map[self._env._game._playerA["r"]
                                      ][self._env._game._playerA["c"]]
        print(f"Reward for Action: {reward}")

        _, BestQVal = self._qtable.BestQValue(
            (self.getState()[0], self.getState()[1]))
        print(f"Best QVal: {BestQVal}")
        tempdiff = reward + (self._gamma * BestQVal) - qStart
        print(f"Temporal Difference: {tempdiff}")
        NewQVal = qStart + tempdiff * self._alpha
        self._qtable[locStart][action] = NewQVal
        print(
            f"Updated QVal {locStart} action: {action} newQval: {NewQVal}\n\n")

    def getState(self) -> Tuple[int, int]:
        drad = [0, 0, 0, 0]
        rad = [0, 0, 0, 0, 0, 0, 0, 0]
        if(self._env._game._map[self._env._game._playerA["r"]-1][self._env._game._playerA["c"]] == engineconfig["Food"]["Reward"]):
            rad[0] = 1
        if(self._env._game._map[self._env._game._playerA["r"]+1][self._env._game._playerA["c"]] == engineconfig["Food"]["Reward"]):
            rad[1] = 1
        if(self._env._game._map[self._env._game._playerA["r"]][self._env._game._playerA["c"]+1] == engineconfig["Food"]["Reward"]):
            rad[2] = 1
        if(self._env._game._map[self._env._game._playerA["r"]][self._env._game._playerA["c"]-1] == engineconfig["Food"]["Reward"]):
            rad[3] = 1
        if(self._env._game._map[self._env._game._playerA["r"]-1][self._env._game._playerA["c"]+1] == engineconfig["Food"]["Reward"]):
            rad[4] = 1
        if(self._env._game._map[self._env._game._playerA["r"]-1][self._env._game._playerA["c"]-1] == engineconfig["Food"]["Reward"]):
            rad[5] = 1
        if(self._env._game._map[self._env._game._playerA["r"]+1][self._env._game._playerA["c"]+1] == engineconfig["Food"]["Reward"]):
            rad[6] = 1
        if(self._env._game._map[self._env._game._playerA["r"]+1][self._env._game._playerA["c"]-1] == engineconfig["Food"]["Reward"]):
            rad[7] = 1

        if(self._env._game._playerB["Score"] < self._env._game._playerA["Score"]):
            oppR = self._env._game._playerA["r"] - \
                self._env._game._playerB["r"]
            oppC = self._env._game._playerA["c"] - \
                self._env._game._playerB["c"]

            if (oppR < 0 and oppC < 0):
                rad[0] = 2
            elif (oppR == 0 and oppC < 0):
                rad[1] = 2
            elif (oppR > 0 and oppC < 0):
                rad[2] = 2
            elif (oppR > 0 and oppC == 0):
                rad[3] = 2
            elif (oppR > 0 and oppC > 0):
                rad[4] = 2
            elif (oppR == 0 and oppC > 0):
                rad[5] = 2
            elif (oppR < 0 and oppC > 0):
                rad[6] = 2
            elif (oppR < 0 and oppC == 0):
                rad[7] = 2

        row = rad[0] + (3 * rad[1]) + (9 * rad[2]) + (27 * rad[3]) + \
            (81 * rad[4]) + (243 * rad[5]) + (729 * rad[6]) + (2187 * rad[7])

        if(self._env._game._map[self._env._game._playerA["r"]-1][self._env._game._playerA["c"]] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]-1][self._env._game._playerA["c"]] == engineconfig["Meteor"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]-2][self._env._game._playerA["c"]] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]-2][self._env._game._playerA["c"]] == engineconfig["Meteor"]["Reward"]):
            drad[0] = 1
        if(self._env._game._map[self._env._game._playerA["r"]+1][self._env._game._playerA["c"]] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]+1][self._env._game._playerA["c"]] == engineconfig["Meteor"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]+2][self._env._game._playerA["c"]] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]+2][self._env._game._playerA["c"]] == engineconfig["Meteor"]["Reward"]):
            drad[1] = 1
        if(self._env._game._map[self._env._game._playerA["r"]][self._env._game._playerA["c"]+1] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]][self._env._game._playerA["c"]+1] == engineconfig["Meteor"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]][self._env._game._playerA["c"]+2] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]][self._env._game._playerA["c"]+2] == engineconfig["Meteor"]["Reward"]):
            drad[2] = 1
        if(self._env._game._map[self._env._game._playerA["r"]][self._env._game._playerA["c"]-1] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]][self._env._game._playerA["c"]-1] == engineconfig["Meteor"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]][self._env._game._playerA["c"]-2] == engineconfig["Zone"]["Reward"] or self._env._game._map[self._env._game._playerA["r"]][self._env._game._playerA["c"]-2] == engineconfig["Meteor"]["Reward"]):
            drad[3] = 1

        if(self._env._game._playerB["Score"] > self._env._game._playerA["Score"]):
            if(self._env._game._playerA["r"]-1 == self._env._game._playerB["r"] and self._env._game._playerA["c"] == self._env._game._playerB["c"]):
                drad[0] = 1
            if(self._env._game._playerA["r"]+1 == self._env._game._playerB["r"] and self._env._game._playerA["c"] == self._env._game._playerB["c"]):
                drad[1] = 1
            if(self._env._game._playerA["r"] == self._env._game._playerB["r"] and self._env._game._playerA["c"]+1 == self._env._game._playerB["c"]):
                drad[2] = 1
            if(self._env._game._playerA["r"] == self._env._game._playerB["r"] and self._env._game._playerA["c"]-1 == self._env._game._playerB["c"]):
                drad[3] = 1

        col = drad[0] + (2*drad[1]) + (4*drad[2])+(8*drad[3])

        return (row, col)


if __name__ == "__main__":
    env = Environment()
    env.run()
