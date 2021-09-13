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
        super(AIPlayer, self).__init__(inputPlayerId, "Russell")

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
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
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
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
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
        moves = listAllLegalMoves(currentState)
        states = []
        nodes = []
        count = 0
        rootNode = getNode(currentState, None, 0, None)
        for move in moves:
            states.append(getNextState(currentState, move))

        for move in move:
            nodes.append(getNode(state[count], move[count], 1, rootNode))
            count+=1

        selectedMove = bestMove(nodes)

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
        # anything below 0.5 is not ideal
        rating = 0.0

        # add .07 for each food in inventory
        rating += 0.07 * getCurrPlayerFood(self, currentState)

        # add .06 for each worker up to two
        rating += 0.06 * len(getAntList(currentState, currentState.whoseTurn, (WORKER,)))

        # add .15 for each drone it has over the enemy
        rating += 0.15 * (len(getAntList(currentState, currentState.whoseTurn, (DRONE,)))-\
                            len(getAntList(currentState, 1-currentState.whoseTurn,(DRONE,))))
        if(rating > 1.0):
            return 1.0
        elif(rating < 0.0):
            return 0.0
        else:
            return rating

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
        eval = utility(state)
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
            if (node["evaluation"] < bestNode["evaluation"]):
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
