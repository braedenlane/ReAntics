from src.Player import *
from src.Constants import *
from src.Construction import CONSTR_STATS
from src.Ant import UNIT_STATS
from src.Move import Move
from src.GameState import *
from src.AIPlayerUtils import *
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
        # the coordinates of the agent's food and tunnel will be stored in these
        # variables (see getMove() below)
        self.myFood = None
        self.myTunnel = None

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
