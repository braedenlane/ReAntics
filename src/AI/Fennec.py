import random
import sys

from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *

sys.path.append("..")  # so other modules can be found in parent dir


##
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Fennec")

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
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
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
                        # Just need to make the space non-empty. So I threw whatever
                        # I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
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
                        # Just need to make the space non-empty. So I threw whatever
                        # I felt like in there.
                        currentState.board[x][y].constr == True
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
        moves = []
        moves.extend(listAllMovementMoves(currentState))
        if (len(moves) == 0):
            moves.append(Move(END, None, None))
        moves.extend(listAllBuildMoves(currentState))
        states = []
        nodes = []
        count = 0

        # rootNode is the node relating to the current state. Has no parent or previous move
        rootNode = self.getNode(None, currentState, 0, None)

        # get a list of valid states based on legal moves
        for move in moves:
            states.append(getNextState(currentState, move))

        # develop a node list based on the moves and states lists
        for move in moves:
            toAdd = self.getNode(moves[count], states[count], 1, rootNode)
            nodes.append(toAdd)
            count += 1

        selectedMove = self.bestMove(nodes)

        return selectedMove

    ##
    # utility
    # Description: Examines the gamestate and returns a rating from 0 to 1
    #   based on how good it thinks the state is. 0 is lowest, 1 is highest
    #
    # Parameters:
    #   state - the state to be examined
    #
    # Return: the score the the gamestate (0.0 is lowest, 1.0 is highest)
    ##
    def utility(self, state):

        myInv = getCurrPlayerInventory(state)
        enemInv = getEnemyInv(self, state)

        # anything below 0.5 is not ideal
        rating = 0.0

        # add .07 for each food in inventory
        rating += 0.07 * myInv.foodCount

        # add .075 for each worker we have, up to 2 (favor worker over just keeping a food)
        if (len(getAntList(state, state.whoseTurn, (WORKER,))) <= 2):
            rating += 0.075 * len(getAntList(state, state.whoseTurn, (WORKER,)))

        # add .2 if we have a drone
        if (len(getAntList(state, state.whoseTurn, (DRONE,))) == 1):
            rating += 0.2

        # add .25 if we have a soldier
        if (len(getAntList(state, state.whoseTurn, (SOLDIER,))) == 1):
            rating += 0.25

        # Evaluate how close this state is to adding a piece of food
        for ant in myInv.ants:

            # Queen behavior (keep off anthill)
            if (ant.type == QUEEN):
                if (myInv.getAnthill().coords == ant.coords):
                    return 0.0

            # Worker behavior
            if (ant.type == WORKER):
                stepsTilFood = 0
                stepsTilConstr = 0

                # calculate the closest food source on my side
                if not (ant.carrying):
                    stepsTilFood = 100  # ie infinity
                    stepsTilConstr = 100  # ie infinity
                    foods = getCurrPlayerFood(self, state)
                    for food in foods:
                        potentialSteps = stepsToReach(state, ant.coords, food.coords)
                        if (potentialSteps < stepsTilFood):
                            stepsTilFood = potentialSteps
                            foodSource = food

                    # calculate the closest structure from foodSource coords
                    constrs = []
                    constrs.append(myInv.getAnthill())
                    constrs.append(myInv.getTunnels()[0])
                    for constr in constrs:
                        potentialSteps = stepsToReach(state, foodSource.coords, constr.coords)
                        if (potentialSteps < stepsTilConstr):
                            stepsTilConstr = potentialSteps


                else:
                    stepsTilFood = 0
                    stepsTilConstr = 100  # ie infinity
                    # calculate the closest structure from ant coords
                    constrs = []
                    constrs.append(myInv.getTunnels()[0])
                    constrs.append(myInv.getAnthill())
                    for constr in constrs:
                        potentialSteps = stepsToReach(state, ant.coords, constr.coords)
                        if (potentialSteps < stepsTilConstr):
                            stepsTilConstr = potentialSteps

                stepsToAddFood = stepsTilFood + stepsTilConstr

                rating -= 0.005 * stepsToAddFood

            # Drone behavior

            if (ant.type == DRONE):
                shortestPathToEnemWorker = 0
                if not (len(getAntList(state, 1 - state.whoseTurn, (WORKER,))) == 0):
                    shortestPathToEnemWorker = 100  # ie infinity
                    for enemAnt in enemInv.ants:
                        if (enemAnt.type == WORKER):
                            potentialSteps = stepsToReach(state, ant.coords, enemAnt.coords)
                            if (potentialSteps < shortestPathToEnemWorker):
                                shortestPathToEnemWorker = potentialSteps

                rating -= 0.005 * shortestPathToEnemWorker

            # Soldier behavior

            if (ant.type == SOLDIER):
                shortestPathToEnemQueen = 100  # ie infinity
                for enemAnt in enemInv.ants:
                    if (enemAnt.type == QUEEN):
                        potentialSteps = stepsToReach(state, ant.coords, enemAnt.coords)
                        if (potentialSteps < shortestPathToEnemQueen):
                            shortestPathToEnemQueen = potentialSteps

                rating -= 0.005 * shortestPathToEnemQueen

        # max rating possible is 1.34, so divide rating by that to get a score between 0 and 1.
        return (rating / 1.34)

    ##
    # getNode
    # Description:
    #
    #
    # Parameters:
    #   move - the move used in the parent node to reach this node
    #   state - the state that would be reached in this node
    #   depth - number of moves required to reach this node from the agent's true current state
    #   parentNode - a reference to the parent node of this node
    #
    # Return:
    ##
    def getNode(self, move, state, depth, parentNode):
        eval = self.utility(state)
        node = {
            "move": move,
            "state": state,
            "depth": depth,
            "evaluation": eval,
            "parentNode": parentNode
        }
        return node

    ##
    # bestMove
    # Description: Finds the best move in the given node list by checking
    #   the evaluation at the depth of 1 and returns the move required to
    #   get there
    #
    # Parameters:
    #   nodeList - a list of nodes
    #
    # Return: the best move we found
    ##
    def bestMove(self, nodeList):
        if (nodeList == None):
            return None

        bestNode = nodeList[0]
        for node in nodeList:
            if (node["evaluation"] > bestNode["evaluation"]):
                bestNode = node
        bestMove = bestNode["move"]
        return bestMove

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
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        # method templaste, not implemented
        pass


