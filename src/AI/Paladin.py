import random
import sys
import unittest
import os.path
from pathlib import Path

sys.path.append('..')  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *



##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):
    stateCatUtils = []
    indexUpdate = -1
    eGreedy = .9999
    eGreedyCount = 0
    train = False

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, 'Paladin')
        self.initWeights()

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]



    ##
    #utility
    #Description: evaluates game state on based on 12 game factors,
    #             multiplies each by a weight and adds all of them up
    #
    #Parameters:
    #   currentState: a clone of the current GameState
    #   gene: the gene (list of numbers) that contains the weights for each factor
    #
    #Return: total sum of all factors * their respective weight
    #
    ##
    def utility(self, currentState):
        # Important vars
        myId = currentState.whoseTurn
        enemyId = 1 - myId
        myCombatAnts = getAntList(currentState, myId, (DRONE, R_SOLDIER, SOLDIER,))
        enemyCombatAnts = getAntList(currentState, enemyId, (DRONE, R_SOLDIER, SOLDIER,))
        myHill = getConstrList(currentState, myId, (ANTHILL,))[0]
        enemyHill = getConstrList(currentState, enemyId, (ANTHILL,))[0]
        myWorkers = getAntList(currentState, myId, (WORKER,))
        enemyWorkers = getAntList(currentState, enemyId, (WORKER,))
        myFood = getCurrPlayerFood(self, currentState)
        myTunnel = getConstrList(currentState, myId, (TUNNEL,))[0]
        
        # 1: Food Count
        foodCount = getCurrPlayerInventory(currentState).foodCount
        
        # 2: Worker Ant Count
        workerCount = 0
        for worker in myWorkers:
            workerCount = workerCount + 1

        if (workerCount > 2):
            workerCount = 2
        
        # 3: Offensive Ant Count
        offCount = len(myCombatAnts)
        
        # 4: Worker Carrying?
        if(len(myWorkers) == 0):
            workerCarry = 0
        for worker in myWorkers:
            if worker.carrying:
                workerCarry = 1
            else:
                workerCarry = 0
        
        # 5: Avg Worker Distance to food when not carrying
        totalWorkerFoodDist = 0
        if (len(myWorkers) == 0):
            avgDistNotCarry = -1
        else:
            for worker in myWorkers:
                if not worker.carrying:

                    # Determine which food is closer, add the smaller dist
                    # If tie, go to first food in list

                    food0Dist = approxDist(worker.coords, myFood[0].coords)
                    food1Dist = approxDist(worker.coords, myFood[1].coords)
                    if food1Dist < food0Dist:
                        totalWorkerFoodDist += food1Dist

                    else:
                        totalWorkerFoodDist += food0Dist

            avgDistNotCarry = int(totalWorkerFoodDist / len(myWorkers))
        
        # 6: Avg Worker Distance to Tunnel/Hill when carrying
        totalWorkerStructDist = 0
        if (len(myWorkers) == 0):
            avgDistCarry = -1
        else:
            for worker in myWorkers:
                if worker.carrying:

                    # Determine which food is closer, add the smaller dist
                    # If tie, go to tunnel

                    hillDist = approxDist(worker.coords, myHill.coords)
                    tunnelDist = approxDist(worker.coords, myTunnel.coords)
                    if hillDist < tunnelDist:
                        totalWorkerStructDist += hillDist

                    else:
                        totalWorkerStructDist += tunnelDist

            avgDistCarry = int(totalWorkerStructDist / len(myWorkers))
        
        # 7: Avg Offensive Ant Dist to Enemy Hill
        avgDistEnemHill = int(self.calcAvgDist(myCombatAnts, enemyHill))

        listOfChecks = [foodCount, workerCount, offCount, workerCarry,
                        avgDistNotCarry, avgDistCarry, avgDistEnemHill]

        if len(self.stateCatUtils) > 0:
            for stateCat in self.stateCatUtils:
                if ((stateCat[0] == foodCount) and
                        (stateCat[1] == workerCount) and
                        (stateCat[2] == offCount) and
                        (stateCat[3] == workerCarry) and
                        (stateCat[4] == avgDistNotCarry) and
                        (stateCat[5] == avgDistCarry) and
                        (stateCat[6] == avgDistEnemHill)):
                    return [stateCat[7], self.stateCatUtils.index(stateCat)]

        listOfChecks.append(0.0)
        self.stateCatUtils.append(listOfChecks)
        return [0.0, (len(self.stateCatUtils) - 1)]
            



    #calcAvgDist
    #
    #Calculates average distance between all ants of a list and a target
    #
    #Params:
    #   antList: ant list to calculate average distance of
    #   target:
    #
    #Return:
    #   average distance between ants in list and the target
    def calcAvgDist(self, antList, target):
        if (len(antList) == 0):
            return 0

        totalDist = 0
        for ant in antList:
            totalDist += approxDist(ant.coords, target.coords)

        return int(totalDist / len(antList))



    #findClosestEnemyWorker
    #
    #Finds closest enemy worker with regards to a specified ant
    #In other words, for one of my ants, find closest enemy worker
    #
    #Params:
    #   ant: ant to consider
    #   enemyWorkerList: list of enemy workers
    #
    #Return:
    #   enemy worker that is closest to the specified ant
    def findClosestEnemyWorker(self, ant, enemyWorkerList):
        #Base cases
        closest = enemyWorkerList[0]
        closestDist = 10000


        for enemyWorker in enemyWorkerList:
            temp = approxDist(ant, enemyWorker)
            if temp < closestDist:
                closest = enemyWorker
                closestDist = temp


        return closest


    #https://www.pythontutorial.net/python-basics/python-check-if-file-exists/
    #10/15
    def initWeights(self):
        #Use random values if no prior genes exist
        path = Path('..\laneb22_profenna23_weights.txt')
        print(path.is_file())
        if (path.is_file()):
            f = open("..\laneb22_profenna23_weights.txt", "r")

            #https://www.kite.com/python/answers/how-to-convert-each-line-in-a-text-file-into-a-list-in-python
            #https://blog.finxter.com/how-to-convert-a-string-list-to-a-float-list-in-python/
            count = 0
            for line in f:
                self.stateCatUtils.append([])
                stripped_line = line.strip()
                line_list = stripped_line.split()
                self.stateCatUtils[count] = ([float(x) for x in line_list])
                count = count+1

            f.close()


    def saveWeights(self):
        path = Path('.\laneb22_profenna23_weights.txt')
        if (path.is_file()):
            print("removing")
            os.remove(path)
        print("Open file\n")
        f = open(".\laneb22_profenna23_weights.txt", "w")
        for list in self.stateCatUtils:
            for slot in range(8):  # TODO: make sure this matches
                f.write(str(list[slot]))
                f.write(' ')
            f.write("\n")

        f.close()
        
    def updateWeights(self, bestUtil, reward):
        self.stateCatUtils[self.indexUpdate][7] = (self.stateCatUtils[self.indexUpdate][7] + \
                                                    .15 * (reward + (.9 * bestUtil) - \
                                                    self.stateCatUtils[self.indexUpdate][7]))

        ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moveList = listAllLegalMoves(currentState)
        bestUtil = -100000
        bestMove = None
        bestIndex = -1
        for move in moveList:
            ret = self.utility(getNextState(currentState, move))
            moveUtil = ret[0]
            if moveUtil > bestUtil:
                bestIndex = ret[1]
                bestUtil = moveUtil
                bestMove = move

        if(self.train):
            # eGreedy chance that it chooses a random move
            if random.random() < (self.eGreedy ** self.eGreedyCount):
                move = moveList[random.randint(0, (len(moveList)-1))]
                ret = self.utility(getNextState(currentState, move))
                bestUtil = ret[0]
                bestIndex = ret[1]
                bestMove = move

            if self.indexUpdate != -1:
                self.updateWeights(bestUtil, -0.01)
            self.indexUpdate = bestIndex

            self.eGreedyCount = self.eGreedyCount + 1

        if not (self.train):
            if (random.random() < .01):
                move = moveList[random.randint(0, (len(moveList) - 1))]
                ret = self.utility(getNextState(currentState, move))
                bestUtil = ret[0]
                bestIndex = ret[1]
                bestMove = move

        return bestMove



    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]



    ##
    # registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, hasWon):
        # save weights after every game
        if hasWon:
            if(self.train):
                self.updateWeights(1.0, 1.0)
            self.saveWeights()
        else:
            if (self.train):
                self.updateWeights(-1.0, -1.0)
            self.saveWeights()
