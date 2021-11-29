from typing import Annotated
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
    # bias11, weightA12, weightB12, weightC12, weightD12, ... (where ABCDEFGHIJKLM are inputs)
    # assigned random value from -1.0 to 1.0 rounded to 1 decimal place
    hidden_weights = []
    for i in range(210):
        randNumber = 0
        while (abs(randNumber) < 0.2):
            randNumber = round(random.uniform(0, 1.0), 1)

        hidden_weights.append(randNumber)

    # 14 weights in the outer layer; 1 for bias, 13 for the outer of the 13 hidden nodes
    # outer_weights[0] = bias, the rest are for the nodes
    outer_weights = []
    for i in range(15):
        randNumber = 0
        while (abs(randNumber) < 0.2):
            randNumber = round(random.uniform(0, 1.0), 1)

        outer_weights.append(randNumber)

    # whether we are currently testing or not
    testing = False
    # list of gamestates throughout the game
    gameStateList = []
    # hard coded weights calculated after training
    hard_hidden_weights = [0.8814726582213236, 0.5048275937225255, 0.741461890194539,
                           1.0044521497013088, 0.17306891746010997, 0.5213723880719433, 0.1773406407893261,
                           0.6027539907608496, 0.20564664661341509, 0.8013661773308401, 0.31009807783777626,
                           0.13433439421397125, 0.5089598272633751, 0.6309272174396662, 0.2706492530712083,
                           -0.11590662059362346, 0.5296008991430228, 0.7247402552735674, 0.4286330770689991,
                           0.5464954311239084, 0.5105005659022348, 0.6481854632947899, 1.0039284906610324,
                           0.8301116352872511, 0.7252480730869024, 0.41736910077742384, 0.05404501493206474,
                           0.6900858356450723, 0.6852057610635336, 0.36967402047926884, -1.2291690226116243,
                           0.7791146831283716, 0.2260145726006155, -0.11499971051570959, 0.032050707931090855,
                           0.03367010759195624, 0.4864941370427583, 0.1995673893580118, 0.49221317409755155,
                           0.392530632949519, 0.5808911882029574, 0.6341879636528236, 1.3221459278115402,
                           0.15801209458023094, -3.2601620116063623, -0.5828535249039216, 0.7895545486297846,
                           0.08733215536079718, 1.2251318756783962, 0.9674044544673864, 0.5343828788482081,
                           0.40807152211874803, 0.5901072570949701, 0.3504991285461305, 0.5591746649595063,
                           0.6643417149648871, 0.14396553099426676, 0.7642890312888354, 0.11495043666200436,
                           -0.7052758770136538, 0.4590128125108257, 0.6109501766794861, 0.4253660732704325,
                           0.27465834094169206, 0.9790100545988231, 0.8868251332769232, 1.0154027810049737,
                           0.49782113211003554, 0.8922138854076619, 0.3960009744617355, 0.37948731567240307,
                           0.3265513686626693, 0.3904184120877566, 0.7322231557620669, 0.9240742082655998,
                           0.6821654679274929, 0.9010631944781742, 0.14244134256422356, 0.40670910770966257,
                           0.273077153004603, 0.8317795579383306, 0.872961549623527, 0.8022163893973077,
                           0.20312066190911396, 0.20191715229286875, 0.5009877682832792, 0.5304636214863563,
                           0.4060334849298752, 0.9301219099805198, 0.17293332025758792, 0.5695240297750731,
                           0.612028692301371, 0.9315511844572918, 0.37611527439662523, 0.7845076276191306,
                           0.8939868996880059, 0.7162476379878034, 0.6984252170722952, 0.8951029314641777,
                           0.19613691731033367, 0.3884065664295943, 0.7355117708687239, 0.5903546871498967,
                           0.8386852879785638, 0.6276512113256835, 1.04870726610721, 0.5137023019740364,
                           0.6188906159983997, 0.47476427261302306, 0.7698496614913192, 0.4796165582231673,
                           0.6109717016853872, 0.4989794728414087, 0.8922884423143643, 0.7959408469677433,
                           0.17604043938182978, 0.6148875966396812, 0.282967459064698, 0.8228082707093184,
                           0.8366652713162099, -0.04900178293303658, 0.9609642649611643, 0.8869200583181673,
                           0.6433474137228494, 0.293189813270177, 0.4004659321363064, 0.7621619946066489,
                           0.6025057915618217, 0.6116997083719062, 0.8089190387370967, 0.5093380377595809,
                           0.6748099422607144, 0.9330825974294377, 0.5615837911809106, 0.6615876249510381,
                           0.5561133058721653, 0.6150186769839643, 0.5241646933508889, 0.1686815397971275,
                           0.7799235205549039, 0.8847228998501919, 0.813856848672958, 0.797605776690649,
                           0.29333030053729325, 0.1949916170368719, 0.793011851957592, 0.7294135836778021,
                           0.7924751183232703, 0.9313324412709297, 0.7268429210746181, 0.17489889759999094,
                           0.8916479417770998, 0.189622410272984, 0.41324118463257276, 0.9044588760468143,
                           0.7038972171134287, 0.19371040802673775, 0.39903519319720226, 0.4982520520851199,
                           0.8020653500120075, 0.5972288183659323, 0.7856848103869052, 1.0043128789752453,
                           0.28644451779070457, 0.9843345542613751, 0.5655885688524325, 0.6009302887351782,
                           0.6335194895612916, 0.402612000039861, 0.3610486720369985, 0.21695974425071896,
                           0.6793770704549851, 0.8024796472590524, 0.6045968979799136, 0.3014851593163599,
                           0.6015225937488923, 0.42043654741278147, 0.6087189737901786, 0.5210912779097483,
                           0.8670628645427142, 0.3307810766377805, 1.0093403563836032, 0.7632599829836737,
                           0.9931723717678015, 0.1500436233971998, 0.4453389411683724, 0.9877323311815921,
                           0.5001434271650164, 0.3965947221580284, 0.29917146425253116, 0.9922165705620598,
                           0.9525462393463971, 0.1999648030163123, 0.1573329084861001, 0.7999997884432666,
                           0.36209031256096225, 0.5947242701766116, 0.4351644825742475, 0.8175708469012833,
                           0.8940348826391259, 0.13463103228908013, 0.4699130023426955, 0.20121035847152086,
                           0.9036889461809626, 0.9026743350659769, 0.7086945515074407, 0.5215139907290325,
                           0.21979448455617687, 0.6232476002313566, 0.659299860710683]
    hard_outer_weights = [-1.365227968559888, 0.03523771005925551, 0.5508178964056902,
                          3.954997561404325, 1.62614160688552, -0.21092849314531398, 0.03906776393750624,
                          -0.3541229366785171, -0.44260545680026825, 0.22403939380746862, -0.320038426836023,
                          0.0975733472023053, -0.0631901059810313, -0.13872664315855346, 0.17027198999506835]

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

        # add all the possible game states to the whole gamestate list
        self.gameStateList.extend(states)

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
    # Description: based off of lUtility, gets inputs based on the
    # state of the game for the ANN to use in it's function
    ##
    def getInputs(self, state):
        # Initialize Inputs
        foodInput = 0.0
        workerInput = 0.0
        haveDroneInput = 0.0
        haveSoldierInput = 0.0
        queenAnthillInput = 0.0
        addFoodInput = 0.0
        droneDistanceWorkerInput = 0.0
        soldierDistanceQueenInput = 0.0
        droneDistanceQueenInput = 0.0
        soldierDistanceWorkerInput = 0.0
        enemyWorkerListInput = 0.0
        enemyAnthillInput = 0.0
        queenHealthInput = 0.0
        enemyAttackListInput = 0.0

        myInv = getCurrPlayerInventory(state)
        enemInv = getEnemyInv(self, state)

        # inputs for the ANN based off of a state
        #   Note: All inputs are between 0.0 and 1.0

        # more food, bigger input
        if (abs(myInv.foodCount - enemInv.foodCount) < 12):
            foodInput = (0.0909 * (myInv.foodCount - enemInv.foodCount))

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
                        # potentialSteps = stepsToReach(state, ant.coords, food.coords)
                        potentialSteps = approxDist(ant.coords, food.coords)
                        if (potentialSteps < stepsTilFood):
                            stepsTilFood = potentialSteps
                            foodSource = food

                    # calculate the closest structure from foodSource coords
                    constrs = []
                    constrs.append(myInv.getAnthill())
                    constrs.append(myInv.getTunnels()[0])
                    for constr in constrs:
                        # potentialSteps = stepsToReach(state, foodSource.coords, constr.coords)
                        potentialSteps = approxDist(foodSource.coords, constr.coords)
                        if (potentialSteps < stepsTilConstr):
                            stepsTilConstr = potentialSteps


                else:
                    stepsTilFood = 0
                    stepsTilConstr = 100  # ie infinity
                    # calculate the closest structure from ant coords
                    constrs = []
                    constrs.append(myInv.getTunnels()[0])
                    constrs.append(myInv.getAnthill())
                    stepsTilConstr = approxDist(ant.coords, constrs[0].coords)
                    # for constr in constrs:
                    #     # potentialSteps = stepsToReach(state, ant.coords, constr.coords)
                    #     potentialSteps = approxDist(ant.coords, constr.coords)
                    #     if (potentialSteps < stepsTilConstr):
                    #         stepsTilConstr = potentialSteps

                stepsToAddFood = stepsTilFood + stepsTilConstr
                if (stepsToAddFood == 0):
                    addFoodInput = 1.0
                else:
                    addFoodInput = .95 / stepsToAddFood

                    # Drone behavior
            if (ant.type == DRONE):
                shortestPathToEnemWorker = 0
                if not (len(getAntList(state, 1 - state.whoseTurn, (WORKER,))) == 0):
                    shortestPathToEnemWorker = 100  # ie infinity
                    for enemAnt in enemInv.ants:
                        if (enemAnt.type == WORKER):
                            # potentialSteps = stepsToReach(state, ant.coords, enemAnt.coords)
                            potentialSteps = approxDist(ant.coords, enemAnt.coords)
                            if (potentialSteps < shortestPathToEnemWorker):
                                shortestPathToEnemWorker = potentialSteps

                if (shortestPathToEnemWorker != 0):
                    droneDistanceWorkerInput = .99 / shortestPathToEnemWorker
                else:
                    droneDistanceWorkerInput = 1.0
                shortestPathToEnemQueen = 100  # ie infinity
                for enemAnt in enemInv.ants:
                    if (enemAnt.type == QUEEN):
                        # potentialSteps = stepsToReach(state, ant.coords, enemAnt.coords)
                        potentialSteps = approxDist(ant.coords, enemAnt.coords)
                        if (potentialSteps < shortestPathToEnemQueen):
                            shortestPathToEnemQueen = potentialSteps

                if (shortestPathToEnemQueen != 0):
                    droneDistanceQueenInput = .99 / shortestPathToEnemQueen
                else:
                    droneDistanceQueenInput = 1.0

            # Soldier behavior
            if (ant.type == SOLDIER):
                shortestPathToEnemQueen = 100  # ie infinity
                for enemAnt in enemInv.ants:
                    if (enemAnt.type == QUEEN):
                        # potentialSteps = stepsToReach(state, ant.coords, enemAnt.coords)
                        potentialSteps = approxDist(ant.coords, enemAnt.coords)
                        if (potentialSteps < shortestPathToEnemQueen):
                            shortestPathToEnemQueen = potentialSteps

                if (shortestPathToEnemQueen != 0):
                    soldierDistanceQueenInput = .99 / shortestPathToEnemQueen
                else:
                    soldierDistanceQueenInput = 1.0
                shortestPathToEnemWorker = 0
                if not (len(getAntList(state, 1 - state.whoseTurn, (WORKER,))) == 0):
                    shortestPathToEnemWorker = 100  # ie infinity
                    for enemAnt in enemInv.ants:
                        if (enemAnt.type == WORKER):
                            # potentialSteps = stepsToReach(state, ant.coords, enemAnt.coords)
                            potentialSteps = approxDist(ant.coords, enemAnt.coords)
                            if (potentialSteps < shortestPathToEnemWorker):
                                shortestPathToEnemWorker = potentialSteps

                if (shortestPathToEnemWorker != 0):
                    soldierDistanceWorkerInput = .99 / shortestPathToEnemWorker
                else:
                    soldierDistanceWorkerInput = 1.0

        enemyWorkerList = (getAntList(state, 1 - state.whoseTurn, (WORKER,)))
        if (len(enemyWorkerList) > 0):
            enemyWorkerListInput = 0.99 - (0.33 * len(getAntList(state, 1 - state.whoseTurn, (WORKER,))))
        else:
            enemyWorkerListInput = 1.0

        if (enemInv.getAnthill()):
            enemyAnthillInput = 0.99 - (0.33 * enemInv.getAnthill().captureHealth)
        else:
            enemyAnthillInput = 1.0

        if (enemInv.getQueen()):
            queenHealthInput = 0.99 - (0.125 * enemInv.getAnthill().captureHealth)
        else:
            queenHealthInput = 1.0

        enemyAttackList = getAntList(state, 1 - state.whoseTurn, (DRONE, SOLDIER, R_SOLDIER,))
        if (len(enemyAttackList) < 10):
            enemyAttackListInput = (0.099 * len(enemyAttackList))
        else:
            enemyAttackListInput = 1.0

        inputs = np.array([foodInput, workerInput, haveDroneInput,
                           haveSoldierInput, queenAnthillInput, addFoodInput,
                           droneDistanceWorkerInput, soldierDistanceQueenInput,
                           droneDistanceQueenInput, soldierDistanceWorkerInput,
                           enemyWorkerListInput, enemyAnthillInput, queenHealthInput,
                           enemyAttackListInput])
        return inputs

    ##
    # lUtility
    # Description: Examines the gamestate and returns a rating from 0 to 1
    #   based on how good it thinks the state is. 0 is lowest, 1 is highest
    #
    # Parameters:
    #   state - the state to be examined
    #
    # Return: the score the the gamestate (0.0 is lowest, 1.0 is highest)
    ##
    def lUtility(self, currentState):

        # Helper variables including the score counter, player ID's, lists of ants and structs
        score = 0.5
        myID = currentState.whoseTurn
        enemyID = 1 - myID
        myInv = currentState.inventories[myID]
        enemyInv = currentState.inventories[enemyID]
        myAntList = getAntList(currentState, myID, (WORKER, DRONE, R_SOLDIER, SOLDIER,))
        enemyAntList = getAntList(currentState, enemyID, (WORKER, DRONE, R_SOLDIER, SOLDIER,))
        myAttackList = getAntList(currentState, myID, (DRONE, R_SOLDIER, SOLDIER,))
        enemyAttackList = getAntList(currentState, enemyID, (SOLDIER, DRONE, R_SOLDIER, QUEEN,))
        myWorkerList = getAntList(currentState, myID, (WORKER,))
        enemyWorkerList = getAntList(currentState, enemyID, (WORKER,))
        myDroneList = getAntList(currentState, myID, (DRONE,))
        enemyDroneList = getAntList(currentState, enemyID, (DRONE,))
        mySoldierList = getAntList(currentState, myID, (SOLDIER,))
        enemySoldierList = getAntList(currentState, enemyID, (SOLDIER,))
        foodList = getConstrList(currentState, None, (FOOD,))
        myTunnel = getConstrList(currentState, myID, (TUNNEL,))[0]

        # calculates the total utility with helper methods
        score = self.foodUtility(score, myInv, enemyInv, myAntList,
                                 enemyAntList, enemyWorkerList)
        score = self.queenUtility(score, myInv, myTunnel, foodList,
                                  enemyDroneList, enemySoldierList)
        score = self.constrUtility(score, myInv, enemyInv)
        score = self.antlistUtility(score, myAttackList, myWorkerList,
                                    enemyAttackList, myAntList, enemyAntList, mySoldierList, enemyWorkerList)
        score = self.distanceUtility(currentState, score, myAttackList,
                                     enemyInv, enemyWorkerList, myWorkerList, foodList, myTunnel, myID, myInv)
        score = self.incentiveUtility(score, myInv, myDroneList,
                                      myAttackList)

        return score

        ##

    # foodUtility
    # Description: Returns the utlity of the game state based on foodCount
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   Helper variables including the score counter, player ID's, lists of ants and structs from
    #   lines 162-178
    # Returns:
    #   a float between 0 and 1 that represents the likelihood of winning in the given gamestate
    #   based on foodCount
    ##
    def foodUtility(self, score, myInv, enemyInv, myAntList,
                    enemyAntList, enemyWorkerList):

        # food utility
        # decrements utility if amount of food and amount of ants is less than the enemy
        if (myInv.foodCount <= enemyInv.foodCount and len(myAntList) < len(enemyAntList)):
            diff2 = score
            score = score - (diff2 * 0.15)
        # increases the utility of food count is greater than the enemy and
        # number of ants is greater by at least 1
        if (myInv.foodCount >= enemyInv.foodCount):
            if (len(myAntList) > 1 + len(enemyAntList)):
                diff = 1.0 - score
                score = score + (diff * 0.2)

        # if the enemyAntList is down to 1 or 0 significantly increases the utility
        if (len(enemyAntList) < 1):
            diff = 1.0 - score
            score = score + (diff * 0.75)
        # also checks the number of ants the enemy has and decrements based on specific
        # scenarios
        elif (len(enemyAntList) < 1 and enemyInv.foodCount < 2):
            diff = 1.0 - score
            score = score + (diff * 0.6)
        elif (len(enemyWorkerList) < 2 and enemyInv.foodCount < 1):
            diff = 1.0 - score
            score = score + (diff * 0.8)

        return score

    ##
    # queenUtility
    # Description: Returns the utlity of the game state based on queen location and proximity to
    #             enemies
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   Helper variables including the score counter, player ID's, lists of ants and structs from
    #   lines 162-178
    # Returns:
    #   a float between 0 and 1 that represents the likelihood of winning in the given gamestate
    #   based on queen location and proximity to enemies
    ##
    def queenUtility(self, score, myInv, myTunnel, foodList,
                     enemyDroneList, enemySoldierList):
        # queen utility
        # don't want the queen to be on the anthill, tunnel, or any of the food
        # so decrease utility if it is on these buildings/structs
        if (myInv.getQueen() is not None and myInv.getAnthill() is not None):
            if (myInv.getQueen().coords == myInv.getAnthill().coords):
                diff2 = score
                score = score - (diff2 * 0.3)
            if (myInv.getQueen().coords == myTunnel.coords):
                diff2 = score
                score = score - (diff2 * 0.25)
            for f in foodList:
                if (myInv.getQueen().coords == f.coords):
                    diff2 = score
                    score = score - (diff2 * 0.1)

            # want the queen to be adjacent to the anthill but not on it
            if (myInv.getQueen().coords != myInv.getAnthill().coords
                    and approxDist(myInv.getQueen().coords, myInv.getAnthill().coords) == 1):
                diff = 1 - score
                score = score + (diff * 0.1)

        return score

    ##
    # constrUtility
    # Description: Returns the utlity of the game state based on health of constructs
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   Helper variables including the score counter, player ID's, lists of ants and structs from
    #   lines 162-178
    # Returns:
    #   a float between 0 and 1 that represents the likelihood of winning in the given gamestate
    #   based on health of constructs
    ##
    def constrUtility(self, score, myInv, enemyInv):
        # construct health utility
        # decreases and increases in utility based on which player's anthill/queen's health
        # is going down. Also goes down more and more as more health goes down
        anthillHealth = myInv.getAnthill().captureHealth
        diff2 = score
        score = score - (diff2 * (1 - (anthillHealth * 0.25)))

        enemyAnthillHealth = enemyInv.getAnthill().captureHealth
        diff = 1 - score
        score = score + (diff * (1 - (enemyAnthillHealth * 0.2)))

        if (myInv.getQueen() != None):
            queenHealth = myInv.getQueen().health
            diff2 = score
            score = score - (diff2 * (1 - (queenHealth * 0.1)))
        else:
            score = 0.01

        if (enemyInv.getQueen() != None):
            enemyQueenHealth = enemyInv.getQueen().health
            diff = 1 - score
            score = score + (diff * (1 - (enemyQueenHealth * 0.1)))
        else:
            score = 0.99
        return score

    ##
    # antlistUtility
    # Description: Returns the utlity of the game state based on length and type of antlist
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   Helper variables including the score counter, player ID's, lists of ants and structs from
    #   lines 162-178
    # Returns:
    #   a float between 0 and 1 that represents the likelihood of winning in the given gamestate
    #   based on length and type of antlist
    ##
    def antlistUtility(self, score, myAttackList, myWorkerList,
                       enemyAttackList, myAntList, enemyAntList, mySoldierList, enemyWorkerList):
        # antList utility
        # decreases utility if the player doesn't have an attacking ant (non-worker and non-queen)
        if (len(myAttackList) < 2):
            diff2 = score
            score = score - (diff2 * 0.08)
        elif (len(myAttackList) < 1):
            diff2 = score
            score = score - (diff2 * 0.13)

        # makes the last worker run away from the enemy's attacking ants
        if (len(myWorkerList) == 1):
            for e in enemyAttackList:
                if (approxDist(e.coords, myWorkerList[0].coords) <= 3):
                    diff2 = score
                    score = score - (diff2 * 0.55)
                    break

        # also makes the workers run away from the enemy's attacking ants if they are within
        # 3 spaces and the player has less ants in general
        if (len(myAntList) < len(enemyAntList)):
            for e in enemyAttackList:
                for w in myWorkerList:
                    if (approxDist(e.coords, w.coords) <= 3):
                        diff2 = score
                        score = score - (diff2 * ((3 - approxDist(e.coords, w.coords)) * 0.05))

        # incentivizes the player to create a soldier by increasing utility if there is a soldier
        if (len(mySoldierList) > 0):
            diff = 1 - score
            score = score + (diff * 0.19)

        # also incentivizes the player to create attacking drones if the enemy has more attacking
        # ants
        if (len(myAttackList) > 0 and len(enemyAttackList) < 4):
            diff = 1 - score
            score = score + (diff * 0.18)

        # decrements the utility based on number of enemy attacking ants
        diff2 = score
        score = score - (diff2 * (len(enemyAttackList) * 0.12))

        if (len(enemyWorkerList) == 0):
            diff = 1 - score
            score = score + (diff * 0.45)
        return score

    ##
    # distanceUtility
    # Description: Returns the utlity of the game state based on distance from ants to useful
    # enemy constructs or enemy ants
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   Helper variables including the score counter, player ID's, lists of ants and structs from
    #   lines 162-178
    # Returns:
    #   a float between 0 and 1 that represents the likelihood of winning in the given gamestate
    #   based on distance from ants to useful enemy constructs or enemy ants
    ##
    def distanceUtility(self, currentState, score, myAttackList,
                        enemyInv, enemyWorkerList, myWorkerList, foodList, myTunnel, myID, myInv):
        # distance utility
        # calculates total distance (steps) from enemy anthill to incentivize player's
        # attacking ants to march towards it. Order is enemy worker, then enemy anthill
        # and while going for the anthill probably runs into the enemy queen as well
        totalSteps3 = 0
        avgDistEnemyAnthill = 0
        for m in myAttackList:
            totalSteps3 = totalSteps3 + approxDist(m.coords,
                                                   enemyInv.getAnthill().coords)

        if (len(myAttackList) != 0):
            avgDistEnemyAnthill = totalSteps3 / len(myAttackList)
        else:
            avgDistEnemyAnthill = -1

        if (avgDistEnemyAnthill != -1):
            diff = 1.0 - score
            if (avgDistEnemyAnthill == 0):
                score = score + (diff * 0.35)
            else:
                score = score + (diff * ((0.2 / avgDistEnemyAnthill)))

        # calculates distance to enemy worker and increments utility the closer it gets
        totalSteps4 = 0
        diff = 1 - score
        if (len(enemyWorkerList) > 0):
            for m in myAttackList:
                totalSteps4 = totalSteps4 + approxDist(m.coords,
                                                       enemyWorkerList[0].coords)
                if (totalSteps4 == 0):
                    score = score + (diff * 0.35)
                else:
                    diff = 1 - score
                    score = score + (diff * ((0.24 / totalSteps4)))

        # for loop checks all workers and sees whether they are carrying food or not
        # it increments utility as the non-carrying worker gets closer to the food
        # it increments utility once the non-carrying worker becomes a carrying worker
        # it the increments utility once the carrying worker delives the food to the
        # tunnel
        # calculates the distance in a similar way to previous calculations to anthill
        # also calculates the closest food
        totalSteps = 0
        totalSteps2 = 0
        diff = 1 - score
        for worker in myWorkerList:
            if not (worker.carrying):
                shortestDist = 1000
                ind = 0
                c = 0
                foodListN = []
                if (myID == 1):
                    foodListN.append(foodList[0])
                    foodListN.append(foodList[1])
                else:
                    foodListN.append(foodList[2])
                    foodListN.append(foodList[3])
                for food in foodListN:
                    if (approxDist(worker.coords, food.coords) < shortestDist):
                        shortestDist = approxDist(worker.coords, food.coords)
                        ind = c
                    c = c + 1
                totalSteps = approxDist(worker.coords, foodListN[ind].coords)
                if (totalSteps == 0):
                    score = score + (diff * 0.05)
                else:
                    diff = 1 - score
                    score = score + (diff * ((0.035 / totalSteps)))
            else:
                diff = 1 - score
                score = score + (diff * 0.05)
                closer = approxDist(worker.coords, myTunnel.coords)
                totalSteps2 = closer
                if (totalSteps2 == 0):
                    score = score + (diff * 0.50)
                else:
                    diff = 1 - score
                    score = score + (diff * ((0.035 / totalSteps2)))
        return score

    ##
    # incentiveUtility
    # Description: Returns the utlity of the game state based on some extra incentives for
    # the AI system to function as wanted
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   Helper variables including the score counter, player ID's, lists of ants and structs from
    #   lines 162-178
    # Returns:
    #   a float between 0 and 1 that represents the likelihood of winning in the given gamestate
    #   based on some extra incentives for the AI to function as wanted
    ##
    def incentiveUtility(self, score, myInv, myDroneList, myAttackList):
        # incentive utility
        # increments utility to convince the carrying ant to drop of the food at the tunnel
        # rather than staying a carrying worker
        diff = 1 - score
        score = score + (diff * 0.09 * myInv.foodCount)

        # increments utility if the player decides to create a drone so the player should have
        # a soldier and a drone. this defeats both AI's very reliably
        if (len(myDroneList) > 0):
            diff = 1 - score
            score = score + (diff * 0.05)

        # increments utility based on how many attacking ants the player has
        diff = 1 - score
        score = score + (diff * 0.07 * (len(myAttackList)))
        return score

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
        eval = self.lUtility(state)
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
    # gathers all the gamestates at the end of each game and
    # does backprop here then sets the instance arrays to the new appropriate values
    #
    def registerWin(self, hasWon):
        # method templaste, not implemented
        if (self.testing):
            error = 0
            totalStates = len(self.gameStateList)
            random.shuffle(self.gameStateList)
            if (totalStates <= 2500):
                for i in self.gameStateList:
                    oldEval = self.lUtility(i)
                    annEval = self.utility(i)
                    inputs = self.getInputs(i)
                    indivError = self.backprop(annEval, oldEval, inputs)
                    error = (abs(error)) + abs(indivError)
            else:
                for i in range(2500):
                    oldEval = self.lUtility(self.gameStateList[i])
                    annEval = self.utility(self.gameStateList[i])
                    inputs = self.getInputs(self.gameStateList[i])
                    indivError = self.backprop(annEval, oldEval, inputs)
                    error = abs(error) + abs(indivError)

            avgErr = error / totalStates
            print(avgErr)
            if (avgErr < 0.0025):
                print("Valid under 0.0025")
                print("Avg. Err = {}".format(avgErr))
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
    # repeats 12 times 12*9 = 108
    # then uses these values to multiply with the outer_weights and then sigmoid
    # the sum to get the output of the network
    def get_input_sum(self, input_array):
        weights = self.hidden_weights
        if (not self.testing):
            weights = self.hard_hidden_weights
        counter = 0
        before_sigmoid = []
        for i in range(14):
            sum = (weights[counter] + \
                   (weights[counter + 1] * input_array[0]) + \
                   (weights[counter + 2] * input_array[1]) + \
                   (weights[counter + 3] * input_array[2]) + \
                   (weights[counter + 4] * input_array[3]) + \
                   (weights[counter + 5] * input_array[4]) + \
                   (weights[counter + 6] * input_array[5]) + \
                   (weights[counter + 7] * input_array[6]) + \
                   (weights[counter + 8] * input_array[7]) + \
                   (weights[counter + 9] * input_array[8]) + \
                   (weights[counter + 10] * input_array[9]) + \
                   (weights[counter + 11] * input_array[10]) + \
                   (weights[counter + 12] * input_array[11]) + \
                   (weights[counter + 13] * input_array[12]) + \
                   (weights[counter + 14] * input_array[13]))
            before_sigmoid.append(sum)
            counter = counter + 15

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
        weights = self.outer_weights
        if (not self.testing):
            weights = self.hard_outer_weights
        outer_sum = weights[0]
        for i in range(len(for_output_layer)):
            outer_sum = outer_sum + (for_output_layer[i] * weights[i + 1])

        return self.sigmoid(outer_sum)

    # val = random int to select array of values from all_inputs,
    # as well as corresponding expected_outputs
    def backprop(self, outputOfUtil, targetOutput, input_array):
        alpha = 0.30
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
            if (i < 15):
                j = 0
            elif (i < 30):
                j = 1
            elif (i < 45):
                j = 2
            elif (i < 60):
                j = 3
            elif (i < 75):
                j = 4
            elif (i < 90):
                j = 5
            elif (i < 105):
                j = 6
            elif (i < 120):
                j = 7
            elif (i < 135):
                j = 8
            elif (i < 150):
                j = 9
            elif (i < 165):
                j = 10
            elif (i < 180):
                j = 11
            elif (i < 195):
                j = 12
            else:
                j = 13

            if ((i % 15) == 0):
                self.hidden_weights[i] = self.hidden_weights[i] + (alpha * hidden_deltas[j])
            else:
                self.hidden_weights[i] = self.hidden_weights[i] + \
                                         (alpha * hidden_deltas[j] * input_array[(i % 15) - 1])

        return error_output_node