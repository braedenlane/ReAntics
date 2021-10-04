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
        super(AIPlayer, self).__init__(inputPlayerId, "Scarab")

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
        frontierNodes = []
        expandedNodes = []

        rootNode = self.getNode(None, currentState, 0, None)

        frontierNodes.append(rootNode)

        # Expand nodes until depth of 4 is reached
        for i in range(4):
            for node in frontierNodes:
                frontierNodes.remove(node)
                expandedNodes.append(node)
                children = self.expandNode(node)

            frontierNodes.extend(children)

        # Choose the move with the lowest score in frontierNodes and trace back to parent
        bestNode = None
        lowestEval = 10000
        for potentialNode in frontierNodes:
            if (potentialNode["evaluation"] < lowestEval):
                bestNode = potentialNode
                lowestEval = potentialNode["evaluation"]

        # iterate back to the parent with depth of 1
        while (bestNode["depth"] != 1):
            bestNode = bestNode["parentNode"]

        return bestNode["move"]

    def getEval(self, dict):
        return dict["evaluation"]

    ##
    # utility
    # Description: Examines the gamestate and estimates how many turns will be
    #   needed to finish the game
    #
    # Parameters:
    #   state - the state to be examined
    #
    # Return: the score the the gamestate (0.0 is lowest, 1.0 is highest)
    ##
    def utility(self, state):

        myInv = getCurrPlayerInventory(state)
        enemInv = getEnemyInv(self, state)

        estimate = 1000

        # Filling our ant arrays that we will need for our estimations
        numWorkers = 0
        workers = []
        drones = []
        enemWorkers = []
        for ant in myInv.ants:
            if (ant.type == DRONE):
                drones.append(ant)
            elif (ant.type == WORKER):
                workers.append(ant)
                numWorkers += 1

        for enemAnt in enemInv.ants:
            if (enemAnt.type == WORKER):
                enemWorkers.append(enemAnt)

        tunnelCoords = getConstrList(state, state.whoseTurn, [TUNNEL, ])[0].coords

        # just a queen is 1000 aka we dont want this. we lose with just queen

        foods = getConstrList(state, 2, [FOOD, ])
        if len(foods) > 1:

            myFood = foods[0]
            max = 1000
            for food in foods:
                steps = approxDist(food.coords, tunnelCoords)
                if steps < max:
                    max = steps
                    myFood = food

            dist = approxDist(tunnelCoords, myFood.coords)

            if numWorkers == 0:
                estimate = 1000
            elif numWorkers == 1:
                estimate = (11 - myInv.foodCount) * dist * 2

            for worker in workers:
                if not worker.carrying:
                    estimate += approxDist(worker.coords, myFood.coords)

            # moving queen off hill and tunnel and food reduces time by 2
            queenCoords = myInv.getQueen().coords
            if queenCoords == myInv.getAnthill().coords \
                    or queenCoords == tunnelCoords \
                    or queenCoords == myFood.coords:
                estimate += 2

            if (len(drones) == 1):
                estimate -= 30
                if (len(enemWorkers) >= 1):
                    estimate += approxDist(drones[0].coords, enemWorkers[0].coords)
                elif(len(enemWorkers) == 0):
                    estimate -= 10
                    estimate += approxDist(drones[0].coords, enemInv.getAnthill().coords)

        return estimate

    ##
    # expandNode
    # Description:
    # Creates new nodes based on a node that is passed in as a parameter
    #
    # Parameters:
    #   parentNode - the node to expand and create frontier/children nodes off of
    ##
    def expandNode(self, parentNode):
        moves = listAllLegalMoves(parentNode["state"])
        ret = []
        for move in moves:
            ret.append(self.getNode(move, getNextState(parentNode["state"], move),
                                    parentNode["depth"] + 1, parentNode))
        return ret

    ##
    # getNode
    # Description:
    # Creates and returns a "node" dictionary containing the information a node would include
    #
    # Parameters:
    #   move - the move used in the parent node to reach this node
    #   state - the state that would be reached in this node
    #   depth - number of moves required to reach this node from the agent's true current state
    #   parentNode - a reference to the parent node of this node
    #
    # Return:
    # the "node" dictionary
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
# Description:
#   tests if the the utility function evaluates the board correctly
#
# Parameters:
#   None
#
# Return:
#   None
##
def testUtility():
   gamestate = GameState.getBasicState()
   score = p.utility(gamestate)
   assert score > 0
   assert score < 10000
##
# testGetNode
#
# Description:
#   tests if the get node function returns the correct node
#
# Parameters:
#   None
#
# Return:
#   None
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
# Description:
#   tests if the best move function returns the best move properly
#
# Parameters:
#   None
#
# Return:
#   None
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