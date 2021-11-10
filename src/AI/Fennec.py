import numpy as np
import random
import math
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

    ###########################################
    ############## and Variables ##############
    ###########################################

    # 40 weights of the hidden layer
    # bias0, weightA0, weightB0, weightC0, weightD0, ..., bias1, weightA1, weightB1, weightC1, ...,
    # bias7, weightA7, weightB7, weightC7, weightD7, ... (where ABCDEFGH are inputs)
    # assigned random value from -1.0 to 1.0 rounded to 1 decimal place
    hidden_weights = []
    for i in range(72):
        hidden_weights.append(round(random.uniform(-1.0, 1.0), 1))

    # 9 weights in the outer layer; 1 for bias, eight for the outpuer of the eight hidden nodes
    # outer_weights[0] = bias, the rest are for the nodes
    outer_weights = []
    for i in range(9):
        outer_weights.append(round(random.uniform(-1.0, 1.0), 1))

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
    # Description: Uses ANN to examine the utility of a state
    #   and returns a rating from 0 to 1 based on how good it
    #   thinks the state is. 0 is the lowest, 1 is the highest
    #
    # Parameters:
    #   state - the state to be examined
    #
    # Return: the score of the gamestate (0.0 is lowest, 1.0 is highest)
    ##
    def utility(self, state):
        inputs = self.getInputs(state)
        return self.output_method(inputs)

    ##
    # getInputs
    # Description: based off of oldUtility, gets inputs based on the
    # state of the game for the ANN to use in it's function
    ##
    def getInputs(self, state):
        # Initialize Inputs
        foodInput = 0.0
        workerInput = 0.0
        haveDroneInput = 0.0
        haveSoldierInput = 0.0
        queenAnthillinput = 0.0
        addFoodInput = 0.0
        droneDistanceInput = 0.0
        soldierDistanceInput = 0.0

        myInv = getCurrPlayerInventory(state)
        enemInv = getEnemyInv(self, state)

        # inputs for the ANN based off of a state
        #   Note: All inputs are between 0.0 and 1.0

        # more food, bigger input
        foodInput = (1.0 / 11.0) * myInv.foodCount

        # If we have one or two workers, give it some input
        if (len(getAntList(state, state.whoseTurn, (WORKER,))) <= 2):
            workerInput = 0.5 * len(getAntList(state, state.whoseTurn, (WORKER,)))
        else:
            workerInput = 0.0

        # If we have a drone, feed input
        if (len(getAntList(state, state.whoseTurn, (DRONE,))) == 1):
            haveDroneInput = 1.0
        else:
            haveDroneInput = 0.0

        # 1.0 if we have soldier, 0.0 if not
        if (len(getAntList(state, state.whoseTurn, (SOLDIER,))) == 1):
            haveSoldierInput = 1.0
        else:
            haveSoldierInput = 0.0

        for ant in myInv.ants:

            # Queen behavior (keep off anthill)
            if (ant.type == QUEEN):
                if (myInv.getAnthill().coords == ant.coords):
                    queenAnthillInput = 0.0
                else:
                    queenAnthillInput = 1.0

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
                if(stepsToAddFood != 0):
                    addFoodInput = .99 / stepsToAddFood
                else:
                    addFoodInput = 1.0

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

                if(shortestPathToEnemWorker != 0):
                    droneDistanceInput = .99 / shortestPathToEnemWorker
                else:
                    droneDistanceInput = 1.0

            # Soldier behavior
            if (ant.type == SOLDIER):
                shortestPathToEnemQueen = 100  # ie infinity
                for enemAnt in enemInv.ants:
                    if (enemAnt.type == QUEEN):
                        potentialSteps = stepsToReach(state, ant.coords, enemAnt.coords)
                        if (potentialSteps < shortestPathToEnemQueen):
                            shortestPathToEnemQueen = potentialSteps

                if(shortestPathToEnemQueen != 0):
                    soldierDistanceInput = .99 / shortestPathToEnemQueen
                else:
                    soldierDistanceInput = 1.0

        inputs = np.array([foodInput, workerInput, haveDroneInput,
                           haveSoldierInput, queenAnthillinput, addFoodInput,
                           droneDistanceInput, soldierDistanceInput])
        return inputs

    ##
    # oldUtility
    # Description: Examines the gamestate and returns a rating from 0 to 1
    #   based on how good it thinks the state is. 0 is lowest, 1 is highest
    #
    # Parameters:
    #   state - the state to be examined
    #
    # Return: the score the the gamestate (0.0 is lowest, 1.0 is highest)
    ##
    def oldUtility(self, state):

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
        eval = self.oldUtility(state)
        aNNeval = self.utility(state)
        inputs = self.getInputs(state)
        print(self.backprop(aNNeval, eval, inputs))
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

    ###########################################
    ############## ANN Functions ##############
    ###########################################

    # sigmoid function
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))


    # goes through the hidden weights multiplying the input by the weights
    # uses counter as an incrementer to go through every (where ABCDEFGH are inputs)
    # 9 weights (bias, weightA, weightB, weightC, weightD, ...) then sigmoid and
    # repeats 8 times 8*9 = 72
    # then uses these values to multiply with the outer_weights and then sigmoid
    # the sum to get the output of the network
    def get_input_sum(self, input_array):
        counter = 0
        before_sigmoid = []
        for i in range(8):
            sum = (self.hidden_weights[counter] + \
                   (self.hidden_weights[counter + 1] * input_array[0]) + \
                   (self.hidden_weights[counter + 2] * input_array[1]) + \
                   (self.hidden_weights[counter + 3] * input_array[2]) + \
                   (self.hidden_weights[counter + 4] * input_array[2]) + \
                   (self.hidden_weights[counter + 5] * input_array[2]) + \
                   (self.hidden_weights[counter + 6] * input_array[2]) + \
                   (self.hidden_weights[counter + 7] * input_array[2]) + \
                   (self.hidden_weights[counter + 8] * input_array[3]))
            before_sigmoid.append(sum)
            counter = counter + 5

        return before_sigmoid


    # Utilizes get_input_sum helper to apply the sum of inputs*weight
    # to then apply them to the sigmoid function
    def get_hidden_outputs(self, input_array):
        before_sigmoid = self.get_input_sum(input_array)
        for_output_layer = []
        for i in range(len(before_sigmoid)):
            for_output_layer.append(self.sigmoid(before_sigmoid[i]))

        return for_output_layer


    # Utilizes get_hidden_outputs to properly calculate the inputs for the output method node.
    #   Note: Bias is assigned to the outer_sum variable and then other inputs and weights are
    #         calculated before feeding into the sigmoid function
    def output_method(self, input_array):
        for_output_layer = self.get_hidden_outputs(input_array)
        outer_sum = self.outer_weights[0]
        for i in range(len(for_output_layer)):
            outer_sum = outer_sum + (for_output_layer[i] * self.outer_weights[i + 1])

        return self.sigmoid(outer_sum)


    # val = random int to select array of values from all_inputs,
    # as well as corresponding expected_outputs
    def backprop(self, outputOfUtil, targetOutput, input_array):
        alpha = 0.75
        # Step 2 in slides
        a = outputOfUtil
        # Step 3 in slides
        error_output_node = targetOutput - a
        # Step 4 in slides
        delta_output_node = error_output_node * a * (1 - a)
        # Step 5 in slides
        hidden_errors = []
        for i in range(1, len(self.outer_weights)):
            hidden_errors.append(self.outer_weights[i] * delta_output_node)
        # Step 6 in slides
        hidden_deltas = []
        hidden_outputs = self.get_hidden_outputs(input_array)
        for i in range(len(hidden_errors)):
            hidden_deltas.append(hidden_errors[i] * hidden_outputs[i] * (1 - hidden_outputs[i]))
        # Step 7 in slides
        # change the outer layer weights
        # change bias differently with x as 1 rather than x as hidden_outputs[i-1]
        for i in range(len(self.outer_weights)):
            if (i == 0):
                self.outer_weights[i] = self.outer_weights[i] + (alpha * delta_output_node)
            else:
                self.outer_weights[i] = self.outer_weights[i] + \
                                   (alpha * delta_output_node * hidden_outputs[i - 1])

        for i in range(len(self.hidden_weights)):
            j = 0
            if (i < 9):
                j = 0
            elif (i < 18):
                j = 1
            elif (i < 27):
                j = 2
            elif (i < 36):
                j = 3
            elif (i < 45):
                j = 4
            elif (i < 54):
                j = 5
            elif (i < 63):
                j = 6
            else:
                j = 7
            if ((i % 9) == 0):
                self.hidden_weights[i] = self.hidden_weights[i] + (alpha * hidden_deltas[j])
            else:
                self.hidden_weights[i] = self.hidden_weights[i] + \
                                    (alpha * hidden_deltas[j] * input_array[(i % 9) - 1])

        return error_output_node