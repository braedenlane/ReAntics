from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir

# Needs methods:
# __init__ constructor
# getPlacement
# getMove
# getAttack
# registerWin

# Can use python Game.py -2p -p Booger human -randomLayout for quick debugging
# add -n 10 for 10 games back to back
# -self -p Booger would make it play against itself

class AIPlayer(Player):

    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Dominus")
        # the coordinates of the agent's food closest to the tunnel and tunnel will be stored in these
        # variables (see getMove() below)
        # coordinates of the agent's food closest to the hill and hill will be stored as well
        self.myTunnelFood = None
        self.myHillFood = None
        self.myHill = None
        self.myTunnel = None

    ##
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        self.myTunnelFood = None
        self.myHillFood = None
        self.myHill = None
        self.myTunnel = None
        myId = currentState.whoseTurn
        enemyId = 1 - myId
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            # Ideal location for the ant hill and tunnel, minimizing the distance to any food source location
            # Grass placed defensively to protect ant hill, also placed to reduce food distance
            return [(2, 1), (7, 2), (0, 3), (1, 3), (2, 3),
                    (3, 3), (4, 3), (5, 3), (6, 3), (5, 0), (9,0)]
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    xCoords = (0,9)
                    yCoords = (6,9)
                    bestDist = 0
                    bestSpot = (0,0)
                    enemyInv = currentState.inventories[enemyId]
                    enemyHill = enemyInv.getAnthill()
                    enemyTunnel = enemyInv.getTunnels()
                    for xCoord in xCoords:
                        for yCoord in yCoords:
                            distTunnel = stepsToReach(currentState, (xCoord, yCoord), enemyTunnel[0].coords)
                            distHill = stepsToReach(currentState, (xCoord, yCoord), enemyHill.coords)
                            if(distTunnel >= 2 and distHill >= 2):
                                # Set the move if this space is empty
                                if currentState.board[xCoord][yCoord].constr == None and (xCoord, yCoord) not in moves:
                                    move = (xCoord, yCoord)
                                    # Just need to make the space non-empty. So I threw whatever I felt like in there.
                                    currentState.board[xCoord][yCoord].constr == True
                                    break
                        if (currentState.board[xCoord][yCoord].constr == True):
                            break
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    # getMove
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):
        myId = currentState.whoseTurn
        enemyId = 1 - myId

        myInv = currentState.inventories[myId]
        myAnts = myInv.ants
        moves = listAllMovementMoves(currentState)

        # the first time this method is called, the foods, hill, and tunnel locations
        # need to be recorded in their respective instance variables
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, myId, (TUNNEL,))[0]
        if (self.myHill == None):
            self.myHill = getConstrList(currentState, myId, (ANTHILL,))[0]
        if (self.myTunnelFood == None):
            foods = getConstrList(currentState, None, (FOOD,))
            self.myTunnelFood = foods[0]
            # find the food closest to the tunnel
            bestDistSoFar = 1000  # i.e., infinity
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if (dist < bestDistSoFar):
                    self.myTunnelFood = food
                    bestDistSoFar = dist
        if (self.myHillFood == None):
            if (self.myTunnelFood == foods[0]):
                self.myHillFood = foods[1]
            else:
                self.myHillFood = foods[0]

        # if I don't have a worker, and am out of food, give up, since food can't be collected
        numAnts = len(myInv.ants)
        if (numAnts == 1 & myInv.foodCount == 0):
            return Move(END, None, None)

        endTurnCheck = True
        for ant in myInv.ants:
            if not (ant.hasMoved):
                endTurnCheck = False
        if endTurnCheck:
            return Move(END, None, None)

        # if the queen is on the anthill move her
        myQueen = myInv.getQueen()
        if (myQueen.coords == myInv.getAnthill().coords):
            return Move(MOVE_ANT, [myInv.getQueen().coords, (2, 0)], None)

        # if the hasn't moved, have her move in place so she will attack
        if (not myQueen.hasMoved):
            return Move(MOVE_ANT, [myQueen.coords], None)

        # Counts of my different ants to determine what "phase" we're in
        countWorker = len(getAntList(currentState, myId, (WORKER,)))
        countDrone = len(getAntList(currentState, myId, (DRONE,)))
        countRSoldier = len(getAntList(currentState, myId, (R_SOLDIER,)))

        # Phases:
        #      - Have the AI shoot for 2 workers, a drone, and then another worker.
        #      - Check these numbers each turn and replenish as needed
        # TODO: check Anthill unoccupied on builds
        if (getAntAt(currentState, myInv.getAnthill().coords) is None):
            if (countWorker < 2):
                if (myInv.foodCount >= 1):
                    return Move(BUILD, [myInv.getAnthill().coords], WORKER)
            if (countDrone < 1):
                if myInv.foodCount >= 2:
                    return Move(BUILD, [myInv.getAnthill().coords], DRONE)
            if (countDrone == 1 and countWorker < 3):
                if (myInv.foodCount >= 1):
                    return Move(BUILD, [myInv.getAnthill().coords], WORKER)
            if (countDrone == 1 and countWorker == 3 and countRSoldier < 1):
                if (myInv.foodCount >= 2):
                    return Move(BUILD, [myInv.getAnthill().coords], R_SOLDIER)

        # Region: Worker behavior
        #     - If not carrying food, move toward closest food source
        #     - If adjacent to a food source, and not carrying, move onto food source and end move
        #     - If carrying food, navigate to closest friendly construction
        #     - If adjacent to construction, and carrying, move onto const. and end move
        myWorkers = getAntList(currentState, myId, (WORKER,))
        for worker in myWorkers:
            if not (worker.hasMoved):
                if not (worker.carrying):
                    # calculate the closest food
                    distToTunnelFood = stepsToReach(currentState, worker.coords, self.myTunnelFood.coords)
                    distToHillFood = stepsToReach(currentState, worker.coords, self.myHillFood.coords)
                    if distToHillFood < distToTunnelFood :
                        path = createPathToward(currentState, worker.coords,
                                    self.myHillFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                        if (getAntAt(currentState, path) is not None):
                            path = createPathToward(currentState, worker.coords,
                                                    self.myTunnelFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                    else:
                        path = createPathToward(currentState, worker.coords, self.myTunnelFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                        if (getAntAt(currentState, path) is not None):
                            path = createPathToward(currentState, worker.coords,
                                                    self.myHillFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                    return Move(MOVE_ANT, path, None)
                else:
                    # calculate the closest structure
                    distToTunnel = stepsToReach(currentState, worker.coords, self.myTunnel.coords)
                    distToHill = stepsToReach(currentState, worker.coords, self.myHill.coords)
                    if distToHill < distToTunnel :
                        path = createPathToward(currentState, worker.coords,
                                    self.myHill.coords, UNIT_STATS[WORKER][MOVEMENT])
                        if (getAntAt(currentState, path) is not None):
                            path = createPathToward(currentState, worker.coords,
                                                    self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                    else:
                        path = createPathToward(currentState, worker.coords,
                                    self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                        if (getAntAt(currentState, path) is not None):
                            path = createPathToward(currentState, worker.coords,
                                                    self.myHill.coords, UNIT_STATS[WORKER][MOVEMENT])
                    return Move(MOVE_ANT, path, None)



        # Region: Drone behavior
        #     - Navigate to the nearest enemy worker (Note, don't send two drones to the same worker)
        #     - If adjacent to enemy worker, attack
        myDrones = getAntList(currentState, myId, (DRONE,))
        enemyWorkers = getAntList(currentState, enemyId, (WORKER,))
        for drone in myDrones:
            if not (drone.hasMoved):
                # check if enemy has any workers. If so, attack them. If not, attack the queen
                if len(enemyWorkers):
                    path = createPathToward(currentState, drone.coords, enemyWorkers[0].coords, UNIT_STATS[DRONE][MOVEMENT])
                else:
                    path = createPathToward(currentState, drone.coords, getAntList(currentState, enemyId, (QUEEN,))[0].coords, UNIT_STATS[DRONE][MOVEMENT])
                return Move(MOVE_ANT, path, None)

        # Region: Ranged Soldier behavior
        #     - Navigate to the queen and defend her
        myRSoldiers = getAntList(currentState, myId, (R_SOLDIER,))
        for rSoldier in myRSoldiers:
            if not (rSoldier.hasMoved):
                # Navigate to be beside the queen to defend her, keep moving to constantly attack if needed
                if (rSoldier.coords == (3,0)):
                    return Move(MOVE_ANT, [rSoldier.coords], None)
                else:
                    path = createPathToward(currentState, rSoldier.coords, (3,0), UNIT_STATS[R_SOLDIER][MOVEMENT])
                return Move(MOVE_ANT, path, None)

    ##
    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    # registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, hasWon):
        # method template, not implemented
        pass
