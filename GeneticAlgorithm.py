import random
from game import sim
import json

#Open Highscore Json File
try:
    with open("highscore.json") as file:
        data = json.load(file)
except:
    print("Error loading Json File")
    data = {
        "Score" : 0,
        "Moveset" : []
    }

#Game Parameters to Tweak
InitFallRatio = 5
FallRatioDelta = 1
JumpSpeed = 4
cap = 25

#Generational AI Algorithm Parameters
PopulationSize = 100
SuccessfulMutationRate = 0.05
FailedMutationRate = 0.5
Generations = 3

#Determines lenght of moveset or howlong birds will attempt to fly
moveSetLength = 500

#Sets Initial Variables including Fall Ratio and High Score
HighScoreTime = 0
FallRatio = InitFallRatio


class Agent:
    def __init__(self, LengthOfMoveSet=1000, moveset=0):
        '''Initialization of variables including creating moveset if needed'''
        if moveset == 0:
            self.moveset = []
            self.generateRandomMoveSet(LengthOfMoveSet)
        else:
            self.moveset = moveset

    def generateRandomMoveSet(self, length):
        '''Generates a randommoveset (Used on initialization if setup not loaded)'''
        for x in range(length):
            self.moveset.append(random.randint(0,InitFallRatio))

def GenerateInitialGeneration(popSize, movesetlength):
    '''Function to generate the initial moveset'''
    gen = [Agent(movesetlength) for x in range(popSize)]
    return gen

def SelectParents(Generation, prevHighScoreTime, iteration=0):
    '''Selects Two Parents of a Generation based on statistics from simulation'''
    #Runs Simulation from game.py
    simedAgents = sim(Generation, iteration, JumpSpeed, prevHighScoreTime, random.randint(0,10000))

    #Sorts and returns the two best agents
    def sortFunc(x):return(x[2])
    simedAgents.sort(key=sortFunc)

    #Tweek FallRatio Based on num of children hitting floor vs roof
    failSpot = [x[5] for x in simedAgents]
    fallRatioAdjustment = 0
    
    above = failSpot.count(0)
    below = failSpot.count(1)

    #If 2/3 of data above gap then decrease chance of jumping by fallratiodelta specificed earlier
    if(above > (above + below)*2/3):
        fallRatioAdjustment = FallRatioDelta
    elif(below > (above + below)*2/3):
        fallRatioAdjustment = -FallRatioDelta


    if(simedAgents[-2:][1][2] > prevHighScoreTime):
        #If improving set low mutation rate
        return simedAgents[-2:], SuccessfulMutationRate, fallRatioAdjustment
    else:
        #Increase Muatation Rate if not improivng
        return simedAgents[-2:], FailedMutationRate, fallRatioAdjustment
    

def CrossOver(parents, do):
    '''Function that provides crossover between two best parents'''
    if do:
        #Do Crossover
        #Specifies at what point in the genes crossover shoudl occur
        CrossOverPoint = random.randint(1, parents[0][3] -1)

        child1moveset = parents[0][4][:CrossOverPoint] + parents[1][4][CrossOverPoint:]
        child2moveset = parents[1][4][:CrossOverPoint] + parents[0][4][CrossOverPoint:]
    else:
        #Dont do crossover
        child1moveset = parents[0][4]
        child2moveset = parents[1][4]

    #Return the children movesets of parents w or w/o crossovr
    return child1moveset, child2moveset

def mutate(moveSet, mutateRate, usedMoves, fallRatio, mutateCap=moveSetLength):
    '''Function used to add randomness to geneset through mutation'''
    outputMoveSet = []

    #Append Everythign up intil moveset-mutatecap
    for x in moveSet[:usedMoves][:-mutateCap]:outputMoveSet.append(x)

    #Append Everything between usedmoves-mutatecap and mutate cap
    for x in moveSet[:usedMoves][-mutateCap:]:
        #If random number above mutate rate then append a new value.  This allows us to determine how often a client mutates
        if random.random() > mutateRate:
            outputMoveSet.append(x)
        else:
            outputMoveSet.append(random.randint(0, fallRatio))

    #Append everything after used moves
    for x in moveSet[usedMoves:]:outputMoveSet.append(x)

    #Return the mutated move set
    return outputMoveSet

    
#Generates the first generation w/ random movesets
CurrentGeneration = GenerateInitialGeneration(PopulationSize, moveSetLength)

#Loops through generations
for x in range(Generations):
    #Select the best parents from current generation
    CurrentGenerationParents = SelectParents(CurrentGeneration, HighScoreTime, iteration=x)

    #Increase or decrease the fall ratio based on the output of the current generations parents
    FallRatio += CurrentGenerationParents[2]

    #Update highscore if current generations parents reached one and reset fall ratio
    if CurrentGenerationParents[0][1][2] > HighScoreTime + 0.2:
        HighScoreTime = CurrentGenerationParents[0][1][2]
        FallRatio = InitFallRatio

    #Initiate crossover for children
    CurrentGenerationChildrenMoveSets = CrossOver(CurrentGenerationParents[0], False)

    #Initialize variables for mutation
    NextGenMoveSet = CurrentGenerationChildrenMoveSets[random.randint(0,1)]
    NextGenMutateRate = CurrentGenerationParents[1]
    PrevGenUsedMoves = CurrentGenerationParents[0][1][3]

    #Creates next generation
    CurrentGeneration = [Agent(moveset=mutate(NextGenMoveSet, NextGenMutateRate, PrevGenUsedMoves, FallRatio, cap)) for x in range(PopulationSize)]

#Check if the score recorded during simulation is better than highscore recorded and if so record new highscore
if(int(data["Score"]) < HighScoreTime):
    #Set Output Data
    OutData = {
        "Score": HighScoreTime,
        "Moveset" : NextGenMoveSet
    }
    print("New All Time High Score")

    #Output Data to json file
    o = json.dumps(OutData)
    with open("highscore.json", "w") as outfile:
        outfile.write(o)