#############################
##   Unit test functions   ##
#############################

p = AIPlayer(1)


##
# testUtility
#
# tests if the the utility function evaluates the board correctly
##
def testUtility():
    gamestate = GameState.getBasicState()
    score = p.utility(gamestate)
    assert score <= 1.0
    assert score >= 0.0


##
# testGetNode
#
# tests if the get node function returns the correct node
##
def testGetNode():
    move = Move(0)
    gamestate = GameState.getBasicState()
    depth = 2
    eval = p.utility(gamestate)
    parentNode = None
    node = p.getNode(move, gamestate, depth, parentNode)

    assert move == node["move"]
    assert gamestate == node["state"]
    assert depth == node["depth"]
    assert eval == node["evaluation"]
    assert parentNode == node["parentNode"]


##
# testBestMove
#
# tests if the best move function returns the best move properly
##
def testBestMove():
    move1 = Move(0)
    move2 = Move(1)
    gamestate = GameState.getBasicState()
    depth = 2
    parent = None

    node1 = p.getNode(move1, gamestate, depth, parent)
    node1["evaluation"] = .9

    node2 = p.getNode(move2, gamestate, depth, parent)
    node2["evaluation"] = .6

    assert move1 == p.bestMove([node1, node2])


########################
## Calling unit tests ##
########################


testUtility()
testGetNode()
testBestMove()