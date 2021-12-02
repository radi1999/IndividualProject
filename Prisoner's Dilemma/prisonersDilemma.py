import os
import itertools
import importlib
import numpy as np

STRATEGY_FOLDER = "Strategies"
RESULTS_FILE = "results.txt"

#        [[P, T], [S, R]]
points = [[1, 5], [0, 3]]
#        ["Defect", "Cooperate"] 
action = ["D", "C"] 

#------------------------------------------------------------------------------------------------------------------------------------

def getHistory(history, agent, turn):
    overallHistory = history[:,:turn].copy()
    if agent == 1:
        overallHistory = np.flip(overallHistory, 0)
    return overallHistory

#------------------------------------------------------------------------------------------------------------------------------------

def strategyGo(agentMove):
    if type(agentMove) is str:
        defects = "defect"
        return 0 if (agentMove in defects) else 1
    else:
        return int(bool(agentMove))

#------------------------------------------------------------------------------------------------------------------------------------

def runRound(pair):
    moduleA = importlib.import_module(STRATEGY_FOLDER + "." + pair[0])
    moduleB = importlib.import_module(STRATEGY_FOLDER + "." + pair[1])
    memoryA = None
    memoryB = None
    
    NUMBER_OF_ROUNDS = 20
    history = np.zeros((2, NUMBER_OF_ROUNDS), dtype=int)
    
    for turn in range(NUMBER_OF_ROUNDS):
        agentAmove, memoryA = moduleA.strategy(getHistory(history, 0, turn), memoryA)
        agentBmove, memoryB = moduleB.strategy(getHistory(history, 1, turn), memoryB)
        history[0, turn] = strategyGo(agentAmove)
        history[1, turn] = strategyGo(agentBmove)
    return history

#------------------------------------------------------------------------------------------------------------------------------------
    
def scoreTally(history):
    scoreA = 0
    scoreB = 0
    ROUND_LENGTH = history.shape[1]
    for turn in range(ROUND_LENGTH):
        agentAmove = history[0, turn]
        agentBmove = history[1, turn]
        scoreA += points[agentAmove][agentBmove]
        scoreB += points[agentBmove][agentAmove]
    return scoreA, scoreB

#------------------------------------------------------------------------------------------------------------------------------------
    
def outputScore(textFile, pair, roundHistory, scoresA, scoresB):
    textFile.write(pair[0] + " (P1)  VS.  " + pair[1] + " (P2)\n")
    for p in range(2):
        for t in range(roundHistory.shape[1]):
            agentMove = roundHistory[p, t]
            textFile.write(action[agentMove]+" ")
        textFile.write("\n")
    textFile.write("Final score for "+pair[0]+": " + str(scoresA) + "\n")
    textFile.write("Final score for "+pair[1]+":  "+ str(scoresB) + "\n")
    textFile.write("\n")

#------------------------------------------------------------------------------------------------------------------------------------
    
def pad(stri, leng):
    result = stri
    for i in range(len(stri),leng):
        result = result + " "
    return result

#------------------------------------------------------------------------------------------------------------------------------------
    
def roundRobinTournament(inFolder, outFile):
    print("\nStarting tournament... reading files from folder '" + os.path.abspath(inFolder) + "'")
    scoreBoard = {}
    STRATEGY_LIST = []
    for file in os.listdir(inFolder):
        if file.endswith(".py"):
            STRATEGY_LIST.append(file[:-3])
            
    for strategy in STRATEGY_LIST:
        scoreBoard[strategy] = 0
        
    textFile = open(outFile,"w+")
    for pair in itertools.combinations(STRATEGY_LIST, r=2):
        roundHistory = runRound(pair)
        scoresA, scoresB = scoreTally(roundHistory)
        outputScore(textFile, pair, roundHistory, scoresA, scoresB)
        scoreBoard[pair[0]] += scoresA
        scoreBoard[pair[1]] += scoresB
        
    scoresNumpy = np.zeros(len(scoreBoard))
    for i in range(len(STRATEGY_LIST)):
        scoresNumpy[i] = scoreBoard[STRATEGY_LIST[i]]
    rankings = np.argsort(scoresNumpy)

    textFile.write("\n\nTOTAL SCORES (" + str(int(len(roundHistory[0])/len(STRATEGY_LIST))) + " STINTS / "  + str(len(roundHistory[0])) + " ROUNDS EACH)\n")
    for position in range(len(STRATEGY_LIST)):
        i = rankings[-1-position]
        score = scoresNumpy[i]
        avgScore = score / (len(STRATEGY_LIST)-1)
        textFile.write("#" + str(position + 1) + ": " + pad(STRATEGY_LIST[i] + ":", 16) + ' %.0f'%score + ' (%.2f'%avgScore+" average)\n")
    
    textFile.write("\n")    
    textFile.flush()
    textFile.close()
    print("\nDone! \n\nResults file written to: '" + os.path.abspath(RESULTS_FILE) + "'\n")

#------------------------------------------------------------------------------------------------------------------------------------
    
roundRobinTournament(STRATEGY_FOLDER, RESULTS_FILE)